import os
import subprocess
import json
import tempfile
import urllib.request


def get_variables(url):
    """
    Generates our JSON format based on a url. Starts by getting the scad file, turning it into json, and then formatting
    it correctly for our database.
    :param url: the url of the scad file
    :return: the final json as a string
    """
    # todo: turn the url into a file (ask jeff)
    # create the file
    open('temp_input_file','w').close()

    with open('temp_input_file', 'r') as input_path:
        urllib.request.urlretrieve(url, input_path.name)
    # todo: make this work with file urls
    # todo: use temp files
    # todo: throw exception if url isn't good

    scad_json = scad_to_scad_json(input_path)
    os.remove('temp_input_file')
    return scad_json_to_our_json(scad_json)


def scad_to_scad_json(input_path):
    """
    Takes a scad file and returns its customizer json as a string
    :param input_path: the scad file
    :param output_path: the location of the output json
    :return: the output json as a string
    """
    process = subprocess.Popen(['openscad', input_path.name, '-o', 'temp_output_file.param'])
    process.wait()
    scad_json_file = open('temp_output_file.param', 'r')
    read = json.load(scad_json_file)
    os.remove('temp_output_file.param')
    return read


def scad_json_to_our_json(scad_json):
    """
    Takes the JSON from the scad file and formats it to our template
    :param scad_json: the JSON generated by scad
    :return: Our JSON as a dict
    """
    # This is the only part of the json that has customizer variables
    scad_json = scad_json['parameters']

    our_json = []
    for current_scad_var in scad_json:
        # the elements attached to every variable
        variable = {
            'name': (current_scad_var['name']),
            'desc': (current_scad_var.get('caption', '')),
            'default': (current_scad_var['initial']),
            'group': (current_scad_var['group']),
        }

        our_json.append(variable)

        # So I can use keys and contains on it
        current_scad_var = dict(current_scad_var)

        # Extra Options
        # Drop Down Menu
        if 'options' in current_scad_var:
            variable['style'] = 'dropdown'
            # todo: ask if this format is okay (no, make it a dict and nicer)
            variable['options'] = current_scad_var['options']

        # TODO: differentiate from numbox
        # Slider
        if 'min' in current_scad_var:
            variable['style'] = 'slider'
            variable['min'] = current_scad_var['min']
            variable['max'] = current_scad_var['max']
            variable['inc'] = current_scad_var['step']

        # Textbox
        if 'maxLength' in current_scad_var:
            variable['style'] = 'textbox'
            variable['max_len'] = current_scad_var['maxLength']

        # Checkbox
        if current_scad_var['type'] == 'boolean':
            variable['style'] = 'checkbox'

    return our_json


print(get_variables('https://drek.cc/dl/example2.scad'))
