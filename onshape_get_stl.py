import requests 
import re
from collections import namedtuple
from tempfile import NamedTemporaryFile


OnShapeDocInfo = namedtuple("OnShapeDocInfo", ('did', 'wv', 'wvid', 'eid'))


def download_file(url, local_filename):
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
    return local_filename


def get_stl(document_url: str, variables: dict = None):
    """
    Generates our JSON format based on a url. Starts by getting the onshape document variables, turning them into json, 
    and then formatting it correctly for our database.
    :param document_url: the url of the onshape document
    :return: the final json as a string
    """
    # Use the API keys generated from the Onshape developer portal 
    stl_url = get_stl_url(get_doc_info(document_url))
    link = fetch_onshape_document_stl(stl_url)["href"]
    with NamedTemporaryFile('rb', suffix = '.stl', delete=False) as output_file:
        print(output_file.name)
        download_file(link, output_file.name)


def get_doc_info(document_url: str) -> OnShapeDocInfo:
    """
    Builds a special variable url in order to fetch the variable data from the document through the Onshape API
    :param document_url: the url of the onshape document
    """
    m = re.match(r"^https?://cad.onshape.com/documents/([0-9a-f]+)/([wv])/([0-9a-f]+)/e/([0-9a-f]+)", document_url)
    if m is None: raise ValueError('invalid OnShape URL')
    return OnShapeDocInfo(m.group(1), m.group(2), m.group(3), m.group(4))


def get_stl_url(doc_info: OnShapeDocInfo) -> str:
    return f'https://cad.onshape.com/api/documents/d/{doc_info.did}/{doc_info.wv}/{doc_info.wvid}/e/{doc_info.eid}/export'


def fetch_onshape_document_stl(api_url):
    """
    Takes an api_url and the api keys and fetches the variable document data
    :param api_url: the url that variables will be taken from
    :param api_keys: the api keys
    :return: the onshape document variables as a JSON
    """

    # Define the header for the request 
    headers = {'Accept': 'application/json;charset=UTF-8;qs=0.09',
            'Content-Type': 'application/json'}

    json = {
    "format": "STL",
    "destinationName": "output",
    "mode": "binary",
    "scale": "1.0",
    "resolution": "medium",
    "units": "millimeter",
    "grouping": "true",
    "angleTolerance": "0.1090830782496456",
    "chordTolerance": "0.12",
    "minFacetWidth": "0.254",
    "triggerAutoDownload": "true",
    "storeInDocument": "false",
    "linkDocumentId": "3c26b3daca62374f0e255d71",
    "linkDocumentWorkspaceId": "ce9955d5aaf2d5b4f25592e8",
    "configuration": ""
}

    # Putting everything together to make the API request 
    response = requests.post(api_url, 
                            json = json,
                            headers=headers)
    response.raise_for_status()
    return response.json()