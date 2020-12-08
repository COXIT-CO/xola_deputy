"""Main script which start all logic. Here we have 2 webhooks,
and process date from request from XOLA and DEPUTY"""
from datetime import datetime
from flask import Flask, request, Response
from xola_client import XolaClient
from deputy_client import DeputyClient
from logger import LoggerClient

app = Flask(__name__)
logger = LoggerClient().get_logger()
xola = XolaClient(logger)
deputy = DeputyClient(logger)


@app.route("/xola", methods=['POST'])
def xola_webhook():
    """Take response from xola notification about order.
        Create parameters for deputy POST request with data from XOLA.
        Post new shift with this parameters , and check which employee free.
        :return: code 200 is all good, code 500 - arose problem
    """
    params, number_shifts = xola.start(request)
    if params is False:
        return Response(status=500)
    for _ in range(number_shifts):
        # first time we created shift in open block
        id_shift, date_shift = deputy.post_new_shift(params)

        date_shift = datetime.fromisoformat(date_shift)
        date_shift = date_shift.strftime("%Y-%m-%d")

        unavailable_employee = deputy.get_people_unavailability(
            date_shift)  # check who have a work
        id_employee = deputy.get_people_availability(
            id_shift, unavailable_employee)

        params.update({
            "intRosterId": id_shift,
            "intRosterEmployee": id_employee
        })
        deputy.post_new_shift(params)  # post shift for employee

        name_of_employee = deputy.get_employee_name(id_employee)
        if xola.post_guides_for_event(name_of_employee) is False:
            return Response(status=500)
    logger.info("Successfully post shift, guides, employee ")

    return Response(status=200)


if __name__ == '__main__':
    if xola.subscribe_to_webhook() is False:
        logger.warning("Can not subscribe to webhook")
    app.run(host="0.0.0.0", port=5000)
