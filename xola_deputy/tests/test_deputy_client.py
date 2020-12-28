import pytest
import json
import requests
from unittest.mock import patch

from xola_deputy.deputy_client import DeputyClient
from xola_deputy.logger import LoggerClient

logging = LoggerClient().get_logger()
deputy = DeputyClient(logging)

@pytest.fixture()
def get_shift_json():
    with open("tests/data_from_post_new_shift_deputy.json", "r") as file:
        request = json.load(file)
    return request

@pytest.fixture()
def get_unvial_json():
    with open("tests/data_from_unvial_deputy.json", "r") as file:
        request = json.load(file)
    return request

@pytest.fixture()
def get_recomendation_json():
    with open("tests/data_recomendation_deputy.json", "r") as file:
        request = json.load(file)
    return request

@pytest.fixture()
def get_dayoff_json():
    with open("tests/data_unvial_employee_deputy.json", "r") as file:
        request = json.load(file)
    return request

@pytest.fixture()
def get_employee_json():
    with open("tests/data_emplloyee_info_deputy.json", "r") as file:
        request = json.load(file)
    return request

def test_process_data_from_new_shift(get_shift_json):
    with patch.object(DeputyClient, '_post_new_shift') as mock_func:
        mock_func.return_value = get_shift_json
        params = {
            "intStartTimestamp": 1234,
            "intEndTimestamp": 1243,
            "intOpunitId": 3,
        }
        assert deputy.process_data_from_new_shift(params)

    with patch.object(DeputyClient, '_post_new_shift', return_value=KeyError):
        params = {
            "intStartTimestamp": 1234,
            "intEndTimestamp": 1243,
            "intOpunitId": 3,
        }
        assert deputy.process_data_from_new_shift(params)

def test_process_people_unavailability(get_unvial_json):
    with patch.object(DeputyClient, '_get_people_unavailability') as mock_func:
        mock_func.return_value = get_unvial_json
        assert deputy.process_people_unavailability("2020-12-17","1")

    with patch.object(DeputyClient, '_get_people_unavailability', return_value=ValueError):
        assert deputy.process_people_unavailability("2020-12-17", "1") == False

def test_get_people_availability(get_recomendation_json):
    with patch.object(DeputyClient, '_get_recomendation') as mock_func:
        mock_func.return_value = get_recomendation_json
        test_unvi = []
        assert deputy.get_people_availability("49",test_unvi)
    with patch.object(DeputyClient, '_get_recomendation') as mock_func:
        mock_func.return_value = get_recomendation_json
        test_unvi = [1,2,3]
        assert deputy.get_people_availability("49", test_unvi)
    with patch.object(DeputyClient, '_get_recomendation') as mock_func:
        get_recomendation_json["trained"] = {}
        mock_func.return_value = get_recomendation_json
        test_unvi = [1,2,3]
        assert deputy.get_people_availability("49", test_unvi)
    with patch.object(DeputyClient, '_get_recomendation', return_value=IndexError):
        mock_func.return_value = get_recomendation_json
        test_unvi = [1,2,3]
        assert deputy.get_people_availability("49", test_unvi) == False

def test_check_all_job_employee():
    unavailable_employee = [1,2,2,3,4,5,6,3,4,5,6,7]
    assert deputy.check_all_job_employee(unavailable_employee) == 7

def test_update_params_for_post_deputy_style():
    test_param={"test":1}
    data = deputy.update_params_for_post_deputy_style(test_param)
    assert type(data) == str

def test_get_employee_unavail(get_dayoff_json):
    with patch.object(DeputyClient, '_get_request_for_employee_unvail') as mock_func:
        mock_func.return_value = []
        assert deputy.get_employee_unavail() == False

    with patch.object(DeputyClient, '_get_request_for_employee_unvail') as mock_func:
        mock_func.return_value = get_dayoff_json
        with patch.object(DeputyClient, '_get_area_for_employee',return_value = "Aliens"):
            assert deputy.get_employee_unavail()
    with patch.object(DeputyClient, '_get_request_for_employee_unvail') as mock_func:
        mock_func.return_value = get_dayoff_json
        with patch.object(DeputyClient, '_get_area_for_employee', return_value= False):
            assert deputy.get_employee_unavail() == False

def test_subscribe_to_webhooks():
    with patch.object(DeputyClient, '_verification_webhooks', return_value=False):
        assert deputy.subscribe_to_webhooks() == False

    with patch.object(DeputyClient, '_verification_webhooks', return_value=True):
        with patch.object(DeputyClient, 'post_params_for_webhook', return_value= 201):
            assert deputy.subscribe_to_webhooks() == False

    with patch.object(DeputyClient, '_verification_webhooks', return_value=True):
        with patch.object(DeputyClient, 'post_params_for_webhook', return_value= 200):
            assert deputy.subscribe_to_webhooks() == True

def test_get_area_for_employee(get_employee_json):
    with patch.object(DeputyClient, '_get_request_employee') as mock_func:
        mock_func.return_value = get_employee_json
        assert deputy._get_area_for_employee("1")

@pytest.mark.xfail(raises=requests.RequestException)
def test_post_new_shift():
    params = {
        "intStartTimestamp": 1234,
        "intEndTimestamp": 1243,
        "intOpunitId": 3,
    }
    deputy._post_new_shift(params)

@pytest.mark.xfail(raises=requests.RequestException)
def test_get_people_unavailability():
    deputy._get_people_unavailability("2020-12-12","1")

@pytest.mark.xfail(raises=requests.RequestException)
def test_get_recomendation():
    deputy._get_recomendation("1")

@pytest.mark.xfail(raises=requests.RequestException)
def test_get_employee_name():
    deputy.get_employee_name("1")

@pytest.mark.xfail(raises=requests.RequestException)
def test_get_request_for_employee_unvail():
    deputy._get_request_for_employee_unvail()

@pytest.mark.xfail(raises=requests.RequestException)
def test_get_request_employee():
    deputy._get_request_employee("1")

@pytest.mark.xfail(raises=requests.RequestException)
def test_verification_webhooks():
    deputy._verification_webhooks("1")

@pytest.mark.xfail(raises=requests.RequestException)
def test_post_params_for_webhook():
    deputy.post_params_for_webhook("Aliens", "url")

@pytest.mark.xfail(raises=requests.RequestException)
def test_get_number_of_employee():
    deputy.get_number_of_employee("1")





