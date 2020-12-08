""""`Have class DeputyCLient,which connect to deputy API and get/post data from here"""
import json
import configparser
from collections import Counter

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
        :param params_for_deputy: data to post request
        :return: str. id shift, and correct date
        """
        json_mylist = json.dumps(params_for_deputy)
        data = f"{json_mylist}"
        url = self.__url + 'supervise/roster/'
        try:
            response = requests.post(
                url=url, headers=self.__headers, data=data)
            return str(response.json()["Id"]), response.json()["Date"]
        except KeyError as ex:
            self.log.warning(
                "Bad area id",
                exc_info=ex)
        except requests.RequestException as ex:
            self.log.error(
                "Unable to send post request to DEPUTY",
                exc_info=ex)

    def get_people_unavailability(self, data):
        """MAke post request , take all shifts,and search which people have a work
        :param data: in which data we looking for shift
        :return: list of unavailable employee
        """
        url = self.__url + 'supervise/roster/' + data
        unavailable_employee = []
        try:

            response = requests.get(url=url, headers=self.__headers,)
            for shift in response.json():
                if shift["_DPMetaData"]["EmployeeInfo"]:
                    unavailable_employee.append(
                        str(shift["_DPMetaData"]["EmployeeInfo"]["Id"]))
            return unavailable_employee

        except requests.RequestException as ex:
            self.log.error(
                "Unable to send post request to DEPUTY",
                exc_info=ex)
        except (ValueError, TypeError):
            self.log.error("Bad JSON data")

    def get_people_availability(self, shift_id, unavi_employee):
        """Take id employee,which can work in taken shift
        :param shift_id: id shift ,which have not employee
        :return: id free employeee
        """
        url = self.__url + 'supervise/getrecommendation/' + shift_id
        try:
            response = requests.get(url=url, headers=self.__headers,)

            free_employee = list(response.json()["trained"])

            if not unavi_employee:  # check if we have all employee free
                return free_employee[0]

            # do we have people who don`t work?
            employees = list(set(free_employee) - set(unavi_employee))
            if not employees:  # no, all people have a work
                return self.check_all_job_employee(unavi_employee)
            return employees[0]

        except IndexError:
            self.log.warning("Not Available employee")
        except requests.RequestException as ex:
            self.log.error(
                "Unable to send post request to DEPUTY",
                exc_info=ex)

    def get_employee_name(self, id_employee):
        """
        make get request to deputy,take employee name
        :param employee_id:
        :return: name of employee
        """
        url = self.__url + 'supervise/employee/' + id_employee
        try:
            response = requests.get(url=url, headers=self.__headers, )
            return response.json()["DisplayName"]
        except requests.RequestException as ex:
            self.log.error(
                "Unable to send post request to DEPUTY",
                exc_info=ex)

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
