import subprocess
import json


def get_variables(filename='example.scad', url='https://drek.cc/example.scad'):
    # todo: turn the url into a file (ask jeff)

    # throw exception if url isn't good

    # todo: turn scad into scad json
    print(scad_to_scad_json(filename))

    # todo: turn scad json in our json


def scad_to_scad_json(filename):
    subprocess.run(['openscad', 'OpenScad_Files/drop_down_box.scad', '-o', 'OpenSCAD_json_dumps/drop_down_box.param'])
    return open('OpenSCAD_json_dumps/drop_down_box.param', 'r').read()


get_variables(filename="./OpenScad_Files/drop_down_box.scad")
