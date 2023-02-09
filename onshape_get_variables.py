import requests 
import json 

import os
from dotenv import load_dotenv


# TODO: Implement function to build correct variables api_url using format, change function to take did wid eid instead

def get_variables(api_url='https://cad.onshape.com/api/v5/variables/d/3c26b3daca62374f0e255d71/w/f85838c02b4f9c69defdf995/e/80a526943d7399f491201813/variables'):
    """
    Generates our JSON format based on a url. Starts by getting the onshape document variables, turning them into json, 
    and then formatting it correctly for our database.
    :param api_url: the url of the scad file
    :return: the final json as a string
    """
    load_dotenv()  # take environment variables from .env.

    # Use the API keys generated from the Onshape developer portal 
    api_keys = (os.getenv('ACCESS_KEY'), os.getenv('SECRET_KEY'))

    # TODO: throw exception if url isn't good

    onshape_json = fetch_onshape_document_variables_json(api_keys, api_url)
    return onshape_json_to_our_json(onshape_json) 


def fetch_onshape_document_variables_json(api_keys, api_url):
    """
    Takes an api_url and the api keys and fetches the variable document data
    :param api_url: the url that variables will be taken from
    :param api_keys: the api keys
    :return: the onshape document variables as a JSON
    """
    # Optional query parameters can be assigned 
    params = {'includeValuesAndReferencedVariables':True}

    # Define the header for the request 
    headers = {'Accept': 'application/json;charset=UTF-8;qs=0.09',
            'Content-Type': 'application/json'}

    # Putting everything together to make the API request 
    response = requests.get(api_url, 
                            params=params, 
                            auth=api_keys, 
                            headers=headers)

    return response.json()[0]['variables']


def onshape_json_to_our_json(onshape_json):
    """
    Takes the JSON from the scad file and formats it to our template
    :param onshape_json: the JSON generated by the call to onshape
    :return: Our JSON as a dict
    """

    our_json = []
    for i, current_onshape_var in enumerate(onshape_json):
        # the elements attached to every variable
        name = current_onshape_var['name']
        desc = current_onshape_var['description']
        # default = current_onshape_var['initial']
        # group = current_onshape_var['group']
        value, label = current_onshape_var['value'].split(' ')

        if label == 'meters':
            value = float(value)*1000 # convert to mm from meters
            label = 'mm'

        our_json.append(
            {
                'name': name,
                'desc': desc,
                # 'default': default,
                # 'group': group,
                'value': value,
                'label': label
            }
        )

        # TODO: add functionality for groups and extra options within onshape description box
        # need to find out how to create groups, this method seems to completely avoid folders

        # # Extra Options
        # for extra in current_onshape_var:
        #     # The drop-down menu
        #     if extra == 'options':
        #         our_json[i]['style'] = 'dropdown'
        #         # todo: ask if this format is okay
        #         our_json[i]['options'] = current_onshape_var['options']

    # todo: change this and tests to output a string
    return our_json