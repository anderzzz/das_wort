"""Vinnova grant analysis

Written by: Anders Ohrn, 2024 May

"""
import json
from httpx import Client
from typing import Sequence, Dict, Optional

from openai import OpenAI


VINNOVA_API_CONF_FILE = "vinnova_api_conf.json"


class VinnovaClientError(Exception):
    pass


class VinnovaDataRetrievalLayer:
    """Bla bla

    """
    base_url = "https://data.vinnova.se/api/"

    def __init__(self,
                 name: str,
                 endpoint: str,
                 description: Optional[str] = None,
                 parameters_description: Optional[Dict[str, Dict[str, str]]] = None,
                 ):
        self.name = name
        self.endpoint = endpoint
        self.description = description
        self.parameters_description = parameters_description

        self._client = None

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

    @property
    def client(self):
        if self._client is None:
            raise VinnovaClientError("HTTP client not set.")
        return self._client

    @client.setter
    def client(self, client: Client):
        self._client = client

    def __call__(self, data: str) -> Dict:
        """Bla bla

        """
        url = f"{self.base_url}/{self.endpoint}/{data}"
        response = self.client.get(url)
        if response.status_code != 200:
            raise VinnovaClientError(f"HTTP GET request failed with status code {response.status_code}")

        return response.json()


def make_vinnova_drl_func(api_conf_fp: str):
    with open(api_conf_fp, 'r') as f:
        api_conf = json.load(f)

    vinnova_drl_func = {}
    for name, conf in api_conf['apis'].items():
        vinnova_drl_func[name] = VinnovaDataRetrievalLayer(
            name=name,
            endpoint=conf['endpoint'],
            description=conf['description'],
            parameters_description=conf['parameters']
        )

    return vinnova_drl_func





def main():
    vinnova_drl_func = make_vinnova_drl_func(VINNOVA_API_CONF_FILE)
    vinnova_drl = VinnovaDataRetrievalLayer(name="program", endpoint="program")
    vinnova_drl.client = Client()
    x = vinnova_drl.get("2022-01-01")
    print(x)


if __name__ == '__main__':
    main()
