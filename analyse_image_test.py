import unittest
from analyse_image import AnalyseImage
import cv2

class TestAnalyseImage(unittest.TestCase):

    def test_analyse_reef01(self):
        image = cv2.imread("reef01.png")
        reef01_cache = cv2.imread("reef01_cache.png")
        anl = AnalyseImage()
        #anl.debug = True # Uncomment to see all images
        #anl.color_mask = True # Uncomment to see only images with color mask
        #anl.check = True # Uncomment to see only final images
        detected_shapes = anl.analyse_image(image, 20000, cache=reef01_cache, scale_percent=0.5, crop_percent=0.5)
        for shape in detected_shapes:
            print("detected shapes", shape)
        self.assertEqual(len(detected_shapes), 5, "Should be 5")
        self.assertEqual(detected_shapes[0].color, "red", "Should be red")
        self.assertEqual(detected_shapes[1].color, "green", "Should be green")
        self.assertEqual(detected_shapes[2].color, "green", "Should be green")
        self.assertEqual(detected_shapes[3].color, "red", "Should be red")
        self.assertEqual(detected_shapes[4].color, "red", "Should be red")
        self.assertTrue(detected_shapes[0].up)
        self.assertTrue(detected_shapes[1].up)
        self.assertTrue(detected_shapes[2].up)
        self.assertTrue(detected_shapes[3].up)
        self.assertTrue(detected_shapes[4].up)

    def test_analyse_field01(self):
        image = cv2.imread("field01.jpg")
        field_cache = cv2.imread("field01_cache.jpg")
        anl = AnalyseImage()
        #anl.debug = True # Uncomment to see all images
        #anl.color_mask = True # Uncomment to see only images with color mask
        #anl.check = True # Uncomment to see only final images
        detected_shapes = anl.analyse_image(image, 200, cache=field_cache, crop_percent=0.3)
        for shape in detected_shapes:
            print("detected shapes", shape)

if __name__ == '__main__':
    unittest.main()

