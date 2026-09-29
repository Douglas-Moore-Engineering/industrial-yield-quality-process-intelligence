import base64
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('private_probe', Path(__file__).with_name('private-probe.py'))
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def jwt(actions):
    payload = base64.urlsafe_b64encode(json.dumps({'access': [{'actions': actions}]}).encode()).decode().rstrip('=')
    return 'header.' + payload + '.signature'


class PrivateProbeSafetyTests(unittest.TestCase):
    settings = {'registryHost': 'registry.example.com', 'runtimeClientId': 'test-runtime', 'publisherClientId': 'test-publisher'}

    @patch.object(probe, 'token', return_value='not-a-real-token')
    def test_runtime_push_must_be_denied(self, _):
        responses = [(200, b'{"refresh_token":"test"}', {}), (200, json.dumps({'access_token': jwt(['pull'])}).encode(), {}), (403, b'', {})]
        with patch.object(probe, 'request', side_effect=responses) as request:
            probe.registry_grants(self.settings, 'runtimeClientId', ['pull'])
            self.assertEqual(request.call_count, 3)

    @patch.object(probe, 'token', return_value='not-a-real-token')
    def test_excess_runtime_privilege_fails(self, _):
        responses = [(200, b'{"refresh_token":"test"}', {}), (200, json.dumps({'access_token': jwt(['pull','push'])}).encode(), {})]
        with patch.object(probe, 'request', side_effect=responses):
            with self.assertRaisesRegex(RuntimeError, 'scope grants'):
                probe.registry_grants(self.settings, 'runtimeClientId', ['pull'])

    @patch.object(probe, 'token', return_value='not-a-real-token')
    def test_cancellation_never_sends_token_to_other_host(self, _):
        responses = [(200, b'{"refresh_token":"test"}', {}), (200, json.dumps({'access_token': jwt(['pull','push'])}).encode(), {}), (202, b'', {'Location': 'https://untrusted.example.com/upload'})]
        with patch.object(probe, 'request', side_effect=responses) as request:
            with self.assertRaisesRegex(RuntimeError, 'registry host'):
                probe.registry_grants(self.settings, 'publisherClientId', ['pull','push'])
            self.assertEqual(request.call_count, 3)

    def test_public_dns_fails_before_authentication(self):
        with patch.object(probe.socket, 'getaddrinfo', return_value=[(None,None,None,None,('1.1.1.1',443))]), patch.object(probe, 'token') as token:
            with self.assertRaisesRegex(RuntimeError, 'Private DNS'):
                probe.run({'hosts':['registry.example.com'], 'endpointSubnet':'10.80.0.0/24'})
            token.assert_not_called()


if __name__ == '__main__':
    unittest.main()
