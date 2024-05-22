"""The Vinnova Data Retrieval Layer (DRL) module

"""
import json
from typing import Dict, Optional, Callable, List

from httpx import Client


class VinnovaHTTPClientError(Exception):
    pass


def get_httpx_client() -> Client:
    return Client(timeout=60.0)


class VinnovaAPI:
    """Bla bla

    """
    base_url = "https://data.vinnova.se/api"

    def __init__(self,
                 endpoint: str,
                 headers: Optional[Dict[str, str]] = None,
                 ):
        self.endpoint = endpoint
        self.headers = headers
        self._client = None

    @property
    def client(self):
        if self._client is None:
            raise VinnovaHTTPClientError("HTTP client not set.")
        return self._client

    @client.setter
    def client(self, client: Client):
        self._client = client

    def __call__(self, data: str) -> Dict:
        """Bla bla

        """
        url = f"{self.base_url}/{self.endpoint}/{data}"
        print (url)
        response = self.client.get(url, headers=self.headers)
        if response.status_code != 200:
            raise VinnovaHTTPClientError(f"HTTP GET request failed with status code {response.status_code}")

        return response.json()


class VinnovaDataRetrievalLayer:
    """Bla bla

    """
    def __init__(self,
                 name: str,
                 vinnova_api: VinnovaAPI,
                 description: Optional[str] = None,
                 parameters_description: Optional[Dict[str, Dict[str, str]]] = None,
                 decorator: Optional[Callable] = None,
                 ):
        self.name = name
        self.vinnova_api = vinnova_api
        self.description = description
        self.parameters_description = parameters_description

        if decorator is not None:
            self._func = decorator(self.vinnova_api)
        else:
            self._func = self.vinnova_api

    @property
    def specification_str(self):
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.parameters_description,
                    "required": ["data"],
                }
            }
        }

    def __call__(self, data: str) -> Dict:
        """Bla bla

        """
        return self._func(data)


def _vinnova_api_decorator_only_diarienr(func):
    def wrapper(data: str) -> List:
        raw_data = func(data)
        diarienr = []
        for entry in raw_data:
            try:
                diarienr.append(entry['Diarienummer'])
            except KeyError:
                print (entry)
                raise KeyError("Diarienummer not found in entry")
        return diarienr
    return wrapper


decorators_to_vinnova_api = {
    'only_diarienr': _vinnova_api_decorator_only_diarienr,
}


def build_vinnova_drl_func(api_conf_fp: str):
    """Bla bla

    """
    client = get_httpx_client()
    with open(api_conf_fp, 'r') as f:
        api_conf = json.load(f)

    vinnova_drl_func = {}
    for name, conf in api_conf['apis'].items():
        vinnova_api = VinnovaAPI(conf['endpoint'])
        vinnova_api.client = client

        if 'decorator' in conf:
            _decorator = decorators_to_vinnova_api[conf['decorator']]
        else:
            _decorator = None

        vinnova_drl_func[name] = VinnovaDataRetrievalLayer(
            name=name,
            description=conf['description'],
            parameters_description=conf['parameters'],
            vinnova_api=vinnova_api,
            decorator=_decorator,
        )

    return vinnova_drl_func


def test_vinnova_drl_project_api():
    api = VinnovaAPI('program')
    api.client = get_httpx_client()
    data = api('2023-01-01')
    print (data)
    api = VinnovaAPI('projekt')
    api.client = get_httpx_client()
    data = api('2023-01-01')
    print (data)


if __name__ == '__main__':
    test_vinnova_drl_project_api()
    print('Done')
