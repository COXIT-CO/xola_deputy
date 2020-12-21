from datetime import datetime
import requests
import pytest

from xola_deputy.deputy_client import DeputyClient
from xola_deputy.logger import LoggerClient

logging = LoggerClient().get_logger()
deputy = DeputyClient(logging)

@pytest.fixture()
def get_id_shift():
    now = int(datetime.now().timestamp())
    now_next = now + 500
    test_params = {
        "intStartTimestamp": now,
        "intEndTimestamp": now_next,
        "intOpunitId": 3,
    }
    id_shift, date_shift = deputy.post_new_shift(test_params)
    return id_shift

def test_post_new_shift(get_id_shift):
    id_shift = get_id_shift
    assert type(id_shift) == str

def test_get_people_unavailability():
    now = (datetime.now().strftime("%Y-%m-%d"))
    unavailable_employee, unavailable_time = deputy.get_people_unavailability(now,"1")
    assert unavailable_employee != False

def test_get_people_availability(get_id_shift):
    id_shift = str(get_id_shift)
    unavailable_employee_1 = [1,2,3,4,5,6,7]
    id_employee_1 = deputy.get_people_availability(
        id_shift, unavailable_employee_1)
    unavailable_employee_1 = [1, 2, 3,]
    id_employee_2 = deputy.get_people_availability(
        id_shift, unavailable_employee_1)
    unavailable_employee_1 = []
    id_employee_3 = deputy.get_people_availability(
        id_shift, unavailable_employee_1)
    assert type(id_employee_1) == str
    assert type(id_employee_2) == str
    assert type(id_employee_3) == str


def test_get_employee_name():
    assert deputy.get_employee_name("1")[1] == 200
    assert deputy.get_employee_name("11") == False

def test_check_all_job_employee():
    unavailable_employee = [1,2,2,3,4,5,6,3,4,5,6,7]
    assert deputy.check_all_job_employee(unavailable_employee) == 7







