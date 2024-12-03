from paddleocr import PaddleOCR
from Mytool.windows import Windows
import logging
import cv2
from time import sleep
logging.getLogger('ppocr').setLevel(logging.WARNING)

class paddle_ocr():
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, lang='ch',)
        self.windows = Windows()
        self.par_handle=Windows.get_handle('MuMu模拟器12')
        self.child_handle=Windows.get_handleEx(self.par_handle,'MuMuPlayer')
        
    def ocr_text(self,area):
        img=Windows.screenshot(self.child_handle, area)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, img = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)
        result = self.ocr.ocr(img, cls=True)
        return result

if __name__ == '__main__':
    ocr = paddle_ocr()
    while True:
        sleep(2)
        result = ocr.ocr_text([905,37,1229,586])
        for line in result[0]:
            print(line[1][0])