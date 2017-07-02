# -*- coding: utf-8 -*-
from __future__ import absolute_import

import inspect
import logging
from os.path import expanduser

import yaml
from crust import config_defs


logger = logging.getLogger(__name__)


class InvalidOption(Exception):
    def __init__(self, opt):
        super(InvalidOption, self).__init__("Invalid option: {}".format(opt))
        self.opt = opt


class InvalidOptionValue(Exception):
    def __init__(self, opt, val, val_type):
        super(InvalidOptionValue, self).__init__(
            "Invalid option value: '{}' value '{}' is not of '{}' type"
            .format(opt, val, val_type.__name__))
        self.opt = opt
        self.val = val
        self.val_type = val_type


class ConfigFileReadError(Exception):
    def __init__(self, conf_file):
        super(ConfigFileReadError, self).__init__(
            "Cannot read crust config file: {}".format(conf_file))
        self.conf_file = conf_file


class ConfigFileNotFound(Exception):
    def __init__(self, conf_file):
        super(ConfigFileNotFound, self).__init__(
            "Cannot find crust config file: {}".format(conf_file))
        self.conf_file = conf_file


class Config(object):
    '''
    This class will be used to access the config options values that are
    declared in config_defs.py

    For instance if there is a config option declared in config_defs.py as:
      CUSTOM_OPTION = ("custom_option", "hello", str)

    Then to access the value of this option, one cam just do:
      Config.CUSTOM_OPTION
    '''
    pass


class ConfigMgr(object):
    _instance = None

    @staticmethod
    def load_options(cli_opts=None):
        if not ConfigMgr._instance:
            ConfigMgr._instance = ConfigMgr()
        if cli_opts:  # check if crust_conf opt is defined
            for opt, val in cli_opts:
                if opt == "crust_conf":
                    setattr(Config, 'CRUST_CONF', val)
        ConfigMgr._instance.process_file_opts()
        ConfigMgr._instance.process_cli_opts(cli_opts)

    @staticmethod
    def log_options_values():  # pragma: no cover
        for opt, (var, _) in ConfigMgr._instance.config_opts.items():
            val = getattr(Config, var)
            logger.debug("%s = %s", opt, val)

    def __init__(self):
        # Config class must be empty. All config options declarations should
        # be done in config_defs.py
        assert not [i for i in dir(Config) if not inspect.ismethod(i) and
                    not i.startswith('_')]

        opt_vars = [i for i in dir(config_defs) if not inspect.ismethod(i) and
                    not i.startswith('_')]
        self.config_opts = dict([
            (getattr(config_defs, opt)[0], (opt, getattr(config_defs, opt)[2]))
            for opt in opt_vars])

        # populate Config class
        for opt in opt_vars:
            opt_triplet = getattr(config_defs, opt)
            setattr(Config, opt, opt_triplet[1])

    def _set_opt_value(self, opt, val):
        if opt not in self.config_opts:
            raise InvalidOption(opt)
        if not isinstance(val, self.config_opts[opt][1]):
            raise InvalidOptionValue(opt, val, self.config_opts[opt][1])
        setattr(Config, self.config_opts[opt][0], val)

    def process_cli_opts(self, cli_opts):
        if not cli_opts:
            return

        for opt, val in cli_opts:
            self._set_opt_value(opt, val)

    def _read_conf_file(self, conf_file):
        try:
            with open(conf_file, 'r') as stream:
                try:
                    config = yaml.load(stream)
                    if not isinstance(config, dict):
                        raise ConfigFileReadError(conf_file)
                    for opt, val in config.items():
                        self._set_opt_value(opt, val)
                except yaml.YAMLError:
                    raise ConfigFileReadError(conf_file)
        except IOError:
            raise ConfigFileNotFound(Config.CRUST_CONF)

    def process_file_opts(self):
        if Config.CRUST_CONF:
            self._read_conf_file(Config.CRUST_CONF)
        else:
            try:
                # read user config file if exists
                self._read_conf_file(expanduser("~/.crust"))
            except ConfigFileNotFound:
                pass
            try:
                # read local config file if exists
                self._read_conf_file(".crust")  # local config file
                return
            except ConfigFileNotFound:
                pass  # no config file, fallback to default options
