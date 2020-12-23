import pytest
import json
from unittest.mock import patch, Mock
import requests

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





