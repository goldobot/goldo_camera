import unittest
from analyse_image import AnalyseImage
import cv2

class TestAnalyseImage(unittest.TestCase):

    def test_analyse_reef(self):
        image = cv2.imread("reef01.png")
        camera_support = cv2.imread("camera_support.png")
        anl = AnalyseImage()
        #anl.debug = True # Uncomment to see all images
        #anl.check = True # Uncomment to see only final images
        detected_shapes = anl.analyse_reef(image, camera_support=camera_support)
        print("detected shapes", detected_shapes)
        self.assertEqual(len(detected_shapes), 3, "Should be 3")
        self.assertEqual(detected_shapes[0][2], "red", "Should be red")
        self.assertEqual(detected_shapes[1][2], "green", "Should be green")
        self.assertEqual(detected_shapes[2][2], "red", "Should be red")

if __name__ == '__main__':
    unittest.main()

