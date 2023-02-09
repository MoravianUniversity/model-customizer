import subprocess
import json
import urllib.request


def get_variables(url='https://drek.cc/example.scad'):
    """
    Generates our JSON format based on a url. Starts by getting the scad file, turning it into json, and then formatting
    it correctly for our database.
    :param url: the url of the scad file
    :return: the final json as a string
    """
    # todo: turn the url into a file (ask jeff)
    input_path = 'example.scad'

    # todo: throw exception if url isn't good

    scad_json = scad_to_scad_json(input_path)
    return scad_json_to_our_json(scad_json)


def scad_to_scad_json(input_path, output_path):
    """
    Takes a scad file and returns its customizer json as a string
    :param input_path: the scad file
    :param output_path: the location of the output json
    :return: the output json as a string
    """
    subprocess.run(['openscad', input_path, '-o', output_path])

    scad_json_file = open(output_path, 'r')
    scad_json = scad_json_file.read()
    scad_json_file.close()

    return scad_json


def scad_json_to_our_json(scad_json):
    """
    Takes the JSON from the scad file and formats it to our template
    :param scad_json: the JSON generated by scad
    :return: Our JSON as a dict
    """
    scad_json = json.loads(scad_json)

    # This is the only part of the json that has customizer variables
    scad_json = scad_json['parameters']

    our_json = []
    for i, current_scad_var in enumerate(scad_json):
        # the elements attached to every variable

        our_json.append(
            {
                'name': (current_scad_var['name']),
                'desc': (current_scad_var['caption']),
                'default': (current_scad_var['initial']),
                'group': (current_scad_var['group']),
            }
        )

        # So I can use keys and contains on it
        current_scad_var = dict(current_scad_var)

        # Extra Options
        # Drop Down Menu
        if current_scad_var.__contains__('options'):
            our_json[i]['style'] = 'dropdown'
            # todo: ask if this format is okay
            our_json[i]['options'] = current_scad_var['options']

        # TODO: differentiate from numbox
        # Slider
        if current_scad_var.__contains__('min'):
            our_json[i]['style'] = 'slider'
            our_json[i]['min'] = current_scad_var['min']
            our_json[i]['max'] = current_scad_var['max']
            our_json[i]['inc'] = current_scad_var['step']

        # Textbox
        if current_scad_var.__contains__('maxLength'):
            our_json[i]['style'] = 'textbox'
            our_json[i]['max_len'] = current_scad_var['maxLength']

        # Checkbox
        if current_scad_var['type'] == 'boolean':
            our_json[i]['style'] = 'checkbox'

    return our_json
