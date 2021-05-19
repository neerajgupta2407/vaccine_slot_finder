from datetime import datetime, timedelta

import requests

from .config import *
from .objects import *


class APISETU:
    def __init__(self):
        pass

    def _get_date_str(self, date):
        return "{}-{}-{}".format(date.day, date.month, date.year)

    def send_request(self, url, query_params={}):
        # url = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode=110027&date=20-05-2021'
        payload = {}

        headers = REQUEST_HEADERS
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(response.content)

    def slot_by_pincode(self, pincode, date=None):
        if not date:
            date = datetime.today().date() + timedelta(days=0)
        url = FIND_BY_PIN_SLOTS_URL.format(
            date=self._get_date_str(date), pincode=pincode
        )
        data = self.send_request(url)
        resp = [CenterObject(**a) for a in data["centers"]]
        return resp

    def slot_by_district(self, district_id, date=None):
        if not date:
            date = datetime.today().date() + timedelta(days=0)
        url = FIND_BY_DISTRICT_SLOTS_URL.format(
            date=self._get_date_str(date), district_id=district_id
        )
        data = self.send_request(url)
        resp = [CenterObject(**a) for a in data.get("centers", [])]
        return resp

    def get_states(self):
        url = LIST_STATES_URL
        data = self.send_request(url)
        resp = [StateObject(**a) for a in data.get("states", [])]
        return resp

    def get_district(self, state_id):
        url = LIST_DISTRICT_URL.format(state_id=state_id)
        data = self.send_request(url)
        resp = [DistrictObject(**a) for a in data.get("districts", [])]
        return resp
