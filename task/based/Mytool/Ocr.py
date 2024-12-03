from task.based.Mytool.windows import Windows
from ppocronnx.predict_system import TextSystem
import cv2
from PIGEON.log import Log

log = Log()


class Ocr:
    par_handle = Windows.get_handle("MuMu模拟器12")
    child_handle = Windows.get_handleEx(par_handle, "MuMuPlayer")
    text_recognizer = TextSystem()

    def __init__(self):
        pass

    @classmethod
    def ocr(cls, area: list, debug=False) -> str:
        try:
            # 直接获取灰度图像，减少一次颜色转换操作
            ocr_img = Windows.screenshot(cls.child_handle, area)
            # ocr_img = cv2.resize(ocr_img, (0,0), fx=2, fy=1)
            # _, ocr_img = cv2.threshold(ocr_img,127,255,cv2.THRESH_BINARY)
            if debug:
                cv2.imshow("ocr_img", ocr_img)
                cv2.waitKey(0)
            if ocr_img is None:
                raise ValueError("无法获取窗口截图")
            # ocr_img = cv2.cvtColor(ocr_img, cv2.COLOR_BGRA2GRAY)
            ocr_result = cls.text_recognizer.ocr_single_line(ocr_img)
            return ocr_result
        except Exception as e:
            log.error(f"OCR操作失败: {e}")
            return None

    @classmethod
    def ocr_numbers(cls, area: list) -> str:
        try:
            if ocr_res := self.ocr(area):
                return ocr_res
        except Exception as e:
            log.error(f"OCR_numbers操作失败: {e}")


if __name__ == "__main__":
    ocr = Ocr()
    shot_img = ocr.screenshot(ocr.child_handle, [457, 146, 841, 256])
    ret, binary_image = cv2.threshold(shot_img, 128, 255, cv2.THRESH_BINARY)
    print(ret)
    res = ocr.text_recognizer.ocr_single_line(binary_image)
    print(res)
    pass
