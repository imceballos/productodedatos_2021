import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import urllib.parse


def requests_retry_session(
    retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def urlencode_string(payload_string):
    return urllib.parse.quote(payload_string, safe="=")


def urlencode_sequence(sequence):
    return urllib.parse.urlencode(sequence)
