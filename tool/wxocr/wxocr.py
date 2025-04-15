import cv2
import os
import re
import sys
from time import sleep
import numpy as np

# 导入自定义模块
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(path)
from tool.Mytool.windows import Windows
from tool.wxocr import wcocr

wx_dir = r"ver4\wx"
ocr_dir = r"ver4\ocr\wxocr.dll"
# 获取当前目录
current_file_dir = os.path.dirname(os.path.realpath(__file__))
# 拼接路径
wx_dir = os.path.join(current_file_dir, wx_dir)
ocr_dir = os.path.join(current_file_dir, ocr_dir)


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

        # print(type(h), type(s), type(v))
        # 解包波动值并确保非负
        h_delta, s_delta, v_delta = (max(0, d) for d in delta_hsv)

        # 确保不超过边界值
        l_h = max(0, h - h_delta)
        u_h = min(179, h + h_delta)
        l_s = max(0, s - s_delta)
        u_s = min(255, s + s_delta)
        l_v = max(0, v - v_delta)
        u_v = min(255, v + v_delta)

        # 创建分割边界值
        lower_hsv = np.array([l_h, l_s, l_v], dtype=np.uint8)  # H最小值（OpenCV中H∈[0,180]）  # S最小值（S∈[0,255]）  # V最小值（V∈[0,255]）
        upper_hsv = np.array([u_h, u_s, u_v], dtype=np.uint8)  # H最大值  # S最大值  # V最大值

        # 转换图像到HSV空间并创建掩码
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_img, lower_hsv, upper_hsv)
        # 应用掩码
        result = cv2.bitwise_and(img, img, mask=mask)
        if DEBUG:
            print(f"[DEBUG] 基准颜色: {base_hex}, HSV: {h}, {s}, {v}")
            print(f"[DEBUG] HSV范围: low:{l_h}, {l_s}, {l_v}, up:{u_h}, {u_s}, {u_v}")

            cv2.imshow("Color Range Detection", result)
            cv2.waitKey(500)
        return result

    @staticmethod
    def rgb_to_hsv(r, g, b):
        # 将RGB转换为BGR格式（OpenCV默认使用BGR）
        bgr = np.uint8([[[b, g, r]]])
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
        return hsv[0][0]  # 返回NumPy数组，shape=(3,), dtype=np.uint8


class WxOcr:
    def __init__(self):
        self.win = Windows()
        self.wcocr = self.init_wcocr()

    def init_wcocr(self):
        if os.path.isfile(ocr_dir) and os.path.isdir(wx_dir):
            if wcocr.init(ocr_dir, wx_dir):
                print("WeChatOCR初始化成功")
                return wcocr
            else:
                print("WeChatOCR初始化失败")
                return None

    def get_ocr_result(self, img_path):
        # print(f"开始识别图片 typr:{type(self.wcocr)}")
        try:
            if os.path.isfile(img_path) and self.wcocr:
                return self.wcocr.ocr(img_path)
            else:
                if self.wcocr is None:
                    print("请检查图片路径是否正确")
                    raise FileNotFoundError
                else:
                    print("weiXinOCR未初始化")
        except Exception as e:
            print(f"WeChatOCR识别出错：{e}")
            return None

    def parse_result(self, result):
        try:
            assert result["ocr_response"], f"WeChatOCR识别出错:err_code{result['errcode']}"
            # 解析结果
            res = result["ocr_response"][0]
            rate = res["rate"]
            text = res["text"]
            coor = [int(i) for i in [res["left"], res["top"], res["right"], res["bottom"]]]

            return {"rate": rate, "text": text, "coor": coor}
        except Exception as e:
            print(f"解析结果出错：{e} and result:{result}")
            return None

    def ocr_by_re(self, area, pattern, threshold=0.9, range_color=None, debug=False):
        try_times = 0
        try:
            while try_times < 3:
                result = self.ocr(area)
                if result["rate"] < threshold:
                    try_times += 1
                    sleep(0.5)
                    continue
                else:
                    text = re.sub(r"\s+", "", result["text"])  # 去除空格
                    if re_res := re.search(pattern, text, re.VERBOSE):
                        return re_res
                    else:
                        try_times += 1
                        sleep(0.5)
                        continue
            return None
        except Exception as e:
            print(f"re识别出错：{e}")
            return None

    def ocr(self, area, range_color=None, debug=None):
        while True:
            # 截图
            scr_img = self.win.screenshot(area)
            # 预处理
            if range_color:
                scr_img = pre_hand_img.range_img(scr_img, *range_color, DEBUG=debug)
            # 保存截图
            save_img_path = os.path.join(current_file_dir, "temp.png")
            if retval := cv2.imwrite(save_img_path, scr_img):
                # 识别
                sleep(0.05)
                result = self.get_ocr_result(save_img_path)
                # print(f"识别结果：{result}")
                break
            else:
                print(f"保存截图失败：{retval}")
                continue

        parse = self.parse_result(result)
        print(f"识别结果：{parse}")
        # cv2.rectangle(scr_img, (parse["coor"][0], parse["coor"][1]), (parse["coor"][2], parse["coor"][3]), (0, 255, 0), 2)
        # cv2.putText(scr_img, parse["text"], (parse["coor"][0], parse["coor"][1]), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        # cv2.imshow("scr_img", scr_img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        return parse
        pass


if __name__ == "__main__":
    wx_ocr = WxOcr()
    area = (494, 22, 621, 57)
    for _ in range(20):
        result = wx_ocr.ocr(area)
        sleep(0.1)
        print(result["text"].split("/")[0])
