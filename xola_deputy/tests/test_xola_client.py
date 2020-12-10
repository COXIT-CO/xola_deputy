import json
import requests
import pytest
from xola_deputy import xola

def test_take_params_from_responce():

    assert xola.calculation_of_employee(1,10) == 1
    assert xola.calculation_of_employee(20, 10) == 1
    assert xola.calculation_of_employee(25, 26) == 2
    assert xola.calculation_of_employee(20, 99) == 5

def test_convert_time():
    assert xola.convert_time("2020-12-07T12:55:40+00:00") == 1607345740
    assert xola.convert_time("2020-12-01T10:14:40+00:00") == 1606817680

def test_subscribe_to_webhook():
    bool_status = xola.subscribe_to_webhook("installation.delete")

    url = "https://xola.com/api/users/5fbe98dc59b3ed24da1e656d/hooks"
    headers = {
        'X-API-KEY': "57YSBIlN_U29-NQmfAsp2xw04_LZkzfemv5o-rCgYO0"
    }
    response = requests.get(url=url, headers=headers)
    id_hooks = ""
    for hook in response.json()["data"]:
        if hook["eventName"] == "installation.delete":
            id_hooks = hook["id"]
    url = "https://xola.com/api/users/5fbe98dc59b3ed24da1e656d/hooks/"+ id_hooks
    requests.delete(url=url, headers=headers)

    assert bool_status == True
    assert xola.subscribe_to_webhook() == False
    assert xola.subscribe_to_webhook("experience.create") == False


def test_get_data_from_event():
    xola._event_id = "5fc69bb3572e05b862364adf"
    response = xola.get_data_from_event()
    assert response.status_code == 200

def test_start():
    with open("tests/test_response_data.json", "r") as file:
        requst =json.load(file)

    assert type(xola.start(requst)[0]) == dict

def test_take_guide_id():
    name = "Alyssa Hebrio"
    id_guides = "5b96b44ac681e166358b4602"
    test_id = xola.take_guide_id(name)
    assert test_id == id_guides
    name = "Vi VI"
    test_id = xola.take_guide_id(name)
    assert test_id == False

def test_compare_experience_and_area():
    exp_id = "5b58a24fc4341e1a2168b456a"
    assert xola.compare_experience_and_area(exp_id) == False
    exp_id = "5b58a277c381e1a3328b4572"
    assert xola.compare_experience_and_area(exp_id) != False

def test_post_guides_for_event():
    assert xola.post_guides_for_event("Gavin Lovett") == False


"""@patch('xola_client.XolaClient.subscribe_to_webhook', return_value=True)
def test_subscribe_to_webhook(subscribe_to_webhook):
    assert subscribe_to_webhook() == True


@patch('xola_client.XolaClient.get_data_from_event', return_value = requests.Response)
def test_get_data_from_event(get_data_from_event):
    assert get_data_from_event() == requests.Response
"""