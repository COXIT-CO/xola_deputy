"""Google class for process data from deputy and post data to google sheets"""
from datetime import datetime

from spreadsheet_api import SpreadsheetAPI
from global_config import compare_mapping, config

START_TIME = " 6:00"  # start time in google sheets
END_TIME = " 23:30"  # end time in google sheets
DELAY = 1800  # in google sheets range 30 minute, so it is in seconds
ONE_DAY_UNIX = 86400  # 1 day in seconds
DELAY_ALL_DAY = 63000  # seconds between first and last cell
DAYS = 30


class GoogleSheetsClient():
    """This is mediator class, where process data and post to google sheets"""
    __spreadsheet_id = ""
    sheets_api = ""

    def __init__(self, deputy, logger):
        self.deputy = deputy
        self.logger = logger

    def init_settings(self):
        """Parser the Settings.ini file, and get parameters for google sheets connection"""
        self.__spreadsheet_id = config['GOOGLE']['spreadsheet_id']
        self.sheets_api = SpreadsheetAPI(self.__spreadsheet_id)

    def change_sheets(self, count_of_days, id_location):
        """
        take shifts from deputy, and minus unavailable employee from cell in google sheets
        :param count_of_days: how many days we process
        :param id_location: location in deputy

        :return: list,with available employee for every time/date cell in google sheets
        """
        date_start, date_end, date_shift = self.date_time()
        number_of_employee = self.deputy.get_number_of_employee(id_location)

        list_of_free_employee = []
        number_of_days = 0

        while number_of_days < count_of_days:
            while date_start <= date_end:
                list_of_free_employee.append([date_start, number_of_employee])
                date_start = date_start + DELAY
            time_of_shits = self.deputy.process_people_unavailability(
                date_shift, id_location)[1]
            self.calculation_unavailability_count(
                time_of_shits, list_of_free_employee)

            date_start, date_end = (date_end - DELAY_ALL_DAY) + \
                ONE_DAY_UNIX, date_end + ONE_DAY_UNIX
            date_shift = datetime.fromtimestamp(
                date_start).strftime('%Y-%m-%d')
            number_of_days += 1

        return list_of_free_employee

    def change_cells(self, start_time, end_time, title):
        """
        change value by -1 in list
        :param start_time: unix time start changed
        :param end_time: unix time end changed
        :param title: title of list in google sheets
        """
        self.sheets_api.change_multiple_ranges_by_value(
            title, start_time, end_time, -1)

    def change_all_spread(self):
        """
        change value of all list in google sheets
        """
        title_of_all_lists = self._get_all_title()
        for title in title_of_all_lists:
            if self.change_specific_spread(title) is False:
                continue

    def change_specific_spread(self, title):
        """
        change value in cell in specific list
        :param title: name of list
        """
        location_id = compare_mapping(title, "title")
        if location_id is False:
            return False
        range_of_values = self.change_sheets(DAYS, location_id["Area"])
        self.sheets_api.change_availability_multiple_ranges(
            title, range_of_values)
        return True

    def _get_all_title(self):
        """
        get all title of list google sheets
        :return: list object with name of title
        """
        all_settings_sheets = self.sheets_api.sheets
        title_of_all_lists = []
        for lists in all_settings_sheets:
            title_of_all_lists.append(lists['properties']['title'])
        return title_of_all_lists

    @staticmethod
    def calculation_unavailability_count(time_of_shits, list_of_free_employee):
        """
        process every cell in google sheets on available employee
        :param time_of_shits: list of lists,with start end end time of shift
        :param list_of_free_employee: list with all available employee
        :return: list with all available employee after minus shifts
        """
        for time_end_start in time_of_shits:
            while time_end_start[0] <= time_end_start[1]:
                for number in list_of_free_employee:
                    if number[0] == time_end_start[0]:
                        number[1] -= 1
                time_end_start[0] += DELAY
        return list_of_free_employee

    @staticmethod
    def date_time():
        """
        take date of today, transform it in unix time and date specific format
        :return: 3 value: unix time(seconds) from today START_TIME
                 and today END_TIME, today in format year-month-day
        """
        date_shift = datetime.now().strftime("%d-%m-%Y")

        str_date = date_shift + START_TIME
        data_unix_start = int(
            datetime.strptime(
                str_date,
                "%d-%m-%Y %H:%M").timestamp())

        str_date = date_shift + END_TIME
        data_unix_end = int(
            datetime.strptime(
                str_date,
                "%d-%m-%Y %H:%M").timestamp())
        date_shift = datetime.now().strftime("%Y-%m-%d")
        return data_unix_start, data_unix_end, date_shift
