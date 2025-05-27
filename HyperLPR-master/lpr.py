import cv2
import numpy as np
from models.fine_mapping import build_finemapping_model
from models.seq_recognition import build_seq_recognition_model
from utils.decode import fastdecode
from utils.plate_color import detect_plate_color


class LPR:
    def __init__(self, model_detection_path, model_finemapping_path, model_seq_rec_path):
        self.watch_cascade = cv2.CascadeClassifier(model_detection_path)
        self.modelFineMapping = build_finemapping_model()
        self.modelFineMapping.load_weights(model_finemapping_path)
        self.modelSeqRec = build_seq_recognition_model(model_seq_rec_path)

    def computeSafeRegion(self, shape, bounding_rect):
        top = max(bounding_rect[1], 0)
        bottom = min(bounding_rect[1] + bounding_rect[3], shape[0])
        left = max(bounding_rect[0], 0)
        right = min(bounding_rect[0] + bounding_rect[2], shape[1])
        return [left, top, right - left, bottom - top]

    def cropImage(self, image, rect):
        x, y, w, h = self.computeSafeRegion(image.shape, rect)
        return image[y:y+h, x:x+w]

    def detectPlateRough(self, image_gray, resize_h=720, en_scale=1.08, top_bottom_padding_rate=0.05):
        if top_bottom_padding_rate > 0.2:
            raise ValueError("top_bottom_padding_rate > 0.2")
        height = image_gray.shape[0]
        padding = int(height * top_bottom_padding_rate)
        scale = image_gray.shape[1] / float(image_gray.shape[0])
        image = cv2.resize(image_gray, (int(scale * resize_h), resize_h))
        image_color_cropped = image[padding:resize_h - padding, 0:image.shape[1]]
        image_gray = cv2.cvtColor(image_color_cropped, cv2.COLOR_RGB2GRAY)
        watches = self.watch_cascade.detectMultiScale(
            image_gray, en_scale, 2, minSize=(36, 9), maxSize=(36*40, 9*40))
        cropped_images = []
        for (x, y, w, h) in watches:
            x -= w * 0.14
            w += w * 0.28
            y -= h * 0.15
            h += h * 0.3
            cropped = self.cropImage(image_color_cropped, (int(x), int(y), int(w), int(h)))
            cropped_images.append([cropped, [x, y + padding, w, h]])
        return cropped_images

    def finemappingVertical(self, image, rect):
        resized = cv2.resize(image, (66, 16))
        resized = resized.astype(float) / 255
        res_raw = self.modelFineMapping.predict(np.array([resized]))[0]
        res = (res_raw * image.shape[1]).astype(int)
        H, T = res
        H = max(H - 3, 0)
        T = min(T + 2, image.shape[1] - 1)
        rect[2] -= rect[2] * (1 - res_raw[1] + res_raw[0])
        rect[0] += res[0]
        image = image[:, H:T+2]
        image = cv2.resize(image, (136, 36))
        return image, rect

    def recognizeOne(self, src):
        x_temp = cv2.resize(src, (164, 48))
        x_temp = x_temp.transpose(1, 0, 2)
        y_pred = self.modelSeqRec.predict(np.array([x_temp]))
        y_pred = y_pred[:, 2:, :]  # 忽略前两个时间步
        return fastdecode(y_pred)

    def SimpleRecognizePlateByE2E(self, image):
        rough_plates = self.detectPlateRough(image, image.shape[0], top_bottom_padding_rate=0.1)
        res_set = []
        for plate, rect in rough_plates:
            refined_img, rect_refined = self.finemappingVertical(plate, rect)
            plate_text, confidence = self.recognizeOne(refined_img)
            plate_color = detect_plate_color(refined_img)
            res_set.append([plate_text, confidence, rect_refined, plate_color])
        return res_set
