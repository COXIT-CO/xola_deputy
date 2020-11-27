""""This script creat config file, and u must run this script first of all"""
import sys
import argparse
import configparser
from os import path

from xola_deputy import xola_client


def create_parser():
    """Creat parameters passing from console"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-ex', '--email_xola')
    parser.add_argument('-px', '--password_xola')
    parser.add_argument('-dat', '--deputy_access_token')
    parser.add_argument('-did', '--deputy_id')
    parser.add_argument('-url', '--url')
    parser.add_argument('-logmode', '--logmode', default='file')
    parser.add_argument('-logpath', '--logpath', default='./logs')

    return parser


def initialize_variables():
    """Using parser to output parameters from console"""
    config = configparser.ConfigParser()
    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])

    config.add_section('XOLA')
    xola_email = namespace.email_xola
    xola_password = namespace.password_xola
    x_api_key, user_id = xola_client.XolaClient.take_xola_settings(
        xola_email, xola_password)
    config["XOLA"]["x_api_key"], config["XOLA"]["user_id"] = x_api_key, user_id

    config.add_section('DEPUTY')
    deputy_access_token = namespace.deputy_access_token
    deputy_id = namespace.deputy_id
    config["DEPUTY"]["deputy_access_token"], config["DEPUTY"]["deputy_id"] = \
        deputy_access_token, deputy_id

    config.add_section('LOG')
    config["LOG"]["log_path"], config["LOG"]["log_mode"] = namespace.logpath, namespace.logmode

    config.add_section('URL')
    config['URL']['public_url'] = namespace.url

    with open('xola_deputy/Settings.ini', 'w') as configfile:  # save
        config.write(configfile)


if __name__ == '__main__':
    if path.isfile('xola_deputy/Settings.ini'):
        key = input("Do you really wanna change your settings?(y/n) ")
        print (key)
        if key == "y":
            initialize_variables()
        else:
            sys.exit("Script is terminated")
    else:
        initialize_variables()
