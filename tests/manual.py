import sys

from gdockutils import conf


def main():
    sys.path.append('/src/tests/fixtures')
    config = conf.Config()
    # config.set('TEST', True, file='tests/fixtures/.env', force=True)
    # print(config.getroot('TEST', file='tests/fixtures/.env'))
    config.set('SECRET', False, file='tests/fixtures/.secret.env', force=True)
    config.list(envfile='tests/fixtures/.env', secretfile='tests/fixtures/.secret.env')


if __name__ == '__main__':
    main()
