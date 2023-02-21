import contextlib
import os
import subprocess
import json
from tempfile import NamedTemporaryFile
from urllib.request import urlretrieve
from urllib.parse import urlparse, unquote
from typing import List, Dict, Any


def is_onshape(url: str) -> bool:
    return urlparse(url).hostname == 'cad.onshape.com'


@contextlib.contextmanager
def get_scad_file(url_or_path: str) -> str:
    url_parts = urlparse(url_or_path)

    # Get the source file
    input_file = None
    try:
        if url_parts.scheme.startswith('http'):
            input_file = NamedTemporaryFile()
            source = input_file.name
            # todo: throw exception if url isn't good
            urlretrieve(url_or_path, source)
        elif url_parts.scheme in ('file', ''):
            source = unquote(url_parts.path)
            if not os.path.exists(source):
                raise Exception("Source file does not exist")
        else:
            raise Exception("Unsupported source URL")
        yield source
    finally:
        if input_file is not None:
            input_file.close()


def get_variables(url: str) -> List[Dict[str, Any]]:
    """
    Generates our JSON format based on a url. Starts by getting the scad file, turning it into json, and then formatting
    it correctly for our database.
    :param url: the url of the scad file
    :return: the final json as a string
    """
    with get_scad_file(url) as source:
        scad_json = scad_to_scad_json(source)
        return scad_json_to_our_json(scad_json)


def scad_to_scad_json(input_path: str) -> dict:
    """
    Takes a scad file and returns its customizer json as a string
    :param input_path: the scad file
    :return: the output json as a string
    """
    with NamedTemporaryFile('r', suffix=".param") as tmp:
        subprocess.run(['openscad-nightly', input_path, '-o', tmp.name]).check_returncode()
        return json.load(tmp)


def scad_json_to_our_json(scad_json: dict):
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
            variable['options'] = {item['name']: item['value'] for item in current_scad_var['options']}

        # TODO: differentiate from numbox
        # Slider
        if 'min' in current_scad_var and 'max' in current_scad_var:
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


def get_stl(url_or_path: str, variables: dict):
    """
    Creates an stl file with the variables in the dict
    :param url_or_path: the url or path of an openscad file
    :param variables: a dict of variable names and values
    :return: idk
    """
    variable_json = {
        "parameterSets": {
            "variableSet": variables
        },
        "fileFormatVersion": "1"
    }

    with (get_scad_file(url_or_path) as scad_file,
          NamedTemporaryFile('w', suffix=".json") as tmp_json,
          NamedTemporaryFile('r', suffix='.stl', delete=False) as tmp_stl):
        tmp_json.write(json.dumps(variable_json))
        tmp_json.flush()

        # openscad --enable=customizer -o model-2.stl -p parameters.json -P model-2 model.scad
        subprocess.run([
            'openscad-nightly', '--enable=customizer',
            '-o', tmp_stl.name,
            '-p', tmp_json.name,
            '-P', 'variableSet',  # IDK why this is here
            scad_file,
        ])

    return None  # The binary? the file path?


def main():
    # previous testing stuff
    # print(get_variables('https://drek.cc/dl/example2.scad'))
    # print(get_variables('file:///Users/colemans/Courses/3d%20Printing/model-customizer/OpenSCAD_Files/checkbox.scad'))
    # is_onshape(
    #     "https://cad.onshape.com/documents/c99362a81274b324031e8a14/w/9ae465f95c7a664af9bf7cde/e/6cb81e95a38e589a1fc4dfe5")

    # get_stl('https://drek.cc/dl/bread-cutter-assembled.scad', {
    #     "slice_thickness": 100,
    # })

    # actual main
    # get url somehow
    url = 'https://drek.cc/dl/example2.scad'

    ## todo: move url verification down here
    if is_onshape(url):
        pass
        # Zack does something
    else:
        print(get_variables(url))


if __name__ == '__main__':
    main()
