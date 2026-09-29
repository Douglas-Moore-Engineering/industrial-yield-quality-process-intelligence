"""One-shot private Grafana setup. Settings arrive as JSON; no secrets logged."""
import copy
import ipaddress
import json
import os
import re
import socket
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from azure.identity import ManagedIdentityCredential


def main(settings):
    endpoint = settings['endpoint'].rstrip('/')
    host = urllib.parse.urlparse(endpoint).hostname
    addresses = {r[4][0] for r in socket.getaddrinfo(host, 443)}
    assert addresses and all(ipaddress.ip_address(a) in ipaddress.ip_network('10.80.0.0/24') for a in addresses)
    credential = ManagedIdentityCredential(client_id=os.environ['AZURE_CLIENT_ID'])

    def api(path, body=None, method=None):
        token = credential.get_token('https://dashboard.azure.com/.default').token
        req = urllib.request.Request(endpoint + path, data=json.dumps(body).encode() if body is not None else None,
            headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}, method=method)
        try:
            with urllib.request.urlopen(req, timeout=45) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if path == '/api/ds/query':
                message = error.read().decode(errors='replace')
                message = re.sub(r'[0-9a-fA-F]{8}-(?:[0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}', '<id>', message)
                print('QUERY_DIAGNOSTIC ' + message[:3000], flush=True)
            raise

    for attempt in range(12):
        try:
            api('/api/org')
            break
        except urllib.error.HTTPError as error:
            if error.code not in (401, 403) or attempt == 11:
                raise
            time.sleep(10)
    ds = {'uid': 'iyqpis-monitor', 'name': 'IYQPIS Azure Monitor', 'type': 'grafana-azure-monitor-datasource',
          'access': 'proxy', 'jsonData': {'azureAuthType': 'msi', 'subscriptionId': settings['subscription']}}
    try:
        api('/api/datasources/uid/iyqpis-monitor')
        api('/api/datasources/uid/iyqpis-monitor', ds, 'PUT')
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise
        api('/api/datasources', ds, 'POST')
    dashboard = copy.deepcopy(settings['dashboard'])
    dashboard.pop('__inputs', None)
    dashboard['templating']['list'][0]['query'] = settings['workspace']
    for panel in dashboard['panels']:
        if 'datasource' in panel:
            panel['datasource']['uid'] = 'iyqpis-monitor'
        for target in panel.get('targets', []):
            target['azureLogAnalytics']['resources'] = [settings['workspace']]
    result = api('/api/dashboards/db', {'dashboard': dashboard, 'overwrite': True}, 'POST')
    assert result.get('status') == 'success'
    saved = api('/api/dashboards/uid/iyqpis-reference')
    assert saved['dashboard']['title'] == dashboard['title']
    print('GRAFANA_DASHBOARD_IMPORTED', flush=True)
    query = {'refId': 'A', 'datasource': {'type': ds['type'], 'uid': ds['uid']},
             'queryType': 'Azure Log Analytics', 'azureLogAnalytics': {
                 'query': 'print Connectivity=1', 'resources': [settings['workspace']], 'resultFormat': 'table'}}
    response = api('/api/ds/query', {'queries': [query], 'from': 'now-1h', 'to': 'now'}, 'POST')
    value = response['results']['A']
    assert not value.get('error') and value.get('frames'), 'Grafana log-query verification failed'
    print('GRAFANA_PRIVATE_QUERY_PASSED', flush=True)


if __name__ == '__main__':
    main(json.loads(sys.argv[1]))
