"""Negative security tests run against the actual compiled template in CI."""
import copy
import json
import os
from pathlib import Path
import unittest

import check_ml_security as security


@unittest.skipUnless(os.environ.get('IYQPIS_COMPILED_ML'), 'requires compiled ML template; CI supplies it')
class CompiledSecurityTests(unittest.TestCase):
    def setUp(self):
        self.template = json.loads(Path(os.environ['IYQPIS_COMPILED_ML']).read_text())

    def test_reference_baseline(self):
        self.assertEqual(security.validate(self.template)['status'], 'passed')

    def test_security_regressions_are_refused(self):
        mutations = [
            ('Microsoft.Storage/storageAccounts', lambda r: r['properties'].update(publicNetworkAccess='Enabled')),
            ('Microsoft.Storage/storageAccounts', lambda r: r['properties'].update(allowSharedKeyAccess=True)),
            ('Microsoft.Storage/storageAccounts', lambda r: r['properties']['networkAcls'].update(bypass='AzureServices')),
            ('Microsoft.Storage/storageAccounts', lambda r: r.update(name='INVALID-NAME')),
            ('Microsoft.Storage/storageAccounts', lambda r: r['sku'].update(name='Standard_GRS')),
            ('Microsoft.MachineLearningServices/workspaces', lambda r: r['properties'].update(publicNetworkAccess='Enabled')),
            ('Microsoft.MachineLearningServices/workspaces', lambda r: r['properties'].update(systemDatastoresAuthMode='accessKey')),
        ]
        for kind, mutate in mutations:
            with self.subTest(kind=kind, mutation=mutate):
                document = copy.deepcopy(self.template)
                mutate(next(r for r in security.resources(document) if r['type'] == kind))
                with self.assertRaises(ValueError):
                    security.validate(document)

    def test_missing_or_miswired_endpoint_is_refused(self):
        for label in ('workspace', 'blob', 'file'):
            for remove in (True, False):
                with self.subTest(label=label, remove=remove):
                    document = copy.deepcopy(self.template)
                    module = next(r for r in document['resources'] if r.get('name') == f'ml-learning-{label}-endpoint')
                    if remove:
                        document['resources'].remove(module)
                    else:
                        module['properties']['parameters']['targetId']['value'] = 'wrong-target'
                    with self.assertRaises(ValueError):
                        security.validate(document)

    def test_scope_expansion_is_refused(self):
        for kind in ('computes', 'onlineEndpoints', 'batchEndpoints'):
            with self.subTest(kind=kind):
                document = copy.deepcopy(self.template)
                document['resources'].append({'type': 'Microsoft.MachineLearningServices/workspaces/' + kind})
                with self.assertRaises(ValueError):
                    security.validate(document)


if __name__ == '__main__':
    unittest.main()
