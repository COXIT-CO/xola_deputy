import pickle
import os.path
import configparser

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from datetime import datetime

TOKEN_PATH = 'token.pickle'
CREDENTIALS_PATH = 'credentials.json'

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


class SpreadsheetAPI:
    """
    A class used for work with google spreadsheet

    ...

    Attributes
    ----------
    spreadsheet_id : str
        id of google spreadsheet with which we will work

    spreadsheet__service : googleapiclient.discovery.Resource
        google spreadsheet object

    Methods
    -------
    get_availability(sheet_title, date)
        Get title of sheet in google spreadsheet and date (year, month, day, hour, minutes) in unix format
        Return value from appropriate cell

    change_availability(self, sheet_title, date, value)
        Change value in appropriate cell

    add_sheet(title)
        create new sheet with provided title

    get_sheet_by_title(title)
        return sheet object

    _get_cell_indexes_by_timestamp(sheet_title, date)
        convert date to str format and looking for index of cell in spreadsheet

    _create_range_name(sheet_title, row_id, column_id)
        create range name which using in google api

    _read_date(range_name)
        Read data from spreadsheet using range name

    _update_date(range_name, value)
        Update value in cell of spreadsheet using range name
    """

    def __init__(self):
        """
        Parameters
        ----------
        spreadsheet_id : str
            Id of google spreadsheet

        ----------

        Init function looking for token with TOKEN_PATH,
        if token doesn't exist or expired - user need to authenticate in google services
        after it function create google spreadsheet object, using provided id and save it

        """
        creds = None
        config = configparser.ConfigParser()
        config.read('Settings.ini')
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(TOKEN_PATH):
            with open(TOKEN_PATH, 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(port=8000)
            # Save the credentials for the next run
            with open(TOKEN_PATH, 'wb') as token:
                pickle.dump(creds, token)

        # self.service = build('sheets', 'v4', credentials=creds)
        self.spreadsheet_service = build('sheets', 'v4', credentials=creds).spreadsheets()
        self.spreadsheet_id = config['GOOGLE']['spreadsheet_id']

        values = self._read_data(self.spreadsheet_service.get(
            spreadsheetId=self.spreadsheet_id
        ).execute().get('sheets', '')[0]['properties']['title'] + '!A1:ZZZ1000')

        self.time_values = values[0]
        self.date_values = [i[0] for i in values]

    @property
    def sheets(self):
        """
        Property
        Return all sheet objects in spreadsheet
        """
        return self.spreadsheet_service.get(spreadsheetId=self.spreadsheet_id).execute().get('sheets', '')

    def get_availability(self, sheet_title, date):
        """
        Parameters
        ----------
        sheet_title : str
            Title of sheet
        date : int
           Date in unix format

        ----------

        Function takes date in unix format convert it into 2 string variables
        After it looking for cell in sheet with provided title, using converted date variables
        In the end function return value from cell in sheet

        Return value from cell if date is valid, in another case - return None
        """
        time_index, date_index = self._get_cell_indexes_by_timestamp(sheet_title, date)
        range_name = self._create_range_name(sheet_title, time_index, date_index)

        if range_name is None:
            return None

        result = self._read_data(range_name)
        if result is None:
            return 0
        else:
            return result[0][0]

    def change_availability(self, sheet_title, date, value):
        """
        Parameters
        ----------
        sheet_title : str
            Title of sheet
        date : int
           Date in unix format
        value : str
            Value which will be insert into sheet

        ----------

        Function looking for cell in sheet and insert new value to this cell
        Return value of cell if date is valid, in another case - return None
        """

        time_index, date_index = self._get_cell_indexes_by_timestamp(sheet_title, date)
        range_name = self._create_range_name(sheet_title, time_index, date_index)

        if range_name is None:
            return None

        return self._update_data(range_name, value)

    def change_availability_by_value(self, sheet_title, date, value):
        """
        Parameters
        ----------
        sheet_title : str
            Title of sheet
        date : int
           Date in unix format
        value : int
            Change current value by this value

        ----------

        Function looking for cell in sheet and change it by new value
        Return value of cell if date is valid, in another case - return None
        """
        try:
            old_value = int(self.get_availability(sheet_title, date))
            new_value = old_value + value
        except ValueError as e:
            return None

        return self.change_availability(sheet_title, date, new_value)

    def add_sheet(self, title):
        """
        Parameters
        ----------
        title : str
            Title of sheet

        ----------

        Try to add new sheet to the spreadsheet
        Return new sheet object if sheet was added or None if this sheet is exist
        """

        try:
            result = self.spreadsheet_service.batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=
                {
                    "requests": [
                        {
                            "addSheet": {
                                "properties": {
                                    "title": title,
                                }
                            }
                        }
                    ]
                }).execute()

            return result
        except HttpError as e:
            return None

    def get_sheet_by_title(self, title):
        """
        Parameters
        ----------
        title : str
           Title of sheet

        ----------

        Looking for sheet with provided title in the spreadsheet
        If sheet isn't exist - create new sheet with provided title
        """
        for sheet in self.sheets:
            if sheet['properties']['title'] == title:
                result = sheet
                break
        else:
            result = self.add_sheet(title)

        return result

    def _get_cell_indexes_by_timestamp(self, sheet_title, date):
        """
        Parameters
        ----------
        sheet_title : str
          Title of sheet
        date: int
            Time in unix format
        ----------

        Convert time into 2 string variables, looking for cell in sheet using this variables
        Return int indexes of row and column of cell in sheet
        """

        spreadsheet_date = datetime.fromtimestamp(date).strftime('%A, %B %-d, %Y')
        spreadsheet_time = datetime.fromtimestamp(date).strftime('%-I:%M %p')

        time_index, date_index = 0, 0
        for index, time in enumerate(self.time_values, 1):

            if time == spreadsheet_time:
                time_index = index
                break

        for index, date in enumerate(self.date_values, 1):
            if date == spreadsheet_date:
                date_index = index
                break

        return time_index, date_index

    @staticmethod
    def _create_range_name(sheet_title, row_id, column_id):
        """
        Parameters
        ----------
        sheet_title : str
          Title of sheet
        row_id: int
            Integer index of row
        column_id: int
            Integer index of column

        ----------

        Create range name of cell in google spreadsheet format, using row and column indexes
        Return string range_name
        """
        letter = ''
        while row_id > 0:
            temp = (row_id - 1) % 26

            letter = chr(temp + 65) + letter
            row_id = (row_id - temp - 1) // 26

        if not letter:
            return None

        return sheet_title + '!' + letter + str(column_id)

    def _read_data(self, range_name):
        """
        Parameters
        ----------
        range_name : str
            Google spreadsheet range name in str format

        ----------

        Read data from cell, using provided range_name
        return result in format [[value]]
        """
        result = self.spreadsheet_service.values().get(
            spreadsheetId=self.spreadsheet_id, range=range_name).execute()
        rows = result.get('values')
        return rows

    def _update_data(self, range_name, value):
        """
        Parameters
        ----------
        range_name : str
            Google spreadsheet range name in str format

        value : str
            Insert this value into cell
        ----------

        Insert value into cell, using provided range_name
        return result in format [[value]]
        """
        value_body = {
            "values": [[value]]
        }

        result = self.spreadsheet_service.values().update(
            spreadsheetId=self.spreadsheet_id, range=range_name, valueInputOption='RAW',
            body=value_body).execute()
        rows = result.get('values')
        return rows

    def change_availability_multiple_ranges(self, sheet_title, data_list):
        """
        Parameters
        ----------
        sheet_title : str
          Title of sheet
        data_list: list
            List contains tuples with date and value for cell
            Example: [[1607414400, 1], [1607416200, 2]]
        ----------

        Create range names for each time from data_list,
        make request for writing all values to a spreadsheet by their range names
        """
        spreadsheet_request_values = []
        for data_item in data_list:
            date = data_item[0]
            value = data_item[1]

            time_index, date_index = self._get_cell_indexes_by_timestamp(sheet_title, date)
            range_name = self._create_range_name(sheet_title, time_index, date_index)
            if range_name is None:
                continue

            spreadsheet_request_values.append(
                {
                    "range": range_name,
                    "values": [[value]]
                }
            )

        self._batch_update_data(spreadsheet_request_values)

        return True

    def _batch_update_data(self, request_values):
        """
        Parameters
        ----------

        request_values : list of dict
            list of dictionaries, which contain range name and value
        ----------

        Send request batchUpdate to google spreadsheet API for updating batch of data
        """
        body = {
            'valueInputOption': 'RAW',
            'data': request_values
        }
        result = self.spreadsheet_service.values().batchUpdate(
            spreadsheetId=self.spreadsheet_id, body=body).execute()
        rows = result.get('values')
        return rows

