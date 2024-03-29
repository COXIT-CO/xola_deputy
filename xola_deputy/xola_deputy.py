"""Main script which start all logic. Here we have 2 webhooks,
and process date from request from XOLA and DEPUTY"""
from flask import Flask, request, Response
from xola_client import XolaClient
from deputy_client import DeputyClient
from logger import LoggerClient
from google_sheets_client import GoogleSheetsClient
from global_config import create_tread

app = Flask(__name__)
logging = LoggerClient()
logging.settings_init()
logging = logging.get_logger()

xola = XolaClient(logging)
xola.init_settings()
deputy = DeputyClient(logging)
deputy.init_settings()
sheets = GoogleSheetsClient(deputy, logging)
sheets.init_settings()


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

        id_shift, date_shift = deputy.process_data_from_new_shift(params)

        if date_shift is False:
            return Response(status=500)

        date_shift = xola.convert_time(date_shift)

        id_location = mapping["Area"]
        title = mapping['Possible Area Nicknames in Production']

        unavailable_employee = deputy.process_people_unavailability(
            date_shift, id_location)[0]  # check who have a work
        if unavailable_employee is False:
            return Response(status=500)

        id_employee = deputy.get_people_availability(
            id_shift, unavailable_employee)

        params.update({
            "intRosterId": id_shift,
            "intRosterEmployee": id_employee
        })
        is_good = deputy.process_data_from_new_shift(
            params)  # post shift for employee
        if is_good is False:
            return Response(status=500)
        sheets.change_cells(
            params["intStartTimestamp"],
            params["intEndTimestamp"],
            title)
        logging.info("Successfully post shift, sheets ")
        name_of_employee = deputy.get_employee_name(id_employee)
        if xola.verification_guides_for_event(name_of_employee) is False:
            return Response(status=500)

    logging.info("Successfully post guides")

    return Response(status=200)


@app.route("/delete_employee", methods=['POST'])
def deputy_delete():
    """we change all list in google sheet,when in deputy delete employee"""
    sheets.change_all_spread()
    logging.info("Successfully change sheet")

    return Response(status=200)


@app.route("/insert_employee", methods=['POST'])
def deputy_insert():
    """we change all list in google sheet,when in deputy insert employee"""
    sheets.change_all_spread()
    logging.info("Successfully change sheet")

    return Response(status=200)


@app.route("/unvial_employee", methods=['POST'])
def deputy_unvial():
    """get all day off from deputy,change specific list,and make minus 1 to cells"""
    list_of_unvial = deputy.get_employee_unavail()

    if list_of_unvial is False:
        return Response(status=500)

    title_to_change = set()
    for unvial_time in list_of_unvial:
        title_to_change.add(unvial_time[2])

    for title in title_to_change:
        sheets.change_specific_spread(title)

    for unvial_time in list_of_unvial:
        sheets.change_cells(unvial_time[0], unvial_time[1], unvial_time[2])

    logging.info("Successfully change sheet")
    return Response(status=200)


if __name__ == '__main__':
    if xola.subscribe_to_webhook() is False:
        logging.warning("Can not subscribe to webhook")
    deputy.subscribe_to_webhooks()
    sheets.change_all_spread()
    create_tread(sheets.change_all_spread)
    app.run(host="0.0.0.0", port=5000)
