import requests 
import re
from collections import namedtuple

from config import ACCESS_KEY, SECRET_KEY


OnShapeDocInfo = namedtuple("OnShapeDocInfo", ('did', 'wv', 'wvid', 'eid'))


def get_doc_names(document_url):
    """
    Gets the names of the document and "tab" names based on a url. Two calls need to be made, one for the document name
    and another for the elements. The call to get document name also contains a lot of other useful information, such as 
    the current user's permissions interacting with the document, document owner name, isMutable, etc.
    :param document_url: the url of the onshape document
    :return: the document name information as a list
    """

    # Use the API keys generated from the Onshape developer portal 
    api_keys = (ACCESS_KEY, SECRET_KEY)

    doc_info_url = get_doc_info_url(get_doc_info(document_url))
    doc_elements_url = get_doc_elements_url(get_doc_info(document_url))

    doc_name = fetch_document_name(api_keys, doc_info_url)
    doc_elements = fetch_document_elements(api_keys, doc_elements_url, get_doc_info(document_url))

    return [doc_name] + doc_elements


def get_doc_info(document_url: str) -> OnShapeDocInfo:
    """
    Builds a special document info url in order to fetch the wanted data from the document through the Onshape API
    :param document_url: the url of the onshape document
    """
    m = re.match(r"^https?://cad.onshape.com/documents/([0-9a-f]+)/([wv])/([0-9a-f]+)/e/([0-9a-f]+)", document_url)
    if m is None: raise ValueError('invalid OnShape URL')
    return OnShapeDocInfo(m.group(1), m.group(2), m.group(3), m.group(4))


def get_doc_info_url(doc_info: OnShapeDocInfo) -> str:
    return f'https://cad.onshape.com/api/v5/documents/{doc_info.did}'

def get_doc_elements_url(doc_info: OnShapeDocInfo) -> str:
    return f'https://cad.onshape.com/api/v5/documents/d/{doc_info.did}/{doc_info.wv}/{doc_info.wvid}/elements'

def fetch_document_name(api_keys, api_name_url):
    """
    Takes an api_url and the api keys and fetches the document information data
    :param api_keys: the api keys
    :param api_url: the url that the get call will use
    :return: the onshape document name as a string
    """
    # Optional query parameters can be assigned 
    params = {}

    # Define the header for the request 
    headers = {'Accept': 'application/json;charset=UTF-8;qs=0.09',
            'Content-Type': 'application/json'}

    # Putting everything together to make the API request 
    response = requests.get(api_name_url, 
                            params=params, 
                            auth=api_keys,
                            headers=headers)
    json = response.json()
    if 'name' not in json:
        raise ValueError(f'Bad request: {json}')
    
    return json['name']


def fetch_document_elements(api_keys, api_elements_url, doc_info):
    """
    Takes an api_url and the api keys and fetches the document element information data
    :param api_keys: the api keys
    :param api_url: the url that the get call will use
    :return: the onshape document element names as strings in a list
    """
    # Optional query parameters can be assigned 
    params = {'elementId': f'{doc_info.eid}'}

    # Define the header for the request 
    headers = {'Accept': 'application/json;charset=UTF-8;qs=0.09',
            'Content-Type': 'application/json'}

    # Putting everything together to make the API request 
    response = requests.get(api_elements_url, 
                            params=params, 
                            auth=api_keys,
                            headers=headers)
    json = response.json()

    element_names = []
    for dict in json:
        if 'name' not in dict:
            raise ValueError(f'Bad request: {json}')
        element_names.append(dict['name'])

    return element_names