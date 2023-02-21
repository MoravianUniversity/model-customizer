import unittest
import get_variables


class TestGetVariables(unittest.TestCase):

    def test_scad_json_to_our_json_drop_down(self):
        our_json = self.get_our_json(
            '/Users/colemans/Courses/3d Printing/model-customizer/OpenScad_Files/drop_down_box.scad',
        )
        self.assertEqual(our_json,
                         [
                             {
                                 'name': 'Numbers',
                                 'desc': 'combo box for number',
                                 'default': 2.0,
                                 'group': 'Drop Down box:',
                                 'style': 'dropdown',
                                 'options': {
                                     '0': 0.0,
                                     '1': 1.0,
                                     '2': 2.0,
                                     '3': 3.0,
                                 },
                             }
                         ]
                         )

    def test_scad_json_to_our_json_slider(self):
        our_json = self.get_our_json(
            '/Users/colemans/Courses/3d Printing/model-customizer/OpenSCAD_Files/sliders.scad',
        )
        self.assertEqual(our_json,
                         [
                             {
                                 'name': 'slider',
                                 'desc': 'slider widget for number',
                                 'default': 34,
                                 'group': 'Slider',
                                 'style': 'slider',
                                 'min': 10,
                                 'max': 100,
                                 'inc': 1
                             }
                         ]
                         )

    def test_scad_json_to_our_json_textbox(self):
        our_json = self.get_our_json(
            '/Users/colemans/Courses/3d Printing/model-customizer/OpenSCAD_Files/textbox.scad',
        )
        self.assertEqual(our_json,
                         [
                             {
                                 'name': 'String',
                                 'desc': 'Text box for string',
                                 'default': 'hello',
                                 'group': 'Textbox',
                                 'style': 'textbox',
                                 'max_len': 8,
                             }
                         ]
                         )

    def test_scad_json_to_our_json_checkbox(self):
        our_json = self.get_our_json(
            '/Users/colemans/Courses/3d Printing/model-customizer/OpenSCAD_Files/checkbox.scad',
        )
        self.assertEqual(our_json,
                         [
                             {
                                 'name': 'Variable',
                                 'desc': 'description',
                                 'default': True,
                                 'group': 'Checkbox',
                                 'style': 'checkbox',
                             }
                         ]
                         )

    @staticmethod
    def get_our_json(input_path):
        scad_json = get_variables.scad_to_scad_json(input_path)
        our_json = get_variables.scad_json_to_our_json(scad_json)
        return our_json

    def test_is_onshape(self):
        self.assertEqual(
            True,
            get_variables.is_onshape('https://cad.onshape.com/documents'
                                     '/c99362a81274b324031e8a14/w/9ae465f95c7a664af9bf7cde/e/6cb81e95a38e589a1fc4dfe5')
        )

        self.assertEqual(False, get_variables.is_onshape('https://drek.cc/dl/example2.scad'))
        self.assertEqual(False, get_variables.is_onshape(
            'file:///Users/colemans/Courses/3d%20Printing/model-customizer/OpenSCAD_Files/checkbox.scad'))
        self.assertEqual(False, get_variables.is_onshape('this is not a url'))


if __name__ == '__main__':
    unittest.main()
