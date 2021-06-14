import unittest
from analyse_image import AnalyseImage

class TestAnalyseImage(unittest.TestCase):

    def test_analyse_reef(self):
        anl = AnalyseImage()
        res = anl.analyse_reef()
        self.assertEqual(len(res), 0, "Should be 0")

if __name__ == '__main__':
    unittest.main()

