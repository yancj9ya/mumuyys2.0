import cv2
import os
import re
import sys
from time import sleep

# 导入自定义模块
path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(path)
from tool.Mytool.windows import Windows
from tool.wxocr import wcocr

wx_dir = r"wx"
ocr_dir = r"ocr\WeChatOCR.exe"
# 获取当前目录
current_file_dir = os.path.dirname(os.path.realpath(__file__))
# 拼接路径
wx_dir = os.path.join(current_file_dir, wx_dir)
ocr_dir = os.path.join(current_file_dir, ocr_dir)


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

    def ocr(self, area):
        while True:
            # 截图
            scr_img = self.win.screenshot(area)
            # 保存截图
            save_img_path = os.path.join(current_file_dir, "temp.png")
            if retval := cv2.imwrite(save_img_path, scr_img):
                # 识别
                result = self.get_ocr_result(save_img_path)
                print(f"识别结果：{result}")
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
    area = (247, 225, 279, 264)
    result = wx_ocr.ocr(area)
    print(result)
