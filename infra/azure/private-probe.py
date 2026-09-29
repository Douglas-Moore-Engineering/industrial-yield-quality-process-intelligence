"""Runs on a temporary private VM using only Python's standard library.

Prints pass/fail labels, never identity IDs, access tokens, or response bodies.
Settings are generated locally and substituted into cloud-init, not committed.
"""
import base64
import ipaddress
import json
import socket
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request


def request(url, data=None, headers=None, method=None):
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return response.status, response.read(), response.headers
    except urllib.error.HTTPError as error:
        return error.code, error.read(), error.headers


def check(condition, label):
    if not condition:
        raise RuntimeError(label)
    print('PASS: ' + label, flush=True)


def token(client_id, resource):
    query = urllib.parse.urlencode({'api-version': '2018-02-01', 'resource': resource, 'client_id': client_id})
    code, body, _ = request('http://169.254.169.254/metadata/identity/oauth2/token?' + query, headers={'Metadata': 'true'})
    check(code == 200, 'Managed identity token request')
    return json.loads(body)['access_token']


def registry_grants(settings, identity, expected):
    host = settings['registryHost']
    access = token(settings[identity], 'https://containerregistry.azure.net')
    form = urllib.parse.urlencode({'grant_type': 'access_token', 'service': host, 'access_token': access}).encode()
    code, body, _ = request('https://' + host + '/oauth2/exchange', form)
    check(code == 200, identity + ' registry token exchange')
    refresh = json.loads(body)['refresh_token']
    form = urllib.parse.urlencode({'grant_type': 'refresh_token', 'service': host, 'scope': 'repository:platform-acceptance:pull,push', 'refresh_token': refresh}).encode()
    code, body, _ = request('https://' + host + '/oauth2/token', form)
    check(code == 200, identity + ' scoped registry token')
    jwt = json.loads(body)['access_token']
    payload = jwt.split('.')[1]
    claims = json.loads(base64.urlsafe_b64decode(payload + '=' * (-len(payload) % 4)))
    actions = {a for grant in claims.get('access', []) for a in grant.get('actions', [])}
    check(actions == set(expected), identity + ' registry scope grants')
    # A real push-initiation operation verifies enforcement, without storing an image.
    code, _, response_headers = request('https://' + host + '/v2/platform-acceptance/blobs/uploads/', b'', {'Authorization': 'Bearer ' + jwt}, 'POST')
    if 'push' in expected:
        check(code == 202, identity + ' push initiation accepted')
        cancel_url = urllib.parse.urljoin('https://' + host, response_headers['Location'])
        check(urllib.parse.urlparse(cancel_url).hostname == host, 'Upload cancellation remains on registry host')
        code, _, _ = request(cancel_url, headers={'Authorization': 'Bearer ' + jwt}, method='DELETE')
        check(code == 204, 'Temporary registry upload cancelled')
    else:
        check(code in (401, 403), identity + ' push denied')


def run(settings):
    for host in settings['hosts']:
        addresses = {item[4][0] for item in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)}
        network = ipaddress.ip_network(settings['endpointSubnet'])
        check(bool(addresses) and all(ipaddress.ip_address(a) in network for a in addresses), 'Private DNS within endpoint subnet')
        context = ssl.create_default_context()
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        with socket.create_connection((host, 443), timeout=20) as sock:
            with context.wrap_socket(sock, server_hostname=host) as tls:
                check(tls.version() in ('TLSv1.2', 'TLSv1.3'), 'Validated service certificate and TLS')
    for identity, expected in [('publisherClientId', ['pull', 'push']), ('runtimeClientId', ['pull'])]:
        registry_grants(settings, identity, expected)
    vault_token = token(settings['runtimeClientId'], 'https://vault.azure.net')
    code, body, _ = request('https://' + settings['vaultHost'] + '/secrets?api-version=7.4', headers={'Authorization': 'Bearer ' + vault_token})
    check(code == 403 and b'ForbiddenByRbac' in body, 'Runtime cannot read vault secrets (RBAC denial)')


if __name__ == '__main__':
    with open('/var/lib/platform-probe/settings.json', encoding='utf-8') as stream:
        settings = json.load(stream)
    for attempt in range(6):
        try:
            run(settings)
            print('IYQPIS_PROBE_PASS', flush=True)
            break
        except Exception as error:
            print('Probe retry: ' + type(error).__name__, flush=True)
            time.sleep(20)
    else:
        print('IYQPIS_PROBE_FAIL', flush=True)
