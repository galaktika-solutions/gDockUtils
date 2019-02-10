import sys

from gdockutils.conf import Config


def main():
    sys.path.append('/src/tests/fixtures')
    config = Config(
        env_file='tests/fixtures/.env',
        secret_file='tests/fixtures/.secret.env'
    )
    # config.setroot('TEST', True)
    # print(config.getroot('TEST'))
    # config.setroot('SECRET', False)
    # config.setroot('USERNAME', 'gstack')
    # config.deleteroot('REPORTNAME')
    # config.get('USERNAME')
    config.setroot('WIFEAGE', 23)
    config.setroot('SECRET', True)
    config.list()
    print(config.getroot('WIFEAGE'))


if __name__ == '__main__':
    main()
