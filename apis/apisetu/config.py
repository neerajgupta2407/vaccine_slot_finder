# REF: https://apisetu.gov.in/public/marketplace/api/cowin
HOST = "https://cdn-api.co-vin.in/api/"
FIND_BY_PIN_SLOTS_URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByPin?pincode={pincode}&date={date}"
LIST_STATES_URL = "https://cdn-api.co-vin.in/api/v2/admin/location/states"
LIST_DISTRICT_URL = (
    "https://cdn-api.co-vin.in/api/v2/admin/location/districts/{state_id}"
)
FIND_BY_DISTRICT_SLOTS_URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={district_id}&date={date}"

COWIN_REGISTRATION_LINK = "https://selfregistration.cowin.gov.in/"
COWIN_REGISTRATION_TEXT = (
    f"<b>Open COWIN: {COWIN_REGISTRATION_LINK}</b>\n\nShare feedback @neerajgupta2407"
)

REQUEST_HEADERS = {
    "authority": "cdn-api.co-vin.in",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="90", "Google Chrome";v="90"',
    "accept": "application/json, text/plain, */*",
    "sec-ch-ua-mobile": "?0",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "origin": "https://www.cowin.gov.in",
    "sec-fetch-site": "cross-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://www.cowin.gov.in/",
    "accept-language": "en-US,en;q=0.9",
}
