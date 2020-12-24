import json
import pytest
from requests.models import Response

from unittest.mock import patch, Mock
from xola_deputy.xola_client import XolaClient
from xola_deputy.logger import LoggerClient

logging = LoggerClient().get_logger()
xola = XolaClient(logging)

@pytest.fixture()
def get_event_json():
    with open("tests/data_event_from_xola.json", "r") as file:
        request = json.load(file)
    return request

@pytest.fixture()
def get_order_json():
    with open("tests/test_response_data.json", "r") as file:
        request = json.load(file)
    return request

@pytest.fixture()
def get_guide_json():
    with open("tests/data_list_of_guide_xola.json", "r") as file:
        request = json.load(file)
    return request

def test_subscribe_to_webhook():
    status_codes = [(200,False),(409,False),(201,True)]
    for status_code in status_codes:
        with patch.object(XolaClient, 'post_request_subscribe_to_webhook', return_value=status_code[0]):
            result = xola.subscribe_to_webhook()
            assert result == status_code[1]

def test_calculation_of_employee():
    assert xola.calculation_of_employee(1,10) == 1
    assert xola.calculation_of_employee(20, 10) == 1
    assert xola.calculation_of_employee(25, 26) == 2
    assert xola.calculation_of_employee(20, 99) == 5

def test_convert_time():
    assert xola.convert_time("2020-12-07T12:55:40+00:00") == "2020-12-07"
    assert xola.convert_time("2020-12-01T10:14:40+00:00") == "2020-12-01"

def test_take_params_from_responce(get_order_json,get_event_json):
    request_order = get_order_json
    with patch.object(XolaClient, '_get_data_from_event',) as mock_func:
        mock_func.return_value = get_event_json
        params, number_shifts, mapping = xola.take_params_from_responce(request_order)
        assert type(params) == dict
        assert type(number_shifts) == int
        assert type(mapping) == dict

def test_start(get_order_json):
    with patch.object(XolaClient, 'take_params_from_responce', return_value= TypeError):
        params, number_shifts, mapping =  xola.start(get_order_json)
        assert params == False
        assert number_shifts == False
        assert mapping == False
    with patch.object(XolaClient, 'take_params_from_responce', return_value= (True,True,True)):
        params, number_shifts, mapping =  xola.start(get_order_json)
        assert params != False
        assert number_shifts != False
        assert mapping != False

def test_get_list_of_guids(get_guide_json):
    with patch.object(XolaClient, '_get_request_list_guides') as mock_func:
        the_response = Mock(spec=Response)
        the_response.json.return_value = get_guide_json
        the_response.status_code = 400
        mock_func.return_value = the_response
        assert xola.get_list_of_guids() == False

    with patch.object(XolaClient, '_get_request_list_guides', ) as mock_func:
        the_response = Mock(spec=Response)
        the_response.json.return_value = get_guide_json
        the_response.status_code = 200
        mock_func.return_value = the_response
        assert type(xola.get_list_of_guids()) == list

def test_take_guide_id():
    with patch.object(XolaClient, 'get_list_of_guids',) as mock_func:
        mock_func.return_value = [('Maaiz - GM Test', '5b5f8e90c481e1e54e8b4571'),
                                  ('Taylor Test', '5b60e68a332e75c36a8b45c1'),
                                  ]
        assert type(xola.take_guide_id('Maaiz - GM Test')) == str
        assert xola.take_guide_id('Maria Test') == False

def test_post_guides_for_event():
    status_codes = [(200, False), (409, False), (201, True)]
    for status_code in status_codes:
        with patch.object(XolaClient, '_post_guides_for_event', return_value=status_code[0]):
            with patch.object(XolaClient, 'take_guide_id', return_value=True):
                result = xola.verification_guides_for_event('Adam Brodner')
                assert result == status_code[1]



