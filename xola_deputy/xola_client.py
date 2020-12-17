""""Have class XolaCLient,which connect to Xola API and get/post data from here.
    Also process data from xola-webhook for parameters to deputy post request"""
import configparser
from datetime import datetime
from math import ceil
import json
import requests

from global_config import compare_mapping, CONFIG_FILE_NAME

HTTP_CREATED = 201
HTTP_CONFLICT = 409


class XolaClient():
    """connect to XOLA API"""
    __url = "https://xola.com/api/"
    _event_id = ""
    _seller_id = ""

    def __init__(self, logger):
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE_NAME)
        self.__x_api_key, self.__user_id = config['XOLA']['x_api_key'], config['XOLA']['user_id']
        self.public_url = config['URL']['public_url']
        self.__headers = {
            'X-API-KEY': self.__x_api_key,
        }
        self.log = logger

    def subscribe_to_webhook(self, event_name="order.create"):
        """do post request to xola api: subscribe to weebhook(order.created)
        :param public_url: public url,where post notification
        :return: bool, false if something wrong, true if all good
        """
        url = self.__url + "users/" + self.__user_id + "/hooks"
        param = {"eventName": event_name, "url": self.public_url + "/xola"}
        json_mylist = json.dumps(param)
        data = f"{json_mylist}"
        try:
            response = requests.post(
                url=url, headers=self.__headers, data=data)
            if response.status_code != HTTP_CREATED:
                if response.status_code == HTTP_CONFLICT:
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

    def _get_data_from_event(self,):
        """
        Make request to XOLA events. Take all data from specific event
        :param event_id: str. with event id
        :return: response json format,with all fields
        """
        url = self.__url + "events/" + self._event_id
        try:
            response = requests.get(
                url=url, headers=self.__headers)
            return response
        except requests.RequestException as ex:
            self.log.error("Unable to send get request to XOLA", exc_info=ex)

    def take_params_from_responce(self, request):
        """Take data from json event request, and process them
        :param request: json format data
        :return: dict with parameters to deputy
         """
        self._event_id = request["data"]["items"][0]["event"]["id"]
        response = self._get_data_from_event()

        time_start = self.convert_time(response.json()["start"])
        time_end = self.convert_time(response.json()["end"])
        experience_id = response.json()["experience"]["id"]

        # all ticket for 1 event
        ticket_count = response.json()["quantity"]["reserved"]
        self._seller_id = response.json()["seller"]["id"]

        mapping = compare_mapping(experience_id, "experience")

        if mapping is False:
            self.log.error("Can not find experience in json file")
            raise ValueError
        shift_count = int(mapping["Shifts logic"])

        params = {
            "intStartTimestamp": time_start,
            "intEndTimestamp": time_end,
            # we need plus 2,because it is specific validation from deputy post
            # request
            "intOpunitId": int(mapping["Area"]) + 2,
        }

        number_shifts = self.calculation_of_employee(shift_count, ticket_count)

        return params, number_shifts, mapping

    def start(self, request):
        """starting"""
        try:
            params, number_shifts, title = self.take_params_from_responce(
                request)
            return params, number_shifts, title
        except (ValueError, TypeError):
            self.log.error("Bad JSON data")
            return False

    def get_list_of_guids(self):
        """
        make get request to xola, find all available guides
        :return: list of name all guides
        """
        url = self.__url + "sellers/" + self._seller_id + "/guides"
        list_guides = []
        try:
            response = requests.get(
                url=url, headers=self.__headers)
            for guide_name in response.json()["data"]:
                guides = (guide_name["name"], guide_name["id"])
                list_guides.append(guides)
            return list_guides
        except requests.RequestException as ex:
            self.log.error("Unable to send get request to XOLA", exc_info=ex)

    def take_guide_id(self, name_of_employee):
        """
        Compare name employee from deputy and guide from xola
        :param name_of_employee: employee name from deputy
        :return: guide id from xola
        """
        list_guides = self.get_list_of_guids()
        guide_id = ""
        for guide in list_guides:
            if guide[0] == name_of_employee:
                guide_id = guide[1]

        if guide_id == "":
            self.log.warning("Can not find employee in xola guides")
            return False
        return guide_id

    def post_guides_for_event(self, name_of_employee):
        """
        make post request to xola with guid name
        :param name_of_employee: employee name from deputy
        :return: trye if successfully, false if have trables
        """
        guide_id = self.take_guide_id(name_of_employee)
        if guide_id is False:
            return False
        url = self.__url + "events/" + self._event_id + "/guides"
        param = {"id": {"id": guide_id}}
        json_mylist = json.dumps(param)
        data = f"{json_mylist}"
        try:
            response = requests.post(
                url=url, headers=self.__headers, data=data)
            if response.status_code != HTTP_CREATED:
                self.log.error("Can not assigned guides " + response.text)
                return False
            if response.status_code == HTTP_CONFLICT:
                self.log.error(
                    "The guide is already assigned to an overlapping event.")
                return False
            self.log.info("Update successfully sent to XOLA")
            return True

        except requests.RequestException as ex:
            self.log.error("Unable to send get request to XOLA", exc_info=ex)

    @staticmethod
    def calculation_of_employee(shift_count, ticket_count):
        """
        :param shift_count: number max ticket for 1 person
        :param ticket_count: all tickets which reserved in event
        :return: how many new shifts we have to do
        """
        if shift_count == 1:  # we don`t need divine ticket on guids|do 1 shift
            return 1
        if ticket_count < shift_count:  # 20<shift_count<25
            return 1
        return ceil(ticket_count / shift_count)

    @staticmethod
    def convert_time(time):
        """change data and time into UNIX time stamp
        :param time: time format in iso format

        :return: str time
        """
        str_date = datetime.fromisoformat(time).strftime("%Y-%m-%d")
        return str_date
