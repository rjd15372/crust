# -*- coding: utf-8 -*-
from __future__ import absolute_import

import logging.config

from .config import ConfigMgr, InvalidOption, ConfigFileNotFound, \
                    ConfigFileReadError


try:
    ConfigMgr.load_options([("salt_api_host", 'localhost')])
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'default': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            '': {
                'handlers': ['default'],
                'level': 'DEBUG',
                'propagate': True
            }
        }
    })

    ConfigMgr.log_options_values()
except (InvalidOption, ConfigFileNotFound, ConfigFileReadError) as ex:
    print(ex.message)
