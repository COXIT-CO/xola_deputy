import json
import requests

from xola_deputy.xola_deputy import xola

def test_take_params_from_responce():

    assert xola.calculation_of_guids(1,10) == 1
    assert xola.calculation_of_guids(20, 10) == 1
    assert xola.calculation_of_guids(25, 26) == 2
    assert xola.calculation_of_guids(20, 99) == 5

def test_convert_time():
    assert xola.convert_time("2020-12-07T12:55:40+00:00") == 1607345740
    assert xola.convert_time("2020-12-01T10:14:40+00:00") == 1606817680

def test_subscribe_to_webhook():
    assert xola.subscribe_to_webhook() == False
    assert xola.subscribe_to_webhook("experience.create") == False
    assert xola.subscribe_to_webhook("installation.delete") == True

def test_get_data_from_event():
    assert xola.get_data_from_event("5fc69bb3572e05b862364adf") == requests.Response

def test_start():
    with open("tests/test_response_data.json", "r") as file:
        requst =json.load(file)
    assert type(xola.start(requst)[0]) == dict
