import time
from json import dumps
from typing import List, Optional, Union
import datadog
import re
from urllib.parse import ParseResult, parse_qsl, unquote, urlencode, urljoin, urlparse

from unidecode import unidecode

from nephrogo import settings


def str_to_ascii(s: str) -> str:
    return unidecode(s)


def only_alphanumeric_or_spaces(s: str) -> str:
    return re.sub(r'[^a-zA-Z0-9 ]+', '', s)


def add_url_params(url, params):
    """ Add GET params to provided URL being aware of existing.
    :param url: string of target URL
    :param params: dict containing requested params to be added
    :return: string with updated URL
    >> url = 'http://stackoverflow.com/test?answers=true'
    >> new_params = {'answers': False, 'data': ['some','values']}
    >> add_url_params(url, new_params)
    'http://stackoverflow.com/test?data=some&data=values&answers=false'
    """
    # Unquoting URL first so we don't loose existing args
    url = unquote(url)
    # Extracting url info
    parsed_url = urlparse(url)
    # Extracting URL arguments from parsed URL
    get_args = parsed_url.query
    # Converting URL arguments to dict
    parsed_get_args = dict(parse_qsl(get_args))
    # Merging URL arguments dict with new params
    parsed_get_args.update(params)

    parsed_get_args = {k: v for k, v in parsed_get_args.items() if v is not None}

    # Bool and Dict values should be converted to json-friendly values
    # you may throw this part away if you don't like it :)
    parsed_get_args.update(
        {k: dumps(v) for k, v in parsed_get_args.items()
         if isinstance(v, (bool, dict))}
    )

    # Converting URL argument to proper query string
    encoded_get_args = urlencode(parsed_get_args, doseq=True)
    # Creating new parsed result object based on provided with new
    # URL arguments. Same thing happens inside of urlparse.
    new_url = ParseResult(
        parsed_url.scheme, parsed_url.netloc, parsed_url.path,
        parsed_url.params, encoded_get_args, parsed_url.fragment
    ).geturl()

    return new_url


class Datadog:
    class __DatadogSingleton:
        def __init__(self):
            datadog.initialize(**settings.DATADOG_SETTINGS)

    instance = None

    def __init__(self):
        if not Datadog.instance:
            Datadog.instance = Datadog.__DatadogSingleton()

    def __getattr__(self, name):
        return getattr(self.instance, name)

    def gauge(self, metric_name: str, value: Union[int, float], tags: Optional[List[str]] = None):
        options = {
            'metric': metric_name,
            'points': [(int(time.time()), value)],
            'type': 'gauge',
        }

        if tags:
            options['tags'] = tags

        return datadog.api.Metric.send(**options)
