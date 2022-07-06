import singer
import requests
import json
import sys

from datetime import timedelta, date, datetime
from dateutil import tz

#schema for the records required
schema = {'properties': {
    'sunrise':{'type':'string','format':'timestamp'}, 
    'sunset':{'type':'string','format':'timestamp'}}}
#api url
URL = "https://api.sunrise-sunset.org/json"

#fixed parameters for requests
PARAMS = {"lat":18.5204, "lng": 73.8567, "formatted":0 }

def daterange(date1, date2):
    """This functions yields a set of dates between date1 and date2 included."""
    for n in range(int ((date2 - date1).days)+1):
        yield (date1 + timedelta(n)).strftime("%Y-%m-%d")

def convert_to_ist(dt_string):
    """This function converts UTC into an IST timestamp."""
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('Asia/Kolkata')
    utc = datetime.strptime(dt_string, "%Y-%m-%dT%H:%M:%S%z")
    utc = utc.replace(tzinfo=from_zone)
    central = utc.astimezone(to_zone)
    return central.strftime("%Y-%m-%d %H:%M:%S")

def retreive_data(start_date, end_date):
    """This function is used to retreive the required data from the api 
    and also transforms it using convert_to_ist function, and returns the
    required set of results."""
    for dt in daterange(start_date,end_date):
        result1 = requests.get(URL, params = {**PARAMS, "date":dt})
        required = {key: convert_to_ist(result1.json()['results'][key]) for key in ['sunrise','sunset']}
        yield required

#Load the last record updated date from state.json
if sys.argv[1] == "--state":
    f = open(sys.argv[2],"r+")
else:
    print("State not provided")
    exit()

data = json.load(f)
#start date = date 1 day after the date in state.json 
start_date = datetime.strptime(data['last_record'],"%Y-%m-%d") + timedelta(1) 
end_date = datetime.today()
result = retreive_data(start_date, end_date)

singer.write_schema(stream_name = "sunrise_sunset", schema= schema, key_properties=[])
singer.write_records(stream_name= "sunrise_sunset", records = (item for item in result))
singer.write_state(value={
        "last_record":end_date.strftime("%Y-%m-%d")
    })
f.close()

json_object = json.dumps({"last_record":end_date.strftime("%Y-%m-%d")})
#Writing state to state.json file
with open(sys.argv[2],"w") as file:
    file.write(json_object)  
