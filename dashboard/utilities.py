import schedule
import time
import requests
import pickle
import json
from decouple import config
from .serializers import UnitDataAPIRequestSerializer, Unit, UnitData, FrequencyData
from datetime import datetime, timedelta
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


client = None
token = None
REQUEST_FORM_DATA_BOUNDARY = "kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A"
REQUEST_CUSTOM_HEADER = {
    'content-type': "multipart/form-data; boundary={}".format(REQUEST_FORM_DATA_BOUNDARY),
}
frequency = {"pointId": "u9das0s_ai306205.pv",
             "systemGuid": "e2e436dc-52cb-4f26-9ae7-23bce3d86727"}

with open("client.pkl", "rb") as f:
    client = pickle.load(f)


def update_client_credentials(client_id, client_secret):
    global token
    reqUrl = config("TOKEN_URL")
    payload = f"--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"grant_type\"\r\n\r\nclient_credentials\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"client_id\"\r\n\r\n{client_id}\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"client_secret\"\r\n\r\n{client_secret}\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"resource\"\r\n\r\nhttp://sentt01eprodweb.azurewebsites.net\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A--\r\n"
    response = requests.post(reqUrl, data=payload,
                             headers=REQUEST_CUSTOM_HEADER)
    if response.status_code == 200:  # kaam baki h
        token = response.json()["access_token"]
        client["id"] = client_id
        client["secret"] = client_secret
        dump_in_pickle_file()
    return response.status_code


def update_client_token():
    """
    Updates the global 'token' variable by making a POST request to the specified TOKEN_URL.

    The request includes form data for 'grant_type', 'client_id', 'client_secret', and 'resource'.
    Uses the global 'client' dictionary for client_id and client_secret values.
    """
    global token
    reqUrl = config("TOKEN_URL")
    payload = f"--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"grant_type\"\r\n\r\nclient_credentials\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"client_id\"\r\n\r\n{client['id']}\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"client_secret\"\r\n\r\n{client['secret']}\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"resource\"\r\n\r\nhttp://sentt01eprodweb.azurewebsites.net\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A--\r\n"
    response = requests.post(reqUrl, data=payload,
                             headers=REQUEST_CUSTOM_HEADER)
    token = response.json()["access_token"]


def del_prev_day_record():
    """
    Deletes records in the 'UnitData' model older than 24 hours.

    'UnitData' model has a 'sample_time' field indicating the timestamp of each record.
    """

    last_24h = datetime.now() - timedelta(days=1)
    UnitData.objects.filter(sample_time__lte=last_24h).delete()


def fetch_unit_data(units):
    reqUrl = config("UNIT_DATA_URL")

    headersList = {
        "Accept": "*/*",
        "User-Agent": "Thunder Client (https://www.thunderclient.com)",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = json.dumps({
        "queries": units
    })

    response = requests.post(reqUrl, data=payload,  headers=headersList)
    return response


def get_unit_data():

    units = UnitDataAPIRequestSerializer(Unit.objects.all(), many=True).data

    response = fetch_unit_data(
        units=units + [frequency])

    data_points = response.json()
    if isinstance(data_points, list):

        plant_unit_data = {}
        frequency_data_point = None

        for data_point in data_points:
            if data_point["pointId"] == frequency["pointId"]:
                frequency_data_point = data_point
                FrequencyData.objects.create(
                    point_value=data_point["pointValues"],
                    quality=data_point["pointAttributes"]["Quality"],
                    derived_quality=data_point["pointAttributes"]["DerivedQuality"],
                    sample_time=datetime.fromtimestamp(0) +
                    timedelta(microseconds=data_point["sampleTime"]/1000))
                continue
            try:
                unit_data_obj = UnitData(unit=Unit.objects.get(
                    point_id=data_point["pointId"]), point_value=data_point["pointValues"],
                    quality=data_point["pointAttributes"]["Quality"],
                    derived_quality=data_point["pointAttributes"]["DerivedQuality"],
                    sample_time=datetime.fromtimestamp(0) +
                    timedelta(microseconds=data_point["sampleTime"]/1000)
                )

                grp_name = f"{unit_data_obj.unit.plant.name}"

                if grp_name in plant_unit_data:
                    plant_unit_data[grp_name].append(data_point)
                else:
                    plant_unit_data[grp_name] = [data_point]

                unit_data_obj.save()
            except Exception as e:
                print(e)

        channel_layer = get_channel_layer()

        for i in plant_unit_data:
            async_to_sync(channel_layer.group_send)(f"{i}", {
                "type": "unit_data_for_plant",
                "data": plant_unit_data[i],
            })


# Schedule tasks
schedule.every(55).minutes.do(update_client_token)
schedule.every(30).seconds.do(get_unit_data)
schedule.every().day.at("00:00", "Asia/Kolkata").do(del_prev_day_record)


def run_scheduler():
    """
    Runs the scheduled tasks using the 'schedule' library in an infinite loop.
    It checks for pending tasks every 5 seconds.
    """
    while True:
        schedule.run_pending()
        time.sleep(5)


def dump_in_pickle_file():
    """
    Dumps the 'client' variable into a pickle file named "client.pkl".
    """
    with open("client.pkl", "wb") as f:
        pickle.dump(client, f)

# u9das0s_ai306205.pv
# e2e436dc-52cb-4f26-9ae7-23bce3d86727


def dump_data():

    start = (datetime.now().replace(hour=0, minute=0, second=0) -
             timedelta(hours=5, minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    end = datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    url = "https://t01eprodcloudapp.sentience.honeywell.com/api/timeseries/values/intervals"
    headersList = {
        "Accept": "*/*",
        "User-Agent": "Thunder Client (https://www.thunderclient.com)",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    units = UnitDataAPIRequestSerializer(Unit.objects.all(), many=True).data
    payload = json.dumps({
        "startTime": start,
        "endTime": end,
        "queries": units,
        "includeBounds": False
    })
    UnitData.objects.all().delete()
    response = requests.post(url, data=payload, headers=headersList)
    for unit in response.json():
        print(unit)
        unit_obj = Unit.objects.get(point_id=unit["pointId"])
        for time, value in sorted(unit["pointValues"].items()):
            time_micro = int(time)//1000
            UnitData.objects.create(
                unit=unit_obj,
                point_value=value,
                derived_quality="Good",
                quality="Good",
                sample_time=datetime.fromtimestamp(0) +
                timedelta(microseconds=time_micro)
            )
    payload = json.dumps({
        "startTime": start,
        "endTime": end,
        "queries": [frequency],
        "includeBounds": False
    })
    response = requests.post(url, data=payload, headers=headersList)
    FrequencyData.objects.all().delete()
    for unit in response.json():
        print(unit)
        for time, value in sorted(unit["pointValues"].items()):
            time_micro = int(time)//1000
            FrequencyData.objects.create(
                point_value=value,
                derived_quality="Good",
                quality="Good",
                sample_time=datetime.fromtimestamp(0) +
                timedelta(microseconds=time_micro)
            )

    print("end")
