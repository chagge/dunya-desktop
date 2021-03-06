import os.path
import ConfigParser

import compmusic.dunya.conn


def _get_option(option):
    config = ConfigParser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), 'config.cfg'))
    return config.get('dunya', option)


def set_token():
    DUNYA_TOKEN = _get_option('token')
    compmusic.dunya.conn.set_token(DUNYA_TOKEN)


def set_hostname():
    DUNYA_HOSTNAME = _get_option('hostname')
    compmusic.dunya.conn.set_hostname(DUNYA_HOSTNAME)
