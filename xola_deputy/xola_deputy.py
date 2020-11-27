"""Main script which start all logic. Here we have 2 webhooks,
and process date from request from XOLA and DEPUTY"""
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
    params = xola.start(request)
    if params is False:
        return Response(status=500)
    # first time we created shift in open block
    id_shift = deputy.post_new_shift(params)
    id_employee = deputy.get_people_availability(
        id_shift)  # watch who can do this
    params.update({
        "intRosterId": id_shift,
        "intRosterEmployee": id_employee
    })
    deputy.post_new_shift(params)
    return Response(status=200)


if __name__ == '__main__':
    if xola.subscribe_to_webhook() is False:
        logger.warning("Can not subscribe to webhook")
    app.run(host="0.0.0.0", port=5000)
