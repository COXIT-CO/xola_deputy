"""Init logger parameters"""
import configparser

import logging
from logging.config import dictConfig
from config import LOG_CONFIG


class LoggerClient():
    """Create logger object"""
    logger = logging.getLogger()

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('Settings.ini')
        self.logmode = config["LOG"]["log_mode"]

    def logger_settings(self):
        """create logger object and do some configuration with them"""
        LOG_CONFIG['root']['handlers'].append(self.logmode)
        flask_log = logging.getLogger('werkzeug')
        flask_log.setLevel(logging.ERROR)
        dictConfig(LOG_CONFIG)
        self.logger = logging.getLogger()

    def get_logger(self):
        """init logfer setting
        :return:logger object
        """
        self.logger_settings()
        return self.logger
