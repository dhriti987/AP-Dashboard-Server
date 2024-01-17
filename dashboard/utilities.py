import schedule
import time
import requests
import pickle
import json
from decouple import config

client = None
token = None
REQUEST_FORM_DATA_BOUNDARY = "kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A"
REQUEST_CUSTOM_HEADER = {
    'content-type': "multipart/form-data; boundary={}".format(REQUEST_FORM_DATA_BOUNDARY),
}


with open("client.pkl", "rb") as f:
    client = pickle.load(f)


def update_client_token():
    reqUrl = config("TOKEN_URL")
    payload = f"--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"grant_type\"\r\n\r\nclient_credentials\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"client_id\"\r\n\r\n{client['id']}\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"client_secret\"\r\n\r\n{client['secret']}\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A\r\nContent-Disposition: form-data; name=\"resource\"\r\n\r\nhttp://sentt01eprodweb.azurewebsites.net\r\n--kljmyvW1ndjXaOEAg4vPm6RBUqO6MC5A--\r\n"
    response = requests.post(reqUrl, data=payload,  headers=REQUEST_CUSTOM_HEADER)
    print(response.text)



def get_unit_data():
    print("I'm also working...")


schedule.every(55).minutes.do(update_client_token)
schedule.every(30).seconds.do(get_unit_data)


def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(5)


def dump_in_pickle_file():
    with open("client.pkl", "wb") as f:
        pickle.dump(client, f)


# dump_in_pickle_file()
update_client_token()
