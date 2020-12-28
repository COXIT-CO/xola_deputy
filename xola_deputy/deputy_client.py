""""`Have class DeputyCLient,which connect to deputy API and get/post data from here"""
import json
from collections import Counter

import requests
from global_config import compare_mapping, config

HTTP_SUCCESS = 200


class DeputyClient():
    """"Connect to Deputy API"""
    __headers = {}
    __url = ""
    __public_url = ""

    def __init__(self, logger):
        self.log = logger

    def init_settings(self):
        """Parser the Settings.ini file, and get parameters for deputy api connection"""
        deputy_access_token, deputy_id = config["DEPUTY"]["deputy_access_token"], \
            config["DEPUTY"]["deputy_id"]
        self.__headers = {
            'Authorization': 'OAuth ' + deputy_access_token,
        }
        self.__url = 'https://' + deputy_id + '/api/v1/'
        self.__public_url = config['URL']['public_url']

    def _post_new_shift(self, params_for_deputy):
        data = self.update_params_for_post_deputy_style(params_for_deputy)
        url = self.__url + 'supervise/roster/'
        try:
            response = requests.post(
                url=url, headers=self.__headers, data=data)
            return response.json()
        except requests.RequestException as ex:
            self.log.error(
                "Unable to send post request to DEPUTY",
                exc_info=ex)

    def process_data_from_new_shift(self, params_for_deputy=None):
        """post a new shift
        :param params_for_deputy: data to post request
        :return: str. id shift, and correct date
        """
        try:
            response = self._post_new_shift(params_for_deputy)
            return str(response["Id"]), response["Date"]
        except (TypeError, KeyError):
            self.log.warning(
                "Can not find availability employee",)
            return False, False

    def _get_people_unavailability(self, date, id_location):
        url = self.__url + 'supervise/roster/' + date + "/" + id_location
        try:
            response = requests.get(url=url, headers=self.__headers, )
            return response.json()
        except requests.RequestException as ex:
            self.log.error(
                "Unable to send post request to DEPUTY",
                exc_info=ex)

    def process_people_unavailability(self, date, id_location):
        """MAke post request , take all shifts,and search which people have a work
        :param data: in which data we looking for shift
        :return: list of unavailable employee
        """
        unavailable_employee = []
        unavailable_time = []
        try:
            response = self._get_people_unavailability(date, id_location)
            for shift in response:
                unavailable_time.append([shift["StartTime"], shift["EndTime"]])
                if shift["_DPMetaData"]["EmployeeInfo"]:
                    unavailable_employee.append(
                        str(shift["_DPMetaData"]["EmployeeInfo"]["Id"]))
            return unavailable_employee, unavailable_time
        except (ValueError, TypeError):
            self.log.error("Bad JSON data")
            return False

    def _get_recomendation(self, shift_id):
        url = self.__url + 'supervise/getrecommendation/' + shift_id
        try:
            response = requests.get(url=url, headers=self.__headers, )
            return response.json()
        except requests.RequestException as ex:
            self.log.error(
                "Unable to send post request to DEPUTY",
                exc_info=ex)

    def get_people_availability(self, shift_id, unavi_employee):
        """Take id employee,which can work in taken shift
        :param shift_id: id shift ,which have not employee
        :return: id free employeee
        """
        try:
            response = self._get_recomendation(shift_id)

            free_employee = list(response["trained"])
            unavilability_employee = list(response["unavailable"])
            free_employee = list(
                set(free_employee) -
                set(unavilability_employee))

            if not unavi_employee:  # check if we have all employee free
                return free_employee[0]

            # do we have people who don`t work?
            employees = list(set(free_employee) - set(unavi_employee))
            if not employees:  # no, all people have a work
                return self.check_all_job_employee(unavi_employee)
            return employees[0]

        except (TypeError, IndexError):
            self.log.warning("Not Available employee")
            return False

    def get_employee_name(self, id_employee):
        """
        make get request to deputy,take employee name
        :param employee_id:
        :return: name of employee
        """
        url = self.__url + 'supervise/employee/' + id_employee
        try:
            response = requests.get(url=url, headers=self.__headers, )
            return response.json()["DisplayName"], response.status_code
        except KeyError:
            self.log.warning("Can not find employee with transferred id")
            return False
        except requests.RequestException as ex:
            self.log.error(
                "Unable to send post request to DEPUTY",
                exc_info=ex)
            return False

    def _get_request_for_employee_unvail(self):
        url = self.__url + 'supervise/unavail/'
        try:
            response = requests.get(url=url, headers=self.__headers, )
            return response.json()
        except requests.RequestException as ex:
            self.log.error(
                "Unable to send post request to DEPUTY",
                exc_info=ex)

    def get_employee_unavail(self):
        """
         make get request to deputy,take employee unavailability
        :return: when employee have unavailability
        """
        response = self._get_request_for_employee_unvail()
        if not response:
            return False
        list_of_em = []
        for employee in response:
            employee_id = str(employee["Employee"])
            title = self._get_area_for_employee(employee_id)
            if title is False:
                return False
            list_of_em.append(
                (employee["StartTime"], employee["EndTime"], title))

        return list_of_em

    def post_params_for_webhook(self, topic, address):
        """
        make post request to deputy for webhook
        :param topic: what we waiting
        :param address: where data come
        :return: status code of response
        """
        params_for_webhooks = {
            "Topic": topic,
            "Enabled": 1,
            "Type": "URL",
            "Address": self.__public_url + address
        }
        url = self.__url + 'resource/Webhook'
        data = self.update_params_for_post_deputy_style(params_for_webhooks)
        try:
            response = requests.post(url=url, headers=self.__headers, data=data)
            return response.status_code
        except requests.RequestException as ex:
            self.log.error(
                "Unable to send post request to DEPUTY",
                exc_info=ex)

    def subscribe_to_webhooks(self):
        """
        make 3 post request for subscribe webhooks
        :return: true if all good
        """
        data_for_webhooks = [
            ("Employee.Delete",
             "/delete_employee"),
            ("Employee.Insert",
             "/insert_employee"),
            ("EmployeeAvailability.Insert",
             "/unvial_employee")]
        if self._verification_webhooks(data_for_webhooks) is False:
            self.log.warning("You already subscribe to webhooks")
            return False
        for data in data_for_webhooks:
            if self.post_params_for_webhook(data[0], data[1]) != HTTP_SUCCESS:
                return False
        return True

    def _verification_webhooks(self, data_for_webhooks):
        """
        make verification , if user already subscribe to webhooks
        :param data_for_webhooks: list of tuple with topic webhook
        :return: bool, false already subscribe , true make post request
        """
        url = self.__url + 'resource/Webhook'
        try:
            response = requests.get(url=url, headers=self.__headers, )
            for webhook in response.json():
                for data in data_for_webhooks:
                    if webhook["Topic"] == data[0]:
                        return False
            return True
        except requests.RequestException as ex:
            self.log.error(
                "Unable to send post request to DEPUTY",
                exc_info=ex)

    def get_number_of_employee(self, id_location):
        """make GET request to DEPUTY,for all employee
        :return: count of employee
        """
        url = self.__url + 'supervise/employee'
        try:
            response = requests.get(url=url, headers=self.__headers, )
            count = 0
            for employee in response.json():
                if employee["Company"] == int(id_location):
                    count += 1
            return count
        except requests.RequestException as ex:
            self.log.error(
                "Unable to send post request to DEPUTY",
                exc_info=ex)

    def _get_request_employee(self, employee_id):
        try:
            url = self.__url + 'supervise/employee/' + employee_id
            response = requests.get(url=url, headers=self.__headers, )
            return response.json()
        except requests.RequestException as ex:
            self.log.error(
                "Unable to send post request to DEPUTY",
                exc_info=ex)

    def _get_area_for_employee(self, employee_id):
        response = self._get_request_employee(employee_id)
        area_id = str(response["Company"])
        title = compare_mapping(area_id, "area")
        if title is False:
            return False
        return title["Possible Area Nicknames in Production"]

    @staticmethod
    def update_params_for_post_deputy_style(params):
        """
        take python dict and change it for json stringify format
        :param params: python dict
        :return: json stringify
        """
        json_mylist = json.dumps(params)
        data = f"{json_mylist}"
        return data

    @staticmethod
    def check_all_job_employee(unavailable_employee):
        """
        create dictionary where take e less worked employee
        :param unavailable_employee:
        :return: employee who have a less work
        """
        job_employees = Counter()
        for job in unavailable_employee:
            job_employees[job] += 1
        return (job_employees.most_common()[-1])[0]
