"""The Vinnova Data Retrieval Layer (DRL) module

"""
import json
from typing import Dict, Optional, Callable

from vinnova_api import decorators_to_vinnova_api, VinnovaAPI


class VinnovaDataRetrievalLayerMissingAPIError(Exception):
    pass


class VinnovaDataRetrievalLayer:
    """The Vinnova data retrieval layer (DRL) class. It provides an interface to the Vinnova APIs
    along with pre- and post-processing of the data. In addition, instances of this class can be
    tools in an LLM engine (e.g. OpenAI, Mistral).

    Args:
        name (str): The name of the DRL
        vinnova_api (VinnovaAPI): The Vinnova API object, single endpoint
        description (Optional[str]): The description of the API; required for LLM tools
        parameters_description (Optional[Dict[str, Dict[str, str]]): The description of the parameters; required for LLM tools
        api_decorator (Optional[Callable]): The decorator function

    """
    def __init__(self,
                 name: str,
                 vinnova_api: VinnovaAPI,
                 description: Optional[str] = None,
                 parameters_description: Optional[Dict[str, Dict[str, str]]] = None,
                 api_decorator: Optional[Callable] = None,
                 ):
        self.name = name
        self.vinnova_api = vinnova_api
        self.description = description
        self.parameters_description = parameters_description

        if api_decorator is not None:
            self._func = api_decorator(self.vinnova_api)
        else:
            self._func = self.vinnova_api

    @property
    def specification_str(self):
        """Return the DRL function specification that is compatible with LLM tools specification

        """
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
        """Pass the data to the API

        """
        return self._func(data)


def build_vinnova_drl_func(
        api_name: str,
        api_conf_fp: str
) -> VinnovaDataRetrievalLayer:
    """Build a data retrieval layer according to configuration

    Args:
        api_name (str): The name of the API
        api_conf_fp (str): The path to the configuration file

    """
    with open(api_conf_fp, 'r') as f:
        api_conf = json.load(f)

    try:
        conf = api_conf['apis'][api_name]
    except KeyError:
        raise VinnovaDataRetrievalLayerMissingAPIError(f"API {api_name} not found in DRL configuration file")

    vinnova_api = VinnovaAPI(conf['endpoint'])

    if 'decorator' in conf:
        _decorator = decorators_to_vinnova_api[conf['decorator']]
    else:
        _decorator = None

    return VinnovaDataRetrievalLayer(
        name=api_name,
        description=conf['description'],
        parameters_description=conf['parameters'],
        vinnova_api=vinnova_api,
        api_decorator=_decorator,
    )


def test_vinnova_drl_program():
    drl_program_list = build_vinnova_drl_func('program-list', 'vinnova_drl_conf.json')
    x = drl_program_list('2024-01-01')
    print (x)


def test_vinnova_drl_projekt():
    drl_project_list = build_vinnova_drl_func('projekt-list', 'vinnova_drl_conf.json')
    x = drl_project_list('2024-01-01')
    print (x)


def test_vinnova_drl_projekt_details():
    drl_project_details = build_vinnova_drl_func('projekt-details', 'vinnova_drl_conf.json')
    x = drl_project_details('2022-03113')
    print (x)


def test_vinnova_drl_utlysningar():
    drl_utlysningar = build_vinnova_drl_func('utlysning-list', 'vinnova_drl_conf.json')
    x = drl_utlysningar('2024-01-01')
    print (x)

def test_vinnova_drl_utlysningar_details():
    drl_utlysningar_details = build_vinnova_drl_func('utlysning-details', 'vinnova_drl_conf.json')
    x = drl_utlysningar_details('2016-02193')
    print (x)


def test_vinnova_drl_ansokningsomgang_details():
    drl_ansokningsomgang_details = build_vinnova_drl_func('ansokningsomgang-details', 'vinnova_drl_conf.json')
    x = drl_ansokningsomgang_details('2016-02198')
    print (x)
    x = drl_ansokningsomgang_details('2019-05009')
    print (x)



if __name__ == '__main__':
    #test_vinnova_drl_utlysningar()
    #test_vinnova_drl_utlysningar_details()
    test_vinnova_drl_ansokningsomgang_details()
