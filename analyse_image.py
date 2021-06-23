import cv2
import numpy as np
import os
import json

from scipy import ndimage as ndi
from skimage.segmentation import watershed
from skimage.feature import peak_local_max
import matplotlib.pyplot as plt

from recordtype import recordtype
box = recordtype("box", "x y w h up color")
pt = recordtype("pt", "x y")

blue = (255, 0, 0)

class AnalyseImage():

    def __init__(self):

        self.debug = False # Pop up all images including intermediate ones.
        self.check = False # Pop up only final images.
        self.color = {
            "green": {
                "hsv_low": [80, 20, 20],
                "hsv_high": [100, 255, 255]
            },
            "red": {
                "hsv_low": [165, 20, 20],
                "hsv_high": [185, 255, 255]
            }
        }

        if os.path.exists("analyse_image.json"):
            with open("analyse_image.json", "r") as read_file:
                self.color = json.load(read_file)
        print(self.color)

    def analyse_image(self, image, min_area, scale_percent=1., crop_percent=False, cache=None):

        image_bgr = image.copy()
        image_bgr = self._scale_and_crop_image(image_bgr, "image", scale_percent=scale_percent, crop_percent=crop_percent)

        if cache is not None:
            cache_bgr = cache.copy()
            cache_bgr = self._scale_and_crop_image(cache_bgr, "cache", scale_percent=scale_percent, crop_percent=crop_percent)
            cache_gray = cv2.cvtColor(cache_bgr, cv2.COLOR_BGR2GRAY)
            if self.debug:
                cv2.imshow("cache gray", cache_gray)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            _, cache_mask = cv2.threshold(cache_gray, 10, 255, cv2.THRESH_BINARY)
            if self.debug:
                cv2.imshow("camera mask", cache_mask)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            image_bgr = cv2.bitwise_and(image_bgr, image_bgr, mask=cache_mask)
            if self.debug:
                cv2.imshow("image with camera mask", image_bgr)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

        shapes = []
        for key in self.color:
            try:
                hsv_low, hsv_high =  self.color[key]["hsv_low"], self.color[key]["hsv_high"]
                shapes += self._detect_shapes(image_bgr.copy(), hsv_low, hsv_high, key, min_area)
            except:
                pass # Detection (watershed, ...) may break: don't break, go on error.
        shapes.sort(key=lambda shape: shape.x)

        if self.debug or self.check:
            for shape in shapes:
                cv2.rectangle(image_bgr, (shape.x, shape.y), (shape.x+shape.w, shape.y+shape.h), blue, 2)
                cv2.putText(image_bgr, "+", (shape.x+shape.w//2, shape.y+shape.h//2), cv2.FONT_HERSHEY_SIMPLEX, 0.6, blue, 2)
            cv2.imshow("image with final box", image_bgr)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return shapes

    def _scale_and_crop_image(self, image, name, scale_percent=False, crop_percent=False):

        if self.debug:
            cv2.imshow("%s"%name, image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        resized_image = image
        if scale_percent:
            height = int(image.shape[0] * scale_percent)
            width = int(image.shape[1] * scale_percent)
            resized_image = cv2.resize(image, (width, height))
            if self.debug:
                cv2.imshow("resized %s"%name, resized_image)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

        cropped_image = resized_image
        if crop_percent:
            height = int(resized_image.shape[0])
            width = int(resized_image.shape[1])
            x_crop, y_crop = 0, int(height * crop_percent)
            cropped_image = resized_image[y_crop:height-1, x_crop:width-1]
            if self.debug:
                cv2.imshow("cropped %s"%name, cropped_image)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

        return cropped_image

    def _detect_shapes(self, image_bgr, hsv_low, hsv_high, color, min_area):

        shapes = []

        hsv_image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
        if self.debug:
            cv2.imshow("%s hsv image"%color, hsv_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        hsv_image = cv2.GaussianBlur(hsv_image, (5, 5), 0)
        if self.debug:
            cv2.imshow("%s blurred hsv image"%color, hsv_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        color_mask = cv2.inRange(hsv_image, np.array(hsv_low), np.array(hsv_high))
        if self.debug:
            cv2.imshow("%s color mask"%color, color_mask)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            if cv2.contourArea(cnt) < min_area:
                continue
            x, y, w, h = cv2.boundingRect(cnt)
            self._detect_shapes_in_shape(color_mask, (x, y, w, h), color, image_bgr.copy(), shapes)

        return shapes

    def _detect_shapes_in_shape(self, color_mask, anchor, color, image_bgr, shapes):

        x, y, w, h = anchor[0], anchor[1], anchor[2], anchor[3]
        color_mask_zoom = color_mask[y:y+h, x:x+w]
        if self.debug:
            cv2.imshow("%s color mask zoom"%color, color_mask_zoom)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        kernel = np.ones((5, 5), np.uint8)
        color_mask_zoom = cv2.dilate(color_mask_zoom, kernel, iterations=4) # Suppress top circle of the cup to improve watershed.
        if self.debug:
            cv2.imshow("%s color mask zoom dilated"%color, color_mask_zoom)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        distance = ndi.distance_transform_edt(color_mask_zoom)
        if self.debug:
            cv2.imshow("%s distance map"%color, distance)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        peak_coords = peak_local_max(distance, min_distance=40, labels=color_mask_zoom)
        #if self.debug:
        #    _, axis = plt.subplots(1, 1)
        #    axis.imshow(distance, cmap=plt.cm.gray)
        #    axis.plot(peak_coords[:, 1], peak_coords[:, 0], 'r.')
        #    axis.set_title("%s distance map : markers"%color)
        #    plt.show()
        if len(peak_coords) == 0:
            info = self._merge_or_append_shape(box(x, y, w, h, h > w, color), shapes) # No peak: add as default shape.
            if self.debug:
                cv2.imshow("%s image with %s box"%(color, info), image_bgr)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            return # Nothing found : keep on with watershed would crash.

        peak_coords_mask = np.zeros(distance.shape, dtype=bool)
        peak_coords_mask[tuple(peak_coords.T)] = True
        markers, _ = ndi.label(peak_coords_mask)

        labels = watershed(-distance, markers, mask=color_mask_zoom)
        for label in np.unique(labels):
            if label == 0: # Background.
                continue # Skip.

            mask = np.zeros(color_mask_zoom.shape, dtype="uint8")
            mask[labels == label] = 255
            cnts, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cnt = max(cnts, key=cv2.contourArea)
            xl, yl, wl, hl = cv2.boundingRect(cnt)
            if wl < w/3:
                continue

            xcl, ycl = x+xl, y+yl
            cv2.rectangle(image_bgr, (xcl, ycl), (xcl+wl, ycl+hl), blue, 2)
            xcl, ycl = xcl+wl//2, ycl+hl//2
            cv2.putText(image_bgr, "+", (xcl, ycl), cv2.FONT_HERSHEY_SIMPLEX, 0.6, blue, 2)

            xcl, ycl = x+xl, y+yl
            info = self._merge_or_append_shape(box(xcl, ycl, wl, hl, hl > wl, color), shapes)
            if self.debug:
                cv2.imshow("%s image with %s box"%(color, info), image_bgr)
                cv2.waitKey(0)
                cv2.destroyAllWindows()

    def _merge_or_append_shape(self, box, shapes):

        for shape in shapes:
            if shape.x-shape.w//2 <= box.x <= shape.x+shape.w//2:
                if box.y+box.h//2 >= shape.y-shape.h//2:
                    shape = self._merge_shape(box, shape) # Replace shape.
                    return "extended"
                if box.y-box.h//2 <= shape.y+shape.h//2:
                    shape = self._merge_shape(box, shape) # Replace shape.
                    return "extended"
                if box.y+box.h//2 <= shape.y+shape.h//2 and box.y-box.h//2 >= shape.y-shape.h//2:
                    return "merged" # Box in contained in shape.

        shapes.append(box) # Add shape.
        return "appended"

    def _merge_shape(self, box, shape):

        topB, downB = pt(box.x+box.w//2, box.y+box.h//2), pt(box.x-box.w//2, box.y-box.h//2)
        topS, downS = pt(shape.x+shape.w//2, shape.y+shape.h//2), pt(shape.x-shape.w//2, shape.y-shape.h//2)

        top = topB
        if topS.x > top.x:
            top.x = topS.x
        if topS.y > top.y:
            top.y = topS.y
        down = downB
        if downS.x < down.x:
            down.x = downS.x
        if downS.y < down.y:
            down.y = downS.y

        modif_shape = shape
        modif_shape.x = int(0.5*(top.x-down.x))+1
        modif_shape.y = int(0.5*(top.y-down.y))+1
        modif_shape.w = int(top.x-down.x)
        modif_shape.h = int(top.y-down.y)
        modif_shape.up = modif_shape.h > modif_shape.w

        return modif_shape
