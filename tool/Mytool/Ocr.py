from tool.Mytool.windows import Windows
from ppocronnx.predict_system import TextSystem
import cv2, re
from PIGEON.log import log
from time import sleep
import numpy as np


class pre_hand_img:
    @staticmethod
    def hex_to_rgb(hex_color):
        """
        将十六进制颜色代码转换为RGB元组。
        """
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    @classmethod
    def range_img(cls, img, base_hex, delta_hsv, DEBUG=False):
        """
        根据基准颜色和HSV波动值生成颜色范围掩码
        :param img: 输入图像（BGR格式）
        :param base_hex: 基准颜色（十六进制，如#ff9200）
        :param delta_hsv: HSV各通道的波动值，格式为 (h_delta, s_delta, v_delta)
        """
        # 检查波动值有效性
        if any(d < 0 for d in delta_hsv):
            raise ValueError("HSV波动值必须为非负数")

        # 将基准颜色转换为HSV
        base_rgb = cls.hex_to_rgb(base_hex)
        base_hsv = cls.rgb_to_hsv(*base_rgb)
        h, s, v = map(int, base_hsv)
        print(f"基准颜色: {base_hex}, HSV: {h}, {s}, {v}")
        print(type(h), type(s), type(v))
        # 解包波动值并确保非负
        h_delta, s_delta, v_delta = (max(0, d) for d in delta_hsv)

        # 确保不超过边界值
        l_h = max(0, h - h_delta)
        u_h = min(179, h + h_delta)
        l_s = max(0, s - s_delta)
        u_s = min(255, s + s_delta)
        l_v = max(0, v - v_delta)
        u_v = min(255, v + v_delta)
        print(f"HSV范围: low:{l_h}, {l_s}, {l_v}, up:{u_h}, {u_s}, {u_v}")

        # 创建分割边界值
        lower_hsv = np.array([l_h, l_s, l_v], dtype=np.uint8)  # H最小值（OpenCV中H∈[0,180]）  # S最小值（S∈[0,255]）  # V最小值（V∈[0,255]）
        upper_hsv = np.array([u_h, u_s, u_v], dtype=np.uint8)  # H最大值  # S最大值  # V最大值

        # 转换图像到HSV空间并创建掩码
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_img, lower_hsv, upper_hsv)
        # 应用掩码
        result = cv2.bitwise_and(img, img, mask=mask)
        if DEBUG:
            cv2.imshow("Color Range Detection", result)
            cv2.waitKey(1)
        return result

    @staticmethod
    def rgb_to_hsv(r, g, b):
        # 将RGB转换为BGR格式（OpenCV默认使用BGR）
        bgr = np.uint8([[[b, g, r]]])
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        return hsv[0][0]  # 返回NumPy数组，shape=(3,), dtype=np.uint8


class Ocr(pre_hand_img):
    win = Windows()
    text_recognizer = TextSystem()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):

        pass

    @classmethod
    def range_color_ocr(cls, area, base_hex, delta_hsv):
        img = cls.win.screenshot(area)
        img = cls.range_img(img, base_hex, delta_hsv, DEBUG=True)
        ocr_result = cls.text_recognizer.ocr_single_line(img)
        return ocr_result

    @classmethod
    def ocr(cls, area: list | tuple, range_color=None, debug=False) -> str:
        try:
            # 直接获取灰度图像，减少一次颜色转换操作
            ocr_img = cls.win.screenshot(area)
            # 图像预处理
            if range_color:
                ocr_img = cls.range_img(ocr_img, *range_color)
            # 图像识别
            ocr_result = cls.text_recognizer.ocr_single_line(ocr_img)
            if debug:
                print(ocr_result)
                cv2.imshow("ocr_img", ocr_img)
                cv2.waitKey(500)
            if ocr_img is None:
                raise ValueError("无法获取窗口截图")
            # ocr_img = cv2.cvtColor(ocr_img, cv2.COLOR_BGRA2GRAY)

            return ocr_result
        except Exception as e:
            log.error(f"OCR操作失败: {e}")
            return None

    @classmethod
    def ocr_by_re(cls, area: list | tuple, pattern: str, threshold=0.9, try_times=5, range_color=None, debug=False):
        t_t = 0
        try:
            while t_t < try_times:
                sleep(0.2)
                res = cls.ocr(area, range_color=range_color, debug=debug)
                log.file(f"尝试次数: {t_t}, 识别结果: {res}")
                if res[1] < threshold:
                    t_t += 1
                    continue
                text = re.sub(r"\s+", "", res[0])  # 去除空格
                if re_res := re.search(pattern, text, re.VERBOSE):
                    return re_res
                else:
                    t_t += 1

        except Exception as e:
            log.error(f"OCR_by_re操作失败: {e}")
        pass

    @classmethod
    def ocr_numbers(cls, area: list) -> str:
        try:
            if ocr_res := cls.ocr(area):
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
