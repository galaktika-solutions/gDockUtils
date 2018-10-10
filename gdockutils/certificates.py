import argparse
import time
import os

from . import run, cp
from .ui import SECRET_SOURCE_DIR


def create(hostnames, ips):
    ips = ips or []
    cn = hostnames[0]
    spec = ['DNS:%s' % n for n in hostnames]
    spec += ['IP:%s' % i for i in ips]
    san = ','.join(spec)
    timestamp = time.strftime('%Y-%m-%d-%H-%M-%S', time.gmtime())
    ca_name = '%s-ca-%s' % (cn, timestamp)

    # generate CA private key
    run(['openssl', 'genrsa', '-out', 'ca.key', '2048'], cwd='/tmp')
    # self signed CA certificate
    run([
        'openssl', 'req', '-x509', '-new', '-nodes',
        '-subj', '/commonName=%s' % ca_name,
        '-key', 'ca.key', '-sha256', '-days', '1024', '-out', 'ca.crt'
    ], cwd='/tmp')
    # generate private key
    run(['openssl', 'genrsa', '-out', 'certificate.key', '2048'], cwd='/tmp')
    # certificate request
    with open('/etc/ssl/openssl.cnf', 'r') as f:
        orig_conf = f.read()
    with open('/tmp/openssl.cnf', 'w') as f:
        f.write(orig_conf)
        f.write('\n[SAN]\nsubjectAltName=%s\n' % san)
    run([
        'openssl', 'req', '-new', '-sha256',
        '-subj', '/commonName=%s' % cn,
        '-key', 'certificate.key', '-reqexts', 'SAN',
        '-out', 'certificate.csr', '-config', 'openssl.cnf'
    ], cwd='/tmp')
    # sign the certificate with CA
    run([
        'openssl', 'x509', '-req', '-in', 'certificate.csr', '-CA', 'ca.crt',
        '-CAkey', 'ca.key', '-out', 'certificate.crt', '-days', '1024',
        '-sha256', '-extensions', 'SAN', '-CAcreateserial', '-CAserial',
        'ca.srl', '-extfile', 'openssl.cnf'
    ], cwd='/tmp')

    stat = os.stat('.')
    os.makedirs(SECRET_SOURCE_DIR, exist_ok=True)
    os.chown(SECRET_SOURCE_DIR, stat.st_uid, stat.st_gid)
    cp(
        '/tmp/ca.crt',
        os.path.join(SECRET_SOURCE_DIR, '%s-%s-ca.crt' % (cn, timestamp)),
        stat.st_uid, stat.st_gid, mode=0o644
    )
    cp(
        '/tmp/certificate.crt',
        os.path.join(SECRET_SOURCE_DIR, '%s-%s.crt' % (cn, timestamp)),
        stat.st_uid, stat.st_gid, mode=0o644
    )
    cp(
        '/tmp/certificate.key',
        os.path.join(SECRET_SOURCE_DIR, '%s-%s.key' % (cn, timestamp)),
        stat.st_uid, stat.st_gid, mode=0o644
    )


def create_cli():
    parser = argparse.ArgumentParser(
        description=(
            'Creates certificates for development purposes.'
        ),
    )
    parser.add_argument(
        '-n', '--hostname', action='append',
        help='specify a host name'
    )
    parser.add_argument(
        '-i', '--ip', action='append',
        help='specify an ip address'
    )
    args = parser.parse_args()
    if not args.hostname:
        parser.error('At least one host name must be specified.')

    create(args.hostname, args.ip)
