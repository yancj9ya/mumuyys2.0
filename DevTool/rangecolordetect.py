import sys
from pathlib import Path

# 获取当前文件的上级目录路径
parent_dir = str(Path(__file__).resolve().parent.parent)
sys.path.append(parent_dir)

# 现在可以导入上级目录中的模块
from tool.Mytool.Ocr import pre_hand_img
from tool.Mytool.windows import Windows

# 计算最佳的颜色范围
from ppocronnx.predict_system import TextSystem


# 初始化
win = Windows()
text_recognizer = TextSystem()


def find_color_range(baseColor, area, want_res):
    """
    寻找最佳的颜色范围
    :param baseColor: 基准颜色
    :param area: 识别区域
    :param want_res: 期望结果
    """
    # 截图
    img = win.screenshot(area)
    if img is None:
        print("截图失败")
        return None, 0
    max_accuracy = 0
    res_color_range = None
    # 定义颜色范围
    for h in range(10, 150, 5):
        for s in range(1, 150, 5):
            for v in range(1, 150, 5):
                # 计算当前颜色
                currentColorRange = (int(h), int(s), int(v))
                # 计算当前颜色的差值
                range_color = [baseColor, currentColorRange]
                # print(f"当前颜色范围: {range_color}")
                # 取色
                img_range = pre_hand_img.range_img(img, baseColor, currentColorRange, DEBUG=False)

                try:
                    # 确保处理后是3通道
                    assert img_range.shape[2] == 3, "图像必须为3通道RGB格式"
                    # OCR识别
                    result = text_recognizer.ocr_single_line(img_range)
                    # print(f"识别结果: {result[0]} accuracy: {result[1]} ")
                    if result[1] > 0.8 and want_res in result[0]:
                        print(f"当前颜色范围: {range_color}, 识别结果: {result[0]}")
                        if result[1] > max_accuracy:
                            max_accuracy = result[1]
                            res_color_range = range_color
                            print(f"更新最佳颜色范围: {res_color_range}, 识别准确率: {max_accuracy}")

                except Exception as e:
                    print(f"{e}")
                    pass
    return res_color_range, max_accuracy


if __name__ == "__main__":

    # 基准颜色
    baseColor = "f5efdb"
    area = (250, 235, 276, 259)
    # 期望结果
    want_res = "2"
    # 寻找最佳的颜色范围
    color_range, accuracy = find_color_range(baseColor, area, want_res)
    print(f"最佳颜色范围: {color_range}, 识别准确率: {accuracy}")
