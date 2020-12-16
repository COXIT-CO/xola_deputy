"""Main script which start all logic. Here we have 2 webhooks,
and process date from request from XOLA and DEPUTY"""
from datetime import datetime
from flask import Flask, request, Response
from xola_client import XolaClient
from deputy_client import DeputyClient
from logger import LoggerClient
from spreadsheet_api import SpreadsheetAPI

app = Flask(__name__)
logging = LoggerClient().get_logger()
xola = XolaClient(logging)
deputy = DeputyClient(logging)
sheets = SpreadsheetAPI()


@app.route("/xola", methods=['POST'])
def xola_deputy_run():
    """Take response from xola notification about order.
        Create parameters for deputy POST request with data from XOLA.
        Post new shift with this parameters , and check which employee free.
        :return: code 200 is all good, code 500 - arose problem
    """
    params, number_shifts, mapping = xola.start(request.json)
    if params is False:
        return Response(status=500)
    for _ in range(number_shifts):
        # first time we created shift in open block
        id_shift, date_shift = deputy.post_new_shift(params)

        date_shift_unix, date_shift = xola.convert_time(date_shift)
        id_location = int(mapping["Area"])
        title = mapping['Possible Area Nicknames in Production']
        unavailable_employee = deputy.get_people_unavailability(
            date_shift, id_location)[0]  # check who have a work
        id_employee = deputy.get_people_availability(
            id_shift, unavailable_employee)
        if id_employee is False:
            return Response(status=500)# think if we sometime have this situation
        params.update({
            "intRosterId": id_shift,
            "intRosterEmployee": id_employee
        })
        deputy.post_new_shift(params)  # post shift for employee

        name_of_employee = deputy.get_employee_name(id_employee)
        if name_of_employee is False:
            return Response(status=500)
        if xola.post_guides_for_event(name_of_employee) is False:
            return Response(status=500)
        sheets.change_availability_by_value(title, date_shift_unix, -1)

    logging.info("Successfully post shift, guides, employee ")

    return Response(status=200)

@app.route("/delete_employee", methods=['POST'])
def deputy_delet():
    sheets.change_availability_by_value("Aliens",1607601600,-1)
    return Response(status=200)

@app.route("/insert_employee", methods=['POST'])
def deputy_insert():
    # TODO:post plus number in google shift
    print(request.json)
    return Response(status=200)

@app.route("/unvial_employee", methods=['POST'])
def deputy_unvial():
    list_of_unvial = deputy.get_employee_unavail()#list of (timestar,timeend) unix
    if list_of_unvial is False:
        return Response(status=500)
    sheets.change_availability_by_value("Aliens",1607601600,-1)
    return Response(status=200)

if __name__ == '__main__':
    #move to setup
    if xola.subscribe_to_webhook() is False:
        logging.warning("Can not subscribe to webhook")
    deputy.subscribe_to_webhooks()
    app.run(host="0.0.0.0", port=5000)
