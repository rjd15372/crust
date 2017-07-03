# -*- coding: utf-8 -*-
# pylint: disable=W0611,E0401,C0411,W0212
import context
import inspect
from pyfakefs import fake_filesystem_unittest
from os.path import expanduser
from config import ConfigMgr, Config, InvalidOption, ConfigFileReadError, \
                   ConfigFileNotFound, InvalidOptionValue


class TestConfig(fake_filesystem_unittest.TestCase):
    def setUp(self):
        self.setUpPyfakefs()
        config_opts = [i for i in dir(Config) if not inspect.ismethod(i) and
                       not i.startswith('_')]
        for opt in config_opts:
            delattr(Config, opt)
        ConfigMgr._instance = None

    def test_no_conf_file(self):
        ConfigMgr.load_options()
        self.assertEqual(Config.SALT_API_PORT, 8000)
        self.assertEqual(Config.LOG_LEVEL, "INFO")

    def test_local_file(self):
        self.fs.CreateFile(".crust",
                           contents="salt_api_port: 8080\n"
                                    "log_level: debug")
        ConfigMgr.load_options()
        self.fs.RemoveFile(".crust")
        self.assertEqual(Config.SALT_API_PORT, 8080)
        self.assertEqual(Config.LOG_LEVEL, "debug")

    def test_user_file(self):
        conf_file = expanduser("~/.crust")
        self.fs.CreateFile(conf_file,
                           contents="salt_api_port: 4000\n"
                                    "log_level: debug")
        ConfigMgr.load_options()
        self.fs.RemoveFile(conf_file)
        self.assertEqual(Config.SALT_API_PORT, 4000)
        self.assertEqual(Config.LOG_LEVEL, "debug")

    def test_cli_opts(self):
        ConfigMgr.load_options([
            ('salt_api_port', 6000),
            ('log_level', 'warn')
        ])
        self.assertEqual(Config.SALT_API_PORT, 6000)
        self.assertEqual(Config.LOG_LEVEL, "warn")

    def test_crust_conf_opt(self):
        conf_file = "mycrustrc"
        self.fs.CreateFile(conf_file,
                           contents="salt_api_port: 8090\n"
                                    "log_level: critic")
        ConfigMgr.load_options([("crust_conf", conf_file)])
        self.fs.RemoveFile(conf_file)
        self.assertEqual(Config.SALT_API_PORT, 8090)
        self.assertEqual(Config.LOG_LEVEL, "critic")

    def test_crust_conf_opt_precedence(self):
        conf_file = "mycrustrc"
        self.fs.CreateFile(conf_file,
                           contents="salt_api_port: 8090\n"
                                    "log_level: critic")
        local_conf = ".crust"
        self.fs.CreateFile(local_conf,
                           contents="salt_api_port: 9000\n"
                                    "salt_api_host: localhost")
        ConfigMgr.load_options([("crust_conf", conf_file)])
        self.fs.RemoveFile(conf_file)
        self.fs.RemoveFile(local_conf)
        self.assertEqual(Config.SALT_API_PORT, 8090)
        self.assertEqual(Config.SALT_API_HOST, "salt")
        self.assertEqual(Config.LOG_LEVEL, "critic")

    def test_config_precedence(self):
        local_conf = ".crust"
        user_conf = expanduser("~/.crust")
        self.fs.CreateFile(local_conf,
                           contents="salt_api_port: 9000\n"
                                    "salt_api_host: localhost")
        self.fs.CreateFile(user_conf,
                           contents="salt_api_port: 7000\n"
                                    "salt_api_host: userhost\n"
                                    "log_level: debug")
        ConfigMgr.load_options([("salt_api_port", 1000)])
        self.fs.RemoveFile(local_conf)
        self.fs.RemoveFile(user_conf)
        self.assertEqual(Config.SALT_API_PORT, 1000)
        self.assertEqual(Config.SALT_API_HOST, "localhost")
        self.assertEqual(Config.SALT_API_EAUTH, "auto")
        self.assertEqual(Config.LOG_LEVEL, "debug")

    def test_invalid_opt(self):
        with self.assertRaises(InvalidOption) as ctx:
            ConfigMgr.load_options([("salt_invalid_opt", 1000)])
        self.assertTrue("Invalid option: salt_invalid_opt" in ctx.exception)

    def test_invalid_yaml_1(self):
        self.fs.CreateFile(".crust",
                           contents="salt_api_port = 9000\n"
                                    "salt_api_host = localhost")
        with self.assertRaises(ConfigFileReadError) as ctx:
            ConfigMgr.load_options()
        self.fs.RemoveFile(".crust")
        self.assertTrue(
            "Cannot read crust config file: .crust" in ctx.exception)

    def test_invalid_yaml_2(self):
        self.fs.CreateFile(".crust",
                           contents="salt_api_port: 9000\n"
                                    "  - - salt_api_host: localhost")
        with self.assertRaises(ConfigFileReadError) as ctx:
            ConfigMgr.load_options()
        self.fs.RemoveFile(".crust")
        self.assertTrue(
            "Cannot read crust config file: .crust" in ctx.exception)

    def test_conf_file_not_found(self):
        with self.assertRaises(ConfigFileNotFound) as ctx:
            ConfigMgr.load_options([("crust_conf", "mycrustfile")])
        self.assertTrue(
            "Cannot find crust config file: mycrustfile" in ctx.exception)

    def test_opt_invalid_type(self):
        with self.assertRaises(InvalidOptionValue) as ctx:
            ConfigMgr.load_options([("salt_api_port", "80")])
        self.assertTrue(
            "'salt_api_port' value '80' is not of 'int' type" in
            ctx.exception.message)

    def test_config_instance(self):
        self.fs.CreateFile(".crust",
                           contents="salt_api_port: 8080\n"
                                    "log_level: debug")
        ConfigMgr.load_options()
        self.fs.RemoveFile(".crust")
        self.assertEqual(Config.SALT_API_PORT, 8080)
        self.assertEqual(Config.LOG_LEVEL, "debug")
        ConfigMgr.load_options()
        self.assertEqual(Config.SALT_API_PORT, 8080)
        self.assertEqual(Config.LOG_LEVEL, "debug")
