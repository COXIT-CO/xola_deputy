"""Main script which start all logic. Here we have 2 webhooks,
and process date from request from XOLA and DEPUTY"""
from datetime import datetime
from flask import Flask, request, Response
from xola_client import XolaClient
from deputy_client import DeputyClient
from logger import LoggerClient
from spreadsheet_api import SpreadsheetAPI

app = Flask(__name__)
logger = LoggerClient().get_logger()
xola = XolaClient(logger)
deputy = DeputyClient(logger)
sheets = SpreadsheetAPI("15CK9uoirlxXaVVbbsTWtW8JbjglusqArqvtaMDdn_YM")


@app.route("/xola", methods=['POST'])
def xola_webhook():
    """Take response from xola notification about order.
        Create parameters for deputy POST request with data from XOLA.
        Post new shift with this parameters , and check which employee free.
        :return: code 200 is all good, code 500 - arose problem
    """
    params, number_shifts, title = xola.start(request.json)
    if params is False:
        return Response(status=500)
    for _ in range(number_shifts):
        # first time we created shift in open block
        id_shift, date_shift,  = deputy.post_new_shift(params)

        date_shift_unix = xola.convert_time(date_shift)
        date_shift = datetime.fromisoformat(date_shift).strftime("%Y-%m-%d")

        unavailable_employee = deputy.get_people_unavailability(
            date_shift)  # check who have a work
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

    logger.info("Successfully post shift, guides, employee ")

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
    if xola.subscribe_to_webhook() is False:
        logger.warning("Can not subscribe to webhook")
    deputy.subscribe_to_webhooks()
    app.run(host="0.0.0.0", port=5000)
