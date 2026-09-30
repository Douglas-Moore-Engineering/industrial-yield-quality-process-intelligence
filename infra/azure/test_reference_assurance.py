"""Simulated safety tests; these do not create cloud execution evidence."""
import copy
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import reference_assurance as assurance


class FakeContainer:
    def __init__(self, service, name, metadata):
        self.service, self.name, self.metadata = service, name, metadata
        self.data = None
        self.deleted = False
        self.restored = False

    def get_blob_client(self, name):
        assert name == 'probe.bin'
        return self

    def upload_blob(self, data, overwrite):
        assert overwrite is False
        self.data = data

    def download_blob(self):
        return SimpleNamespace(readall=lambda: b'corrupted' if self.restored and self.service.corrupt else self.data)

    def get_container_properties(self):
        return {'metadata': self.metadata if not self.service.foreign else {'purpose': 'other'}}

    def list_blobs(self):
        return [{'name': 'probe.bin'}] + ([{'name': 'foreign.bin'}] if self.service.extra else [])

    def delete_container(self):
        self.service.deleted_names.append(self.name)
        self.deleted = True

    def exists(self):
        return not self.deleted


class FakeService:
    def __init__(self, enabled=True, days=7, extra=False, foreign=False, corrupt=False, collision=False):
        self.enabled, self.days = enabled, days
        self.extra, self.foreign, self.corrupt, self.collision = extra, foreign, corrupt, collision
        self.created, self.deleted_names = [], []
        self.restore_calls = []

    def retention(self):
        return {'enabled': self.enabled, 'days': self.days}

    def create_container(self, name, metadata):
        if self.collision:
            raise RuntimeError('simulated ResourceExistsError')
        self.created.append(name)
        self.container = FakeContainer(self, name, metadata)
        return self.container

    def list_containers(self, name_starts_with, include_deleted):
        assert name_starts_with == self.container.name and include_deleted is True
        return [{'name': self.container.name, 'deleted': True, 'version': 'version-1'},
                {'name': self.container.name + '-different', 'deleted': True, 'version': 'unrelated'}]

    def undelete_container(self, deleted_container_name, deleted_container_version):
        self.restore_calls.append((deleted_container_name, deleted_container_version))
        self.container.deleted, self.container.restored = False, True
        return self.container


class RecoverySafetyTests(unittest.TestCase):
    def test_approval_and_retention_fail_before_creation(self):
        for approved, enabled, days in [(False, True, 7), (True, False, 7), (True, True, 1), (True, True, 90)]:
            with self.subTest(approved=approved, enabled=enabled, days=days):
                service = FakeService(enabled=enabled, days=days)
                with self.assertRaises(ValueError):
                    assurance.recover(service, service.retention, approve=approved)
                self.assertEqual(service.created, [])
                self.assertEqual(service.deleted_names, [])

    def test_restore_checks_exact_version_checksum_and_checkpoint(self):
        service, checkpoints = FakeService(), []
        result = assurance.recover(service, service.retention, approve=True, checkpoint=lambda e: checkpoints.append(copy.deepcopy(e)))
        self.assertEqual(result['status'], 'passed')
        self.assertEqual(result['expected_sha256'], result['restored_sha256'])
        self.assertEqual(service.restore_calls, [(result['container'], 'version-1')])
        self.assertEqual(service.deleted_names, service.created)
        self.assertRegex(result['container'], r'^iyqpis-recovery-[a-f0-9]{32}$')
        self.assertIn('delete_requested', [e['phase'] for e in checkpoints])
        self.assertFalse(result['production_rto_verified'])

    def test_foreign_contents_or_metadata_refuse_deletion(self):
        for values in ({'extra': True}, {'foreign': True}):
            service = FakeService(**values)
            with self.assertRaises(ValueError):
                assurance.recover(service, service.retention, approve=True)
            self.assertEqual(service.deleted_names, [])

    def test_existing_name_never_overwritten_or_deleted(self):
        service = FakeService(collision=True)
        with self.assertRaises(RuntimeError):
            assurance.recover(service, service.retention, approve=True)
        self.assertEqual(service.deleted_names, [])

    def test_changed_context_prevents_deletion(self):
        service = FakeService()
        def changed():
            raise ValueError('Wrong context')
        with self.assertRaises(ValueError):
            assurance.recover(service, service.retention, approve=True, before_delete=changed)
        self.assertEqual(service.deleted_names, [])

    def test_retention_removed_during_drill_prevents_deletion(self):
        service = FakeService()
        with self.assertRaises(ValueError):
            assurance.recover(service, service.retention, approve=True, before_delete=lambda: setattr(service, 'enabled', False))
        self.assertEqual(service.deleted_names, [])

    def test_corrupt_restoration_does_not_pass(self):
        service, evidence = FakeService(corrupt=True), {}
        with self.assertRaisesRegex(ValueError, 'checksum'):
            assurance.recover(service, service.retention, approve=True, evidence=evidence)
        self.assertNotEqual(evidence['status'], 'passed')
        self.assertEqual(evidence['deleted_container_version'], 'version-1')

    def test_missing_deleted_version_does_not_restore_other_container(self):
        service = FakeService()
        with patch.object(service, 'list_containers', return_value=[]):
            with self.assertRaisesRegex(ValueError, 'not visible'):
                assurance.recover(service, service.retention, approve=True, pause=lambda _: None)
        self.assertEqual(service.restore_calls, [])

    def test_public_or_mixed_dns_is_refused(self):
        for addresses in [('8.8.8.8',), ('10.80.0.4', '8.8.8.8')]:
            with patch.object(assurance.socket, 'getaddrinfo', return_value=[(None, None, None, None, (a, 443)) for a in addresses]):
                with self.assertRaises(ValueError):
                    assurance.private_dns('example.blob.core.windows.net')


class MonitoringSafetyTests(unittest.TestCase):
    context = {'subscriptionId': '11111111-1111-1111-1111-111111111111',
               'tenantId': '22222222-2222-2222-2222-222222222222', 'accountEmail': 'engineer@example.com'}

    def test_context_mismatch_is_refused(self):
        actual = {'id': self.context['subscriptionId'], 'tenantId': self.context['tenantId'], 'user': {'name': 'wrong@example.com'}}
        with patch.object(assurance, 'az', return_value=actual):
            with self.assertRaisesRegex(ValueError, 'Wrong Azure context'):
                assurance.verify_context(self.context)

    def test_diagnostic_is_explicit_and_query_injection_is_refused(self):
        event = assurance.diagnostic('a' * 32)
        self.assertTrue(event['diagnostic'])
        self.assertEqual(event['scope'], 'reference_diagnostic')
        with self.assertRaises(ValueError):
            assurance.diagnostic("' | union *")

    def test_ingestion_is_not_notification_delivery(self):
        root = '/subscriptions/' + self.context['subscriptionId'] + '/resourceGroups/' + assurance.RESOURCE_GROUP
        rule = {'properties': {'enabled': True,
                'scopes': [root + '/providers/Microsoft.OperationalInsights/workspaces/' + assurance.WORKSPACE],
                'actions': {'actionGroups': [root + '/providers/Microsoft.Insights/actionGroups/' + assurance.ACTION_GROUP]}}}
        for count, expected in [(0, 'pending'), (1, 'observed')]:
            responses = [{'properties': {'customerId': self.context['tenantId']}},
                         {'properties': {'enabled': True, 'emailReceivers': [{'name': 'test'}]}},
                         rule, rule, [{'matching_events': count, 'failure_events': count}]]
            with patch.object(assurance, 'az', side_effect=responses):
                result = assurance.inspect_monitoring(self.context, 'a' * 32)
            self.assertEqual(result['status'], expected)
            self.assertFalse(result['notification_delivery_verified'])
            self.assertFalse(result['end_to_end_verified'])


if __name__ == '__main__':
    unittest.main()
