"""This script creates a config file for the main script.
 This should be run once at the very beginning before
the main script run (zola_deputy.py).
Then it should be run every time you want to reconfigure the script."""
import sys
import argparse
import configparser
from os import path


def create_parser():
    """Creates parameters passed from console"""
    parser = argparse.ArgumentParser()
    parser.add_argument('-xak', '--x_api_key')
    parser.add_argument('-ui', '--user_id')
    parser.add_argument('-dat', '--deputy_access_token')
    parser.add_argument('-did', '--deputy_id')
    parser.add_argument('-url', '--url')
    parser.add_argument('-spid', '--spreadsheet_id')
    parser.add_argument('-logmode', '--logmode', default='file')
    parser.add_argument('-logpath', '--logpath', default='./logs')

    return parser


def initialize_variables():
    """Using parser to output parameters from console"""
    config = configparser.ConfigParser()
    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])
    if len(sys.argv) == 1:
        sys.exit(
            "Please check if you run script with parameters . Script is terminated")

    config.add_section('XOLA')
    config["XOLA"]["x_api_key"], config["XOLA"]["user_id"] = namespace.x_api_key, namespace.user_id

    config.add_section('DEPUTY')
    deputy_access_token = namespace.deputy_access_token
    deputy_id = namespace.deputy_id
    config["DEPUTY"]["deputy_access_token"], config["DEPUTY"]["deputy_id"] = \
        deputy_access_token, deputy_id

    config.add_section('LOG')
    config["LOG"]["log_path"], config["LOG"]["log_mode"] = namespace.logpath, namespace.logmode

    config.add_section('URL')
    config['URL']['public_url'] = namespace.url

    config.add_section('GOOGLE')
    config['GOOGLE']['spreadsheet_id'] = namespace.spreadsheet_id


    with open('xola_deputy/Settings.ini', 'w') as configfile:  # save
        config.write(configfile)


if __name__ == '__main__':
    if path.isfile('xola_deputy/Settings.ini'):
        key = input("Do you really wanna change your settings?(y/n) ")
        if key == "y":
            initialize_variables()
        else:
            sys.exit("Script is terminated")
    else:
        initialize_variables()
