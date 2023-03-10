import json
import logging
import signal
import time


from ricxappframe.xapp_frame import RICMessage, RICRegion, RICService, RICSubscription
from ricxappframe.xapp_frame import RICXapp, RICXappException

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Define the signal handler function
def signal_handler(sig, frame):
    logging.info("Exiting...")
    exit(0)

# Define the E2 message handler function
def e2_message_handler(e2event):
    logging.info("Received E2 message: %s", e2event.data)

# Define the xApp class
class HelloWorldXapp(RICXapp):
    def __init__(self):
        super().__init__("HelloWorldXapp")
        self.subscription_id = None
        self.region_id = None
        self.service_id = None
        self.subscribed = False

    # Override the RICXapp.run() method
    def run(self):
        # Register the signal handler
        signal.signal(signal.SIGINT, signal_handler)

        # Initialize the E2 interface
        self.e2_init()
        self.e2_register_callback(e2_message_handler)

        # Register the RIC subscription
        self.subscription_id = self.register_subscription(RICSubscription.RIC_SUB_REQ_SUBDEL, None, self.subscription_callback)
        logging.info("Registered subscription with subscription ID: %s", self.subscription_id)

        # Register the RIC region
        self.region_id = self.register_ric_region(RICRegion.RIC_REGION_NOTIFY, None, None)
        logging.info("Registered RIC region with region ID: %s", self.region_id)

        # Register the RIC service
        self.service_id = self.register_ric_service(RICService.RIC_SERVICE_UPDATE, self.service_callback)
        logging.info("Registered RIC service with service ID: %s", self.service_id)

        # Wait for events
        while True:
            time.sleep(1)

    # Define the RIC subscription callback function
    def subscription_callback(self, sub_id, notification):
        logging.info("Received RIC subscription notification: %s", notification)
        self.subscribed = True

    # Define the RIC service callback function
    def service_callback(self, service_data):
        logging.info("Received RIC service update: %s", service_data)

        # Send an E2 message
        e2_message = {"message": "Hello, E2!"}
        self.e2_send_message(json.dumps(e2_message).encode(), 1234)

if __name__ == "__main__":
    try:
        # Create and run the xApp
        xapp = HelloWorldXapp()
        xapp.run()
    except RICXappException as e:
        logging.error(str(e))
