""""`Have class XolaCLient,which connect to Xola API and get/post data from here"""
import configparser
from datetime import datetime
import json
import requests


class XolaClient():
    """connect to XOLA API"""
    __url = "https://xola.com/api/"

    def __init__(self, logger):
        config = configparser.ConfigParser()
        config.read('Settings.ini')
        self.__x_api_key, self.__user_id = config['XOLA']['x_api_key'], config['XOLA']['user_id']
        self.public_url = config['URL']['public_url']
        self.__headers = {
            'X-API-KEY': self.__x_api_key,
        }
        self.log = logger

    def subscribe_to_webhook(self,):
        """do post request to xola api: subscribe to weebhook(order.created)
        :param public_url: public url,where post notification
        :return: bool, false if something wrong, true if all good
        """
        url = self.__url + "users/" + self.__user_id + "/hooks"
        param = {"eventName": "order.create", "url": self.public_url+"/xola"}
        json_mylist = json.dumps(param)
        data = f"{json_mylist}"
        try:
            response = requests.post(
                url=url, headers=self.__headers, data=data)
            if response.status_code != 201:
                if response.status_code == 409:
                    self.log.warning("Webhook already subscribe")
                    return False
                self.log.error("Subscription failed " +
                               "response.status_code = " +
                               str(response.status_code) +
                               " - " +
                               response.text)
                return False
            return True
        except requests.RequestException as ex:
            self.log.error("Unable to send post request to XOLA", exc_info=ex)

    def take_params_from_responce(self, request):
        """take data from json, and process them
        :param request: json format data
        :return: dict with parameters to deputy
         """
        data = request.json["items"][0]["arrival"].split("-")  # list
        data = [int(x) for x in data]
        time = str(request.json["items"][0]["arrivalTime"])
        hour, minute = int(time[:2]), int(time[2:])
        time_start = self.convert_time(data[0], data[1], data[2], hour, minute)
        duration = int(request.json["meta"]["abandonOrders"]
                       [0]["items"][0]["experience"]["eventDuration"]) * 60
        time_end = time_start + duration
        params = {
            "intStartTimestamp": time_start,
            "intEndTimestamp": time_end,
            "intOpunitId": 3,
        }
        return params

    @staticmethod
    def convert_time(year, month, day, hour, minute):
        """change data and time into UNIX time stamp
        :param year: correct year
        :param month: correct month
        :param day: correct day
        :param hour: correct hour
        :param minute: correct minute

        :return: unix time stamp
        """
        data_time = datetime(year, month, day, hour, minute)
        timestamp = data_time.timestamp()
        return int(timestamp)

    @staticmethod
    def take_xola_settings(email, password):
        """"Get APi KEY from xola """
        response = requests.get(
            'https://sandbox.xola.com/api/users/me',
            auth=(
                email,
                password))
        return response.json()["apiKey"], response.json()["id"]

    def start(self, request):
        """starting"""
        try:
            params = self.take_params_from_responce(request)
            return params
        except (ValueError, TypeError):
            self.log.error("Bad JSON data")
            return False
