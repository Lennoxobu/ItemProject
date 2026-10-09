

import requests
import datetime
import os
import time
from  http import HTTPStatus


class EventSchedulerGateway:
    def __init__ (self, customer , product):
        self.customer = customer
        self.product = product


    def schedule_event(self, path , execution_time, payload=None) -> UseCaseResult :

        event = {
            "customer": self.customer,
            "product": self.product,
            "path" : path,
            "execution_time" : execution_time.timestamp(),
            "payload" : payload
        }

        response = requests.post(os.getenv("DOMAIN_ENDPOINT"),  json=event ,  timeout=30)

        if response.status_code == HttpStatus.OK:
            return UseCaseResult(return_code = 200 , excuted_time = event.execution_time)
        else:
            return UseCaseResult(return_code = 400 , excuted_time = event.execution_time)



