"""Init logger parameters"""
import configparser

import logging
from logging.config import dictConfig

from global_config import CONFIG_FILE_NAME, LOG_CONFIG

DEFAULT_NAME_FLASK_LOGGER = 'werkzeuq'


class LoggerClient():
    """Create logger object"""
    logger = logging.getLogger()
    logmode = "console"

    def settings_init(self):
        """Parser the Settings.ini file, and get parameters for logger"""
        config_console = configparser.ConfigParser()
        config_console.read(CONFIG_FILE_NAME)
        self.logmode = config_console["LOG"]["log_mode"]

    def logger_settings(self):
        """create logger object and do some configuration with them"""
        LOG_CONFIG['root']['handlers'].append(self.logmode)
        flask_log = logging.getLogger(DEFAULT_NAME_FLASK_LOGGER)
        flask_log.setLevel(logging.ERROR)
        dictConfig(LOG_CONFIG)
        self.logger = logging.getLogger()

    def get_logger(self):
        """init logfer setting
        :return:logger object
        """
        self.logger_settings()
        return self.logger
