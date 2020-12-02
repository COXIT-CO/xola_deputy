""""`Have class XolaCLient,which connect to Xola API and get/post data from here"""
import configparser
from datetime import datetime
from math import ceil
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

    def get_data_from_event(self,event_id):
        """
        :param event_id: str. with event id
        :return: response json format,with all fields
        """
        url = self.__url + "events/" + event_id
        try:
            response = requests.get(
                url=url, headers=self.__headers)
            return response
        except requests.RequestException as ex:
            self.log.error("Unable to send gey request to XOLA", exc_info=ex)

    def take_params_from_responce(self, request):
        """take data from json, and process them
        :param request: json format data
        :return: dict with parameters to deputy
         """
        event_id = request.json["data"]["items"][0]["event"]["id"]
        response = self.get_data_from_event(event_id)

        time_start = self.convert_time(response.json()["start"])
        time_end = self.convert_time(response.json()["end"])
        experience_id = response.json()["experience"]["id"]
        ticket_count = response.json()["quantity"]["reserved"]#all ticket for 1 event

        area = self.compare_experience_and_area(experience_id)
        shift_count = area["shift_count"]

        params = {
            "intStartTimestamp": time_start,
            "intEndTimestamp": time_end,
            "intOpunitId": area["area_id"],
        }

        number_shifts = self.calculation_of_guids(shift_count, ticket_count)

        return params, number_shifts

    def start(self, request):
        """starting"""
        try:
            params, number_shifts = self.take_params_from_responce(request)
            return params, number_shifts
        except (ValueError, TypeError):
            self.log.error("Bad JSON data")
            return False


    @staticmethod
    def calculation_of_guids(shift_count, ticket_count):
        """
        :param shift_count: number max ticket for 1 person
        :param ticket_count: all tickets which reserved in event
        :return: how many new shifts we have to do
        """
        if shift_count == 1: #we don`t need divine ticket on guids|do 1 shift
            return 1
        if ticket_count < shift_count : # 20<shift_count<25
            return 1
        else:
            return ceil(ticket_count/shift_count)

    @staticmethod
    def compare_experience_and_area(experience_id):
        """
        :param experience_id: id experience from xola
        :return: area id and ticket divine to deputy
        """
        with open("data_file.json", "r") as write_file:
            dani = json.load(write_file)
        for exp in dani:
            if exp["experience_id"] == experience_id:
                return exp["area"]

    @staticmethod
    def convert_time(time):
        """change data and time into UNIX time stamp
        :param time: time format in iso format

        :return: unix time stamp
        """
        timestamp = datetime.fromisoformat(time).timestamp()
        return int(timestamp)

    @staticmethod
    def take_xola_settings(email, password):
        """"Get APi KEY from xola """
        response = requests.get(
            'https://xola.com/api/users/me',
            auth=(
                email,
                password))
        return response.json()["apiKey"], response.json()["id"]