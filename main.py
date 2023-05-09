#!/usr/bin/env python3

import os
from os import path
import argparse
from tracemalloc import start
from typing import cast
from urllib import parse
from fhir import *
from more_itertools import last
import arrow
from oauthlib.oauth2.rfc6749.errors import MissingTokenError
from typing_extensions import Final
from withings_api import AuthScope, WithingsAuth, WithingsApi
from withings_api.common import CredentialsType, MeasureType, AuthFailedException, NotifyAppli
import requests
from requests.auth import HTTPBasicAuth
from pick import pick
import uuid
import pickle
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load environment variables
WITHINGS_CLIENT_ID = os.environ.get('WITHINGS_CLIENT_ID')
WITHINGS_CLIENT_SECRET = os.environ.get('WITHINGS_CLIENT_SECRET')
CALLBACK_URL = os.environ.get('CALLBACK_URL')

print('ID -> ', WITHINGS_CLIENT_ID)
print('SECRET -> ', WITHINGS_CLIENT_SECRET)
print('CALLBACK_URL -> ', CALLBACK_URL)

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
    parser: Final = argparse.ArgumentParser(description="Process some integers.")
    parser.add_argument(
        "--client-id",
        dest="client_id",
        help="Client ID provided by Withings",
    )
    parser.add_argument(
        "--consumer-secret",
        dest="consumer_secret",
        help="Consumer Secret provided by Withings",
    )
    parser.add_argument(
        "--callback-uri",
        dest="callback_uri",
        help="Callback URI configured for Withings application.",
    )
    parser.add_argument(
        "--live-data",
        dest="live_data",
        action="store_true",
        help="Should we run against live data? (Removal of .credentials file is required before running)",
    )
    
    args: Final = parser.parse_args()

    if path.isfile(CREDENTIALS_FILE):
        api = WithingsApi(load_credentials(), refresh_cb=save_credentials)
        try:
            api.user_get_device()
            api.notify_subscribe(
                callbackurl="https://localhost:8080/new_weights",
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
        print("Goto this URL in your browser and authorize:", authorize_url)

        print(
            "Once you are redirected, copy and paste the whole url"
            "(including code) here."
        )
        redirected_uri: Final = input("Provide the entire redirect uri: ")
        redirected_uri_params: Final = dict(
            parse.parse_qsl(parse.urlsplit(redirected_uri).query)
        )

        auth_code: Final = redirected_uri_params["code"]
        print("Auth code:", auth_code)
        print("Getting Creddentials with auth code", auth_code)
        save_credentials(auth.get_credentials(auth_code))

    api = WithingsApi(load_credentials(), refresh_cb=save_credentials)
    print("Refreshing token...")
    api.refresh_token()
    print("\n")

if __name__ == "__main__":
    main()