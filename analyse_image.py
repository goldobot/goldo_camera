import cv2
import numpy as np

class AnalyseImage():

    def __init__(self):
        self.debug = False

    def analyse_reef(self, image):

        image = self._scale_and_crop_image(image)

        low_green, high_green = np.array([80, 20, 20]), np.array([100, 255, 255])
        shapes_green = self._detect_shapes(image, low_green, high_green, "green")

        low_red, high_red = np.array([165, 20, 20]), np.array([185, 255, 255])
        shapes_red = self._detect_shapes(image, low_red, high_red, "red")

        shapes = shapes_green + shapes_red
        shapes.sort(key=lambda shape: shape[0])

        return shapes

    def _scale_and_crop_image(self, image, scale_percent=50):

        if self.debug:
            cv2.imshow("image", image)
            cv2.waitKey(0)
        height = int(image.shape[0] * scale_percent / 100)
        width = int(image.shape[1] * scale_percent / 100)
        resized_image = cv2.resize(image, (width, height))
        if self.debug:
            cv2.imshow("resized image", resized_image)
            cv2.waitKey(0)
        height = int(resized_image.shape[0])
        width = int(resized_image.shape[1])
        x_crop, y_crop = 0, height//2
        cropped_image = resized_image[y_crop:height-1, x_crop:width-1]
        if self.debug:
            cv2.imshow("cropped image", cropped_image)
            cv2.waitKey(0)

        return cropped_image

    def _detect_shapes(self, image, low, high, color):

        shapes = []

        image_cp = image.copy()
        hsv_image = cv2.cvtColor(image_cp, cv2.COLOR_BGR2HSV)
        if self.debug:
            cv2.imshow("%s hsv image"%color, hsv_image)
            cv2.waitKey(0)
        hsv_image = cv2.GaussianBlur(hsv_image, (5, 5), 0)
        if self.debug:
            cv2.imshow("%s blurred hsv image"%color, hsv_image)
            cv2.waitKey(0)
        color_mask = cv2.inRange(hsv_image, low, high)
        if self.debug:
            cv2.imshow("%s mask"%color, color_mask)
            cv2.waitKey(0)
        masked_image = cv2.bitwise_and(image_cp, image_cp, mask=color_mask)
        if self.debug:
            cv2.imshow("%s masked image"%color, masked_image)
            cv2.waitKey(0)

        contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for ctn in contours:
            if cv2.contourArea(ctn) < 20000:
                continue
            x, y, w, h = cv2.boundingRect(ctn)
            cv2.rectangle(image_cp, (x, y), (x+w, y+h), (255, 0, 0), 2)
            shapes.append((x, y, color))
        if self.debug:
            cv2.imshow("%s image with rectangle"%color, image_cp)
            cv2.waitKey(0)
        shapes.sort(key=lambda shape: shape[0])

        return shapes
