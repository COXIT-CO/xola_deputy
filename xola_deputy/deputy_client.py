""""`Have class DeputyCLient,which connect to deputy API and get/post data from here"""
import json
import configparser

import requests


class DeputyClient():
    """"Connect to Deputy API"""
    __headers = {}
    __url = ""

    def __init__(self, logger):
        config = configparser.ConfigParser()
        config.read('Settings.ini')
        deputy_access_token, deputy_id = config["DEPUTY"]["deputy_access_token"],\
            config["DEPUTY"]["deputy_id"]
        self.__headers = {
            'Authorization': 'OAuth ' + deputy_access_token,
        }
        self.__url = 'https://' + deputy_id + '/api/v1/'
        self.log = logger

    def post_new_shift(self, params_for_deputy):
        """post a new shift
        :param params_for_deputy: data to post requst
        :return: str. id shift
        """
        json_mylist = json.dumps(params_for_deputy)
        data = f"{json_mylist}"
        url = self.__url + 'supervise/roster/'
        try:
            response = requests.post(
                url=url, headers=self.__headers, data=data)
            return str(response.json()["Id"])
        except requests.RequestException as ex:
            self.log.error(
                "Unable to send post request to DEPUTY",
                exc_info=ex)

    def get_people_availability(self, shift_id):
        """Take id employee,which can work in taken shift
        :param shift_id: id shift ,which have not employee
        :return: id free employeee
        """
        url = self.__url + 'supervise/getrecommendation/' + shift_id
        response = requests.get(url=url, headers=self.__headers,)
        try:
            dictionar = list(response.json()["trained"])
            return dictionar[0]
        except IndexError:
            self.log.warning("Not Available employee")
