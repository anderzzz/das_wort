"""The interface to the Vinnova API and post-processing of the returned data.

"""
from typing import Dict, Optional, List, Callable
from httpx import Client


class VinnovaHTTPClientError(Exception):
    pass


def get_httpx_client(timeout: float = 60.0) -> Client:
    return Client(timeout=timeout)


class VinnovaAPI:
    """The basic interface to the Vinnova APIs

    The APIs are relatively simple with few options. They are accessed via HTTP GET requests,
    usually without any headers. The data is returned as JSON.

    Documentation is found at https://data.vinnova.se/api/

    """
    base_url = "https://data.vinnova.se/api"

    def __init__(self,
                 endpoint: str,
                 headers: Optional[Dict[str, str]] = None,
                 ):
        self.endpoint = endpoint
        self.headers = headers
        self._client = get_httpx_client()

    @property
    def client(self):
        if self._client is None:
            raise VinnovaHTTPClientError("HTTP client not set.")
        return self._client

    @client.setter
    def client(self, client: Client):
        self._client = client

    def __call__(self, data: str) -> Dict:
        """Invoke the API by passing data to the endpoint.

        """
        url = f"{self.base_url}/{self.endpoint}/{data}"
        response = self.client.get(url, headers=self.headers)
        if response.status_code != 200:
            raise VinnovaHTTPClientError(f"HTTP GET request failed with status code {response.status_code}")

        return response.json()


#
# The Vinnova APIs are basic and return typically very large and information rich JSON
# objects. In some applications, these objects are unsuitable to be used directly and
# therefore best filtered and transformed before being used. This is done by decorators
# that are applied to the VinnovaAPI object.
def _identity_func(x):
    return x


def _make_vinnova_api_decorator(func_pre: Callable = _identity_func,
                                func_post: Callable = _identity_func) -> Callable:
    """Make a decorator for the VinnovaAPI object."""
    def decorator(api: VinnovaAPI) -> Callable:
        def wrapper(data: str) -> List:
            return func_post(
                api(
                    func_pre(data)
                )
            )
        return wrapper
    return decorator


def _post_only_diarienr(payload: Dict):
    diarienr = []
    for entry in payload:
        try:
            diarienr.append(entry['Diarienummer'])
        except KeyError:
            print(entry)
            raise KeyError("Diarienummer not found in entry")
    return diarienr


decorators_to_vinnova_api = {
    'only_diarienr': _make_vinnova_api_decorator(func_post=_post_only_diarienr),
}


def test_vinnova_drl_project_api():
    api = VinnovaAPI('program')
    api.client = get_httpx_client()
    data = api('2023-01-01')
    print(data)
    api = VinnovaAPI('projekt')
    api.client = get_httpx_client()
    data = api('2023-01-01')
    print(data)


if __name__ == '__main__':
    test_vinnova_drl_project_api()
    print('Done')
