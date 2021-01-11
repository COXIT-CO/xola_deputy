import pytest
from unittest.mock import patch, Mock

from xola_deputy.deputy_client import DeputyClient
from xola_deputy.logger import LoggerClient
from xola_deputy.google_sheets_client import GoogleSheetsClient


logging = LoggerClient().get_logger()
deputy = DeputyClient(logging)
sheets = GoogleSheetsClient(deputy,logging)

def test_date_time():
    assert sheets.date_time()

def test_calculation_unavailability_count():
    time_of_shits =  [[1608641235, 1608641735], [1608641238, 1608641738]]
    list_of_free_employee = [[1608609600, 4], [1608611400, 4], [1608613200, 4]]
    assert sheets.calculation_unavailability_count(time_of_shits,list_of_free_employee)

def test_change_sheets():
    with patch.object(DeputyClient, 'get_number_of_employee', return_value=4):
        with patch.object(DeputyClient, 'process_people_unavailability', return_value=[[1608641235, 1608641735], [1608641238, 1608641738]]):
            with patch.object(GoogleSheetsClient, 'calculation_unavailability_count', return_value=True):
                assert sheets.change_sheets(3,1)
