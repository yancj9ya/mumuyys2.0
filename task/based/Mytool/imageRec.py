from task.based.Mytool.windows import Windows
from PIGEON.log import log
from random import randint
import cv2
import numpy as np
import pathlib
import time


class ImageRec:
    # def __new__(cls, *args, **kwargs):
    #     if not hasattr(cls, "_instance"):
    #         cls._instance = super().__new__(cls)
    #     return cls._instance

    def __init__(self):
        self.win = Windows()

    def verify_img_area(self, img_area: list) -> bool:
        try:
            _sx, _sy, _ex, _ey = img_area
            if not (0 <= _sx <= _ex <= 1280 and 0 <= _sy <= _ey <= 720):
                return False
            return True
        except (TypeError, ValueError) as e:
            log.error(f"verify_img_area 发生错误: {e}")
            return False

    def match_ui(self, img: list, accuracy=0.8, min_accuracy=0.7) -> str:
        try:
            # 获取屏幕当前的完整截图并转为灰度图
            shot_img = self.win.screenshot([0, 0, 1280, 720])
            if shot_img is None:
                raise Exception("截图失败,返回的图像为空")
            full_scr_image = cv2.cvtColor(shot_img, cv2.COLOR_BGR2GRAY)
            # log.debug(f"full_scr_image shape: {full_scr_image.shape}")

            # 遍历模板列表
            for img_match in img:
                # 匹配当前模板
                # 读取模板图片
                read_img = cv2.imread(img_match[0])
                if read_img is not None:
                    template = cv2.cvtColor(read_img, cv2.COLOR_BGR2GRAY)
                else:
                    log.error(f"未能正确读取template图片<{img_match[0]}>")
                    continue  # 跳过当前模板，继续下一个

                # 从全屏幕截图获取指定区域
                # log.debug(f"img_match[1]: {img_match[1]}")
                # 确保截图区域在屏幕范围内
                y1, y2 = max(img_match[1][1] - 5, 0), min(img_match[1][3] + 5, 720)
                x1, x2 = max(img_match[1][0] - 5, 0), min(img_match[1][2] + 5, 1280)
                part_scr_img = full_scr_image[y1:y2, x1:x2]

                # 匹配模板
                Res = cv2.matchTemplate(part_scr_img, template, cv2.TM_CCOEFF_NORMED)
                # 计算匹配度
                _, max_val, _, _ = cv2.minMaxLoc(Res)
                if max_val > accuracy:
                    # 匹配到返回匹配的UI名称
                    return img_match[2]
                elif max_val > min_accuracy:
                    # log.debug(f"模板<{img_match[2]}> 匹配度不高，但仍然是<{max_val:.2f}>")
                    pass

            return None
        except Exception as e:
            log.error(f"match_ui 发生错误: {e}")
            return None

    # def match_ui(self, img: list, accuracy=0.8) -> str:
    #     try:
    #         for img_match in img:
    #             if self.match_img(img_match, accuracy=accuracy):
    #                 # if self.is_stuck(img_match[2]):return 'stucked'
    #                 return img_match[2]
    #     except Exception as e:
    #         print(f"match_ui <{img}>发生错误: {e}")
    #         return None

    def match_img(self, img: list | tuple, accuracy=0.9) -> list:
        try:
            match_area = [
                max(img[1][0] - 5, 0),
                max(img[1][1] - 5, 0),
                min(img[1][2] + 5, 1280),
                min(img[1][3] + 5, 720),
            ]
            if not self.verify_img_area(match_area):
                raise Exception("截图区域超出屏幕范围")
            ShotImage = self.win.screenshot(match_area)
            if ShotImage is not None:
                ShotImage = cv2.cvtColor(ShotImage, cv2.COLOR_BGR2GRAY)
            else:
                raise Exception("截图失败,返回的图像为空")
            # 确保图片路径正确，读取成功
            read_img = cv2.imread(img[0])
            if read_img is not None:
                template = cv2.cvtColor(read_img, cv2.COLOR_BGR2GRAY)
            else:
                log.error(f"未能正确读取template图片<{img[0]}>")
                return None
            Res = cv2.matchTemplate(ShotImage, template, cv2.TM_CCOEFF_NORMED)

            if cv2.minMaxLoc(Res)[1] > accuracy:
                matchCor = cv2.minMaxLoc(Res)[3]
                h, w = template.shape
                s_X = img[1][0] + matchCor[0] - 5
                s_Y = img[1][1] + matchCor[1] - 5
                e_X = w + s_X
                e_Y = h + s_Y
                log.file(f"匹配到<{img[0].split('/')[-1]}> 坐标: {s_X},{s_Y} - {e_X},{e_Y}")
                return [s_X, s_Y, e_X, e_Y]
            return None
        except Exception as e:
            log.file(f"match_img<{img}> 发生错误: {e}")
            return None

    def match_color_img(self, img: list | tuple, accuracy=0.8, color_simi_acc=0.9) -> list:
        # 彩色图像模板匹配
        # start_time = time.time()
        try:
            if matched_img := self.match_img(img, accuracy=accuracy):

                shot_color_img = cv2.cvtColor(self.win.screenshot(img[1]), cv2.COLOR_BGRA2BGR)
                assert shot_color_img is not None, "截图失败,返回的图像为空"
                template_color_img = cv2.imread(img[0], cv2.IMREAD_COLOR)
                color_simi = np.mean((shot_color_img - template_color_img) ** 2)
                log.debug(f"颜色均方差: {color_simi:.2f}")
                return matched_img if color_simi < color_simi_acc else None
            else:
                return None
        except Exception as e:
            print(f"match_color_img 发生错误: {e}")
            return None

        pass

    def match_duo_img(self, img: list | tuple, accuracy=0.8, debug=False) -> list:  # 匹配区域内所有相符合的图像
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
            temp_list, weight = cv2.groupRectangles(rectList=temp_list, groupThreshold=1, eps=0.2)
            if debug:
                for pt in temp_list:
                    point_s = (pt[0] - img[1][0], pt[1] - img[1][1])
                    point_e = (point_s[0] + pt[2], point_s[1] + pt[3])
                    cv2.rectangle(f_shot_img, point_s, point_e, (0, 255, 0), 2)
                cv2.imshow("shot_img", f_shot_img)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            for pt in temp_list:
                return_list.append([pt[0], pt[1], pt[0] + pt[2], pt[1] + pt[3]])
            return return_list
        except Exception as e:
            print(f"match_duo_img 发生错误: {e}")
            return None

    def find_duo_img(self, img_dir: str, match_area: list | tuple, accuracy=0.8, return_only_one=False) -> dict | list:  # 查找目录下所有图片，返回符合条件的图片坐标
        return_dict = {}
        try:
            path = pathlib.Path(img_dir)
            img_list = [img_file for img_file in path.glob("*") if img_file.is_file()]
            ShotImage = cv2.cvtColor(self.win.screenshot(match_area), cv2.COLOR_BGRA2GRAY)
            assert ShotImage is not None, "截图失败,返回的图像为空"
            for img in img_list:
                # print(img)
                template = cv2.imread(str(img), cv2.IMREAD_GRAYSCALE)
                Res = cv2.matchTemplate(ShotImage, template, cv2.TM_CCOEFF_NORMED)
                if cv2.minMaxLoc(Res)[1] > accuracy:
                    matchCor = cv2.minMaxLoc(Res)[3]
                    h, w = template.shape
                    s_X = match_area[0] + matchCor[0]
                    s_Y = match_area[1] + matchCor[1]
                    e_X = w + s_X
                    e_Y = h + s_Y
                    if return_only_one:
                        return [str(img), [s_X, s_Y, e_X, e_Y], img.stem]
                    return_dict[img.stem] = [s_X, s_Y, e_X, e_Y]
            if return_dict:
                return return_dict
            else:
                return None
        except Exception as e:
            print(f"find_duo_img 发生错误: {e}")
            return None

    def stat_reward(self, need_stat_dir: str, match_area: list, accuracy=0.9) -> dict:
        return self.find_duo_img(need_stat_dir, match_area, accuracy=accuracy, return_only_one=False)
