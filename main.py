#!/usr/bin/env python3

import os
from os import path
from typing import cast
from urllib import parse
from urllib.request import urlopen
from fhir import *
from typing_extensions import Final
from withings_api import AuthScope, WithingsAuth, WithingsApi
from withings_api.common import CredentialsType, AuthFailedException, NotifyAppli
import pickle
from dotenv import load_dotenv
from options import ShowOptions
import webbrowser
import time

# Load environment variables from .env file
load_dotenv()

# Load environment variables
WITHINGS_CLIENT_ID = os.environ.get('WITHINGS_CLIENT_ID')
WITHINGS_CLIENT_SECRET = os.environ.get('WITHINGS_CLIENT_SECRET')
CALLBACK_URL = os.environ.get('CALLBACK_URL')
ACCOUNT_WITHINGS_URL = os.environ.get('ACCOUNT_WITHINGS_URL')
URL_FILE = os.environ.get('URL_FILE')

CREDENTIALS_FILE: Final = path.abspath(
    path.join(path.dirname(path.abspath(__file__)), "./.credentials")
)

def save_credentials(credentials: CredentialsType) -> None:
    """Save credentials to a file."""
    print("Saving credentials in:", CREDENTIALS_FILE)
    with open(CREDENTIALS_FILE, "wb") as file_handle:
        pickle.dump(credentials, file_handle)


def load_credentials() -> CredentialsType:
    """Load credentials from a file."""
    print("Using credentials saved in:", CREDENTIALS_FILE)
    with open(CREDENTIALS_FILE, "rb") as file_handle:
        return cast(CredentialsType, pickle.load(file_handle))

def main() -> None:

    if path.isfile(CREDENTIALS_FILE):
        api = WithingsApi(load_credentials(), refresh_cb=save_credentials)
        try:
            api.notify_subscribe(
                callbackurl="{0}/new_weights".format(CALLBACK_URL),
                appli=NotifyAppli.WEIGHT,
            )
        except AuthFailedException:
            os.remove(CREDENTIALS_FILE)
            print("Credentials in file are expired. Re-starting auth procedure...")

    if not path.isfile(CREDENTIALS_FILE):
        auth: Final = WithingsAuth(
            client_id = WITHINGS_CLIENT_ID,
            consumer_secret = WITHINGS_CLIENT_SECRET,
            callback_uri = CALLBACK_URL,
            scope=(
                AuthScope.USER_ACTIVITY,
                AuthScope.USER_METRICS,
                AuthScope.USER_INFO,
            ),
        )
        authorize_url: Final = auth.get_authorize_url()
        
        webbrowser.open(authorize_url)
        while not os.path.exists(URL_FILE):
            print("Waiting for callback...")
            time.sleep(2)
            pass
        
        f = open(URL_FILE, 'r')
        redirected_uri = f.read()

        print(redirected_uri)
        redirected_uri_params: Final = dict(
            parse.parse_qsl(parse.urlsplit(redirected_uri).query)
        )

        os.remove(URL_FILE)

        auth_code: Final = redirected_uri_params["code"]
        print("Auth code:", auth_code)
        print("Getting Creddentials with auth code", auth_code)
        save_credentials(auth.get_credentials(auth_code))

    api = WithingsApi(load_credentials(), refresh_cb=save_credentials)
    print("Refreshing token...")
    api.refresh_token()
    print("\n")
    ShowOptions(api)

if __name__ == "__main__":
    main()