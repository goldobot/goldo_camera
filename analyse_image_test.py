import unittest
from analyse_image import AnalyseImage
import cv2

class TestAnalyseImage(unittest.TestCase):

    def test_analyse_reef01(self):
        image = cv2.imread("reef01.png")
        camera_support = cv2.imread("camera_support.png")
        anl = AnalyseImage()
        #anl.debug = True # Uncomment to see all images
        #anl.check = True # Uncomment to see only final images
        detected_shapes = anl.analyse_image(image, camera_support=camera_support)
        for shape in detected_shapes:
            print("detected shapes", shape)
        self.assertEqual(len(detected_shapes), 5, "Should be 5")
        self.assertEqual(detected_shapes[0].color, "red", "Should be red")
        self.assertEqual(detected_shapes[1].color, "green", "Should be green")
        self.assertEqual(detected_shapes[2].color, "green", "Should be green")
        self.assertEqual(detected_shapes[3].color, "red", "Should be red")
        self.assertEqual(detected_shapes[4].color, "red", "Should be red")

if __name__ == '__main__':
    unittest.main()

