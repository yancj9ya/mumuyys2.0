from tool.Mytool.windows import Windows
from typing import List, Tuple, Optional, Dict, Union
from PIGEON.log import log
from random import randint
import numpy as np
import cv2
import pathlib


class ImageRec:
    """
    图像识别类。
    """

    def __init__(self):
        self.win = Windows()

    def verify_img_area(self, img_area: list) -> bool:
        """验证图片区域是否在屏幕范围内。"""
        try:
            _sx, _sy, _ex, _ey = img_area
            if not (0 <= _sx <= _ex <= 1280 and 0 <= _sy <= _ey <= 720):
                return False
            return True
        except (TypeError, ValueError) as e:
            log.error(f"verify_img_area 发生错误: {e}")
            return False

    def match_ui(self, img: list, accuracy: float = 0.8, min_accuracy: float = 0.7) -> Optional[str]:
        """
        在指定区域内匹配模板图像，返回匹配的UI名称。

        :param img: 包含模板路径、匹配区域和UI名称的列表 [(template_path, [x1, y1, x2, y2], ui_name)]
        :param accuracy: 匹配精度阈值，默认 0.8
        :param min_accuracy: 最低匹配精度阈值，默认 0.7
        :return: 匹配的UI名称，如果未匹配到则返回 None
        """
        try:
            # 获取屏幕当前的完整截图并转为灰度图
            shot_img = self.win.screenshot([0, 0, 1280, 720])
            if shot_img is None:
                raise Exception("截图失败,返回的图像为空")
            full_scr_image = cv2.cvtColor(shot_img, cv2.COLOR_BGR2GRAY)

            # 遍历模板列表
            for template_path, area, ui_name in img:
                # 读取模板图片
                template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
                if template is None:
                    log.error(f"未能正确读取template图片<{ui_name}>")
                    continue  # 跳过当前模板，继续下一个

                # 从全屏幕截图获取指定区域
                y1, y2 = max(area[1] - 5, 0), min(area[3] + 5, 720)
                x1, x2 = max(area[0] - 5, 0), min(area[2] + 5, 1280)
                part_scr_img = full_scr_image[y1:y2, x1:x2]

                # 匹配模板
                Res = cv2.matchTemplate(part_scr_img, template, cv2.TM_CCOEFF_NORMED)

                # 检查匹配精度
                _, max_val, _, _ = cv2.minMaxLoc(Res)
                if max_val > accuracy:
                    # 匹配到返回匹配的UI名称
                    return ui_name
                elif max_val > accuracy - 0.05:
                    log.debug(f"模板<{ui_name}> 匹配度不高，但仍然是<{max_val:.2f}>")
                    pass

            return None
        except ValueError as ve:
            log.error(f"参数错误: {ve}")
            return None
        except Exception as e:
            log.error(f"match_ui 发生错误: {e}")
            return None

    def match_img(self, img: list | tuple, accuracy: float = 0.9, needMask: bool | str = False) -> Optional[list[int]]:
        """
        在指定区域内匹配模板图像。

        :param img: 包含模板路径和匹配区域的元组 (template_path, [x1, y1, x2, y2])
        :param accuracy: 匹配精度阈值，默认 0.9
        :param needMask: 掩码路径，如果为 None 则不使用掩码
        :return: 匹配区域的坐标 [x1, y1, x2, y2]，如果未匹配到则返回 None
        """
        try:
            # 扩展匹配区域，确保边界安全
            match_area = [max(img[1][0] - 5, 0), max(img[1][1] - 5, 0), min(img[1][2] + 5, 1280), min(img[1][3] + 5, 720)]

            # 截图并转为灰度图
            ShotImage = self.win.screenshot(match_area)
            if ShotImage is not None:
                ShotImage = cv2.cvtColor(ShotImage, cv2.COLOR_BGR2GRAY)
            else:
                raise Exception("截图失败,返回的图像为空")
            # 确保图片路径正确，读取成功
            template = cv2.imread(img[0], cv2.IMREAD_GRAYSCALE)
            if template is None:
                log.error(f"未能正确读取template图片<{img[0]}>")
                return None

            # 使用掩码（如果提供）
            mask = None
            if needMask:
                mask = cv2.imread(needMask, 0)
                if mask is None:
                    log.error(f"未能正确读取掩码图片: {needMask}")
                    return None

            # 模板匹配
            res = cv2.matchTemplate(ShotImage, template, cv2.TM_CCOEFF_NORMED, mask=mask)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)

            # 计算匹配区域的坐标
            if max_val > accuracy:
                matchCor = max_loc
                h, w = template.shape
                s_X = img[1][0] + matchCor[0] - 5
                s_Y = img[1][1] + matchCor[1] - 5
                e_X = w + s_X
                e_Y = h + s_Y
                # log.file(f"匹配到<{img[0].split('/')[-1]}> 坐标: {s_X},{s_Y} - {e_X},{e_Y}")
                return [s_X, s_Y, e_X, e_Y]
            return None

        except ValueError as ve:
            log.error(f"参数错误: {ve}")
            return None
        except Exception as e:
            log.file(f"match_img<{img}> 发生错误: {e}")
            return None

    def match_img_by_hist(self, img: list | tuple, accuracy=0.9) -> Optional[list[int]]:
        """
        基于颜色直方图的识别方式，对图像的旋转具有一定的鲁棒性
        :param img: 包含模板路径和匹配区域的元组 (template_path, [x1, y1, x2, y2])
        :param accuracy: 匹配精度阈值，默认 0.9
        :return: 匹配区域的坐标 [x1, y1, x2, y2]，如果未匹配到则返回 None
        """
        try:
            # 验证图片区域是否在屏幕范围内
            if not self.verify_img_area(img[1]):
                log.error(f"图片区域超出屏幕范围: {img[1]}")
                return None
            # 截取目标区域的图片
            shot_img = self.win.screenshot(img[1])
            assert shot_img is not None, "截图失败,返回的图像为空"
            # 读取模板图片
            template = cv2.imread(img[0], cv2.IMREAD_COLOR)
            assert template is not None, f"未能正确读取template图片<{img[0]}>"
            # 计算模板的颜色直方图
            template_color_hist = cv2.calcHist([template], [0, 1, 2], None, [16, 16, 16], [0, 256, 0, 256, 0, 256])
            # 计算截图的颜色直方图
            shot_color_hist = cv2.calcHist([shot_img], [0, 1, 2], None, [16, 16, 16], [0, 256, 0, 256, 0, 256])
            # 归一化处理
            template_color_hist = cv2.normalize(template_color_hist, template_color_hist, 0, 1, cv2.NORM_MINMAX)
            shot_color_hist = cv2.normalize(shot_color_hist, shot_color_hist, 0, 1, cv2.NORM_MINMAX)
            # 计算颜色直方图的相似度
            color_simi = cv2.compareHist(template_color_hist, shot_color_hist, cv2.HISTCMP_CORREL)
            # 匹配
            if color_simi > accuracy:
                s_X = img[1][0]
                s_Y = img[1][1]
                e_X = img[1][2]
                e_Y = img[1][3]
                log.file(f"匹配到<{img[0].split('/')[-1]}> 坐标: {s_X},{s_Y} - {e_X},{e_Y}, 相似度: {color_simi:.2f}")
                return [s_X, s_Y, e_X, e_Y]
            else:
                log.file(f"颜色直方图匹配度不高，但仍然是<{color_simi:.2f}>")
                return None
        except Exception as e:
            log.error(f"match_img_by_hist 发生错误: {e}")
            return None

    def match_color_img(self, img: list | tuple, accuracy=0.8, color_simi_acc=0.9) -> list:
        """
        在指定区域内匹配彩色模板图像。

        :param img: 包含模板路径和匹配区域的元组 (template_path, [x1, y1, x2, y2],img_name)
        :param accuracy: 匹配精度阈值，默认 0.8
        :param color_simi_acc: 颜色相似度阈值，默认 0.9
        :return: 匹配区域的坐标 [x1, y1, x2, y2]，如果未匹配到则返回 None
        """
        try:
            if matched_img := self.match_img(img, accuracy=accuracy):

                shot_color_img = cv2.cvtColor(self.win.screenshot(img[1]), cv2.COLOR_BGRA2BGR)
                assert shot_color_img is not None, "彩色匹配时截图失败,返回的图像为空"
                template_color_img = cv2.imread(img[0], cv2.IMREAD_COLOR)
                color_simi = np.mean((shot_color_img - template_color_img) ** 2)
                log.debug(f"颜色均方差: {color_simi:.2f}")
                return matched_img if color_simi < color_simi_acc else None
            else:
                return None
        except Exception as e:
            print(f"match_color_img 发生错误: {e}")
            return None

    def match_color_img_by_hist(self, img: list | tuple, accuracy=0.8, color_simi_acc=0.9) -> list:
        """
        基于模板匹配和颜色直方图相似度比较的图像匹配方法。

        参数:
            img (list | tuple): 包含模板图像路径和截图区域的列表或元组。
            accuracy (float): 模板匹配的阈值，默认值为 0.8。
            color_simi_acc (float): 颜色相似度的阈值，默认值为 0.9。

        返回:
            list: 匹配位置的坐标 [s_X, s_Y, e_X, e_Y]，如果未匹配到则返回 None。
        """
        # 1. 截图
        shot_img = self.win.screenshot(img[1])

        # 2. 读取模板图片
        template = cv2.imread(img[0], cv2.IMREAD_COLOR)

        # 3. 模板匹配获取位置
        # 使用彩色图像进行模板匹配
        res = cv2.matchTemplate(shot_img, template, cv2.TM_CCOEFF_NORMED)
        _, match_score, _, max_loc = cv2.minMaxLoc(res)

        # 如果匹配值大于阈值，则获取匹配位置
        if match_score > accuracy:
            s_X = img[1][0] + max_loc[0]
            s_Y = img[1][1] + max_loc[1]
            e_X = s_X + template.shape[1]
            e_Y = s_Y + template.shape[0]
            position = [s_X, s_Y, e_X, e_Y]

            # 从截图中提取匹配区域
            matched_region = shot_img[max_loc[1] : max_loc[1] + template.shape[0], max_loc[0] : max_loc[0] + template.shape[1]]
        else:
            return None

        # 4. 计算颜色直方图
        template_color_hist = cv2.calcHist([template], [0, 1, 2], None, [16, 16, 16], [0, 256, 0, 256, 0, 256])
        shot_color_hist = cv2.calcHist([matched_region], [0, 1, 2], None, [16, 16, 16], [0, 256, 0, 256, 0, 256])

        # 5. 归一化处理
        template_color_hist = cv2.normalize(template_color_hist, template_color_hist, 0, 1, cv2.NORM_MINMAX)
        shot_color_hist = cv2.normalize(shot_color_hist, shot_color_hist, 0, 1, cv2.NORM_MINMAX)

        # 6. 计算颜色相似度
        color_similarity = cv2.compareHist(template_color_hist, shot_color_hist, cv2.HISTCMP_CORREL)

        # 如果颜色相似度大于阈值，则返回匹配位置
        if color_similarity > color_simi_acc:
            return position
        else:
            log.debug(f"颜色相似度不高，但仍然是<{color_similarity:.2f}>")
            return None

    def match_duo_img(self, img: list | tuple, accuracy=0.8, debug=False) -> list:
        """
        在指定区域内匹配所有符合的模板图像。

        :param img: 包含模板路径和匹配区域的元组 (template_path, [x1, y1, x2, y2],img_name)
        :param accuracy: 匹配精度阈值，默认 0.8
        :param debug: 是否调试模式，默认 False
        :return: 匹配区域的坐标列表 [[x1, y1, x2, y2]]，如果未匹配到则返回 None
        """
        return_list = []
        temp_list = []
        try:
            f_shot_img = self.win.screenshot(img[1])
            assert f_shot_img is not None, "截图失败,返回的图像为空"
            shot_img = cv2.cvtColor(f_shot_img, cv2.COLOR_BGRA2GRAY)
            template = cv2.imread(img[0], cv2.IMREAD_GRAYSCALE)
            Res = cv2.matchTemplate(shot_img, template, cv2.TM_CCOEFF_NORMED)
            h, w = template.shape
            loc = np.where(Res >= accuracy)
            for pt in zip(*loc[::-1]):
                s_X = img[1][0] + pt[0]
                s_Y = img[1][1] + pt[1]
                temp_list.append([s_X, s_Y, w, h])
            temp_list = self.merge_rectangles(temp_list)
            if debug:
                for pt in temp_list:
                    point_s = (pt[0] - img[1][0], pt[1] - img[1][1])
                    point_e = (point_s[0] + pt[2], point_s[1] + pt[3])
                    cv2.rectangle(f_shot_img, point_s, point_e, (0, 255, 0), 1)
                cv2.imshow("shot_img", f_shot_img)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            for pt in temp_list:
                return_list.append([pt[0], pt[1], pt[0] + pt[2], pt[1] + pt[3]])
            return return_list
        except Exception as e:
            print(f"match_duo_img 发生错误: {e}")
            return None

    def iou(self, box1, box2):
        """计算两个矩形框的 IOU"""
        x1, y1, w1, h1 = box1
        x2, y2, w2, h2 = box2

        # 计算交集的坐标
        xi1 = max(x1, x2)
        yi1 = max(y1, y2)
        xi2 = min(x1 + w1, x2 + w2)
        yi2 = min(y1 + h1, y2 + h2)

        # 如果没有重叠区域，则 IOU 为 0
        if xi1 >= xi2 or yi1 >= yi2:
            return 0.0

        # 计算交集区域的面积
        intersection_area = (xi2 - xi1) * (yi2 - yi1)

        # 计算两个矩形框的面积
        area1 = w1 * h1
        area2 = w2 * h2

        # 计算 IOU
        iou = intersection_area / (area1 + area2 - intersection_area)
        return iou

    def merge_rectangles(self, rects, threshold=0.5):
        """根据 IOU 合并矩形框"""
        merged = []
        while rects:
            # 选择第一个框作为参考
            rect = rects.pop(0)
            to_merge = [rect]

            # 遍历其余框，计算 IOU，如果大于阈值则合并
            for other in rects[:]:
                if self.iou(rect, other) > threshold:
                    to_merge.append(other)
                    rects.remove(other)

            # 合并所有选择的框，取它们的最小左上角和最大右下角来构成合并后的框
            if len(to_merge) > 1:
                x1 = min([r[0] for r in to_merge])
                y1 = min([r[1] for r in to_merge])
                x2 = max([r[0] + r[2] for r in to_merge])
                y2 = max([r[1] + r[3] for r in to_merge])
                merged.append([x1, y1, x2 - x1, y2 - y1])
            else:
                # 如果只有一个框，直接保留它
                merged.append(to_merge[0])

        return merged

    def find_duo_img(self, img_dir: str | list, match_area: list | tuple, accuracy=0.8, return_only_one=False, debug=False) -> dict | list:
        """
        查找目录下所有图片，返回符合条件的图片坐标。
        :param img_dir: 图片目录路径,或图片路径组成的列表
        :param match_area: 匹配区域 [x1, y1, x2, y2]
        :param accuracy: 匹配精度阈值，默认 0.8
        :param return_only_one: 是否只返回一个结果，默认 False
        :param debug: 是否显示调试信息，默认 False
        :return: 如果 return_only_one 为 True,则返回 (template_path, [x1, y1, x2, y2], img_name)；否则返回 {img_name: [x1, y1, x2, y2]}
        """
        return_dict = {}
        try:
            # 处理 img_dir 参数
            if isinstance(img_dir, str):
                path = pathlib.Path(img_dir)
                img_list = [img_file for img_file in path.glob("*") if img_file.is_file()]
            elif isinstance(img_dir, list):
                img_list = [pathlib.Path(img_path[0]) for img_path in img_dir]
            else:
                raise ValueError("img_dir 参数类型错误，应为字符串或列表")

            # 截取匹配区域的图像并转换为灰度图
            ShotImage = cv2.cvtColor(self.win.screenshot(match_area), cv2.COLOR_BGRA2GRAY)
            if ShotImage is None:
                raise ValueError("截图失败，返回的图像为空")

            # 遍历所有模板图片
            for img in img_list:
                template = cv2.imread(str(img), cv2.IMREAD_GRAYSCALE)
                if template is None:
                    print(f"无法读取模板图片: {img}")
                    continue

                # 模板匹配
                Res = cv2.matchTemplate(ShotImage, template, cv2.TM_CCOEFF_NORMED)
                if Res is None:
                    print(f"模板匹配失败: {img}")
                    continue

                # 调试模式下显示截图和模板
                if debug:
                    cv2.imshow("shot_img", ShotImage)
                    cv2.imshow("template", template)
                    cv2.waitKey(1)  # 等待 1ms，避免卡住
                    cv2.destroyAllWindows()

                # 找到所有匹配度高于阈值的位置
                loc = np.where(Res >= accuracy)
                # print(f"匹配到<{img.stem}> 坐标: {loc}")
                h, w = template.shape

                # 提取所有匹配框及其匹配度
                temp_list = []
                for pt in zip(*loc[::-1]):  # loc[::-1] 反转坐标顺序 (x, y)
                    s_X = int(match_area[0] + pt[0])
                    s_Y = int(match_area[1] + pt[1])
                    temp_list.append([s_X, s_Y, w, h])

                # 使用 cv2.groupRectangles 合并重叠的矩形框
                if len(temp_list) > 1:
                    # print(f"原始坐标: {temp_list}")
                    grouped_rects = self.merge_rectangles(temp_list, threshold=0.9)
                    # print(f"合并后的坐标: {grouped_rects}")
                else:
                    grouped_rects = temp_list
                # 遍历合并后的矩形框
                for rect in grouped_rects:
                    s_X, s_Y, e_X, e_Y = rect[0], rect[1], rect[0] + w, rect[1] + h

                    # 如果只需要返回一个结果
                    if return_only_one:
                        return [str(img), [s_X, s_Y, e_X, e_Y], img.stem]

                    # 将结果存入字典
                    key = img.stem
                    if return_dict.get(key, None) is not None:
                        key = f"{img.stem}_{randint(1000, 9999)}"  # 重命名
                    return_dict[key] = [s_X, s_Y, e_X, e_Y]

            # 返回结果
            if return_dict:
                return return_dict
            else:
                return None

        except Exception as e:
            print(f"find_duo_img 发生错误: {e}")
            return None

    def stat_reward(self, need_stat_dir: str, match_area: list, accuracy=0.9) -> dict:
        """
        统计奖励区域内的匹配结果。

        :param need_stat_dir: 图片目录路径
        :param match_area: 匹配区域 [x1, y1, x2, y2]
        :param accuracy: 匹配精度阈值，默认 0.9
        :return: {img_name: [x1, y1, x2, y2]}，如果未匹配到则返回 None
        """
        return self.find_duo_img(need_stat_dir, match_area, accuracy=accuracy, return_only_one=False)
