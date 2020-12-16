# Take time pf shifts from DEPUTY and post all free employee in GOOGLE SHEETS
from xola_deputy import deputy, sheets
from datetime import datetime

START_TIME = " 6:00"  # start time in google sheets
END_TIME = " 23:30"  # end time in google sheets
DELAY = 1800  # in google sheets range 30 minute, so it is in seconds
ONE_DAY_UNIX = 86400  # 1 day in seconds
DELAY_ALL_DAY = 63000  # seconds between first and last cell


def date_time():
    """
    take date of today, transform it in unix time and date specific format
    :return: 3 value: unix time(seconds) from today START_TIME and today END_TIME, today in format year-month-day
    """
    date_shift = datetime.now().strftime("%d-%m-%Y")

    str_date = date_shift[-2:] + START_TIME
    data_unix_start = int(
        datetime.strptime(
            str_date,
            "%d-%m-%y %H:%M").timestamp())

    str_date = date_shift[-2:] + END_TIME
    data_unix_end = int(
        datetime.strptime(
            str_date,
            "%d-%m-%y %H:%M").timestamp())
    date_shift = datetime.now().strftime("%Y-%m-%d")
    return data_unix_start, data_unix_end, date_shift


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


def change_sheets(count_of_days, id_location):
    """
    take shifts from deputy, and minus unavailable employee from cell in google sheets
    :param count_of_days: how many days we process
    :return: list,with available employee for every time/date cell in google sheets
    """
    # TODO location
    date_start, date_end, date_shift = date_time()
    number_of_employee = deputy.get_number_of_employee()

    list_of_free_employee = []
    number_of_days = 0

    while number_of_days < count_of_days:
        while date_start <= date_end:
            list_of_free_employee.append([date_start, number_of_employee])
            date_start = date_start + DELAY
        time_of_shits = deputy.get_people_unavailability(date_shift, id_location )[1]

        calculation_unavailability_count(time_of_shits, list_of_free_employee)

        date_start, date_end = (date_end - DELAY_ALL_DAY) + \
            ONE_DAY_UNIX, date_end + ONE_DAY_UNIX
        date_shift = datetime.fromtimestamp(date_start).strftime('%Y-%m-%d')
        number_of_days += 1

    return list_of_free_employee
