# -*- coding: utf-8 -*-
'''
In this module is declared all configuration options of crust.
Each config option is defined by a variable name that is assigned a triplet
with the config option name, the default value, and the type of the value.

If you need to add a new config option, just add it to this file.
'''

# Special option (DO NOT CHANGE THIS)
CRUST_CONF = ('crust_conf', None, str)

# Core options
LOG_FILE = ('log_file', '/var/log/crust.log', str)
LOG_LEVEL = ('log_level', 'INFO', str)

# Salt API options
SALT_API_HOST = ('salt_api_host', 'salt', str)
SALT_API_PORT = ('salt_api_port', 8000, int)
SALT_API_EAUTH = ('salt_api_eauth', 'auto', str)
