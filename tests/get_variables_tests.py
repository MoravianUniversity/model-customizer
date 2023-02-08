import unittest
import get_variables


class TestGetVariables(unittest.TestCase):

    def test_scad_json_to_our_json(self):
        input_path = '/Users/colemans/Courses/3d Printing/model-customizer/OpenScad_Files/drop_down_box.scad'
        output_path = '/Users/colemans/Courses/3d Printing/model-customizer/OpenSCAD_json_dumps/drop_down_box.param'
        scad_json = get_variables.scad_to_scad_json(input_path, output_path)
        our_json = get_variables.scad_json_to_our_json(scad_json)
        self.assertEqual(our_json,
                         [
                             {
                                 'name': 'Numbers',
                                 'desc': 'combo box for number',
                                 'default': 2.0,
                                 'group': 'Drop Down box:',
                                 'style': 'dropdown',
                                 'options': [
                                     {'name': '0', 'value': 0.0},
                                     {'name': '1', 'value': 1.0},
                                     {'name': '2', 'value': 2.0},
                                     {'name': '3', 'value': 3.0},
                                 ],
                             }
                         ]
                         )

if __name__ == '__main__':
    unittest.main()
