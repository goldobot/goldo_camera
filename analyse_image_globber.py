# python3 analyse_image_globber.py "screenshots/reef*.png" reef
# python3 analyse_image_globber.py "screenshots/harbor*.png" harbor
# python3 analyse_image_globber.py "screenshots/startpos*.png" field

import sys
import glob
from analyse_image import AnalyseImage
import cv2

def main(path, type_img):

    print("type_img", type_img)
    for image_name in glob.glob(path):
        print(image_name)
        image = cv2.imread(image_name)
        anl = AnalyseImage()
        anl.check = True # Uncomment to see only final images
        if type_img == "reef":
            anl.analyse_image(image, 20000, cache=None, scale_percent=0.5, crop_percent=0.5)
        elif type_img == "harbor":
            anl.analyse_image(image, 2000, cache=None, scale_percent=0.5, crop_percent=0.3)
        elif type_img == "field":
            anl.analyse_image(image, 200, cache=None, crop_percent=0.3)
        else:
            print("unknow type_img")
            return

if __name__ == '__main__':
    if len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
