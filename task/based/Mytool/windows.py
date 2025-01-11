# This file is used to capture the screenshot of the game window and send mouse events to the game window.
#
#

import win32gui
import win32ui
import win32con
import time
import numpy as np
import cv2
from ctypes import windll
from PIGEON.log import log
from functools import cached_property


# from Mytool.nemu.mumuScreencap import MuMuScreenCap
WM_XBUTTONDOWN = 0x020B
WM_XBUTTONUP = 0x020C
MK_XBUTTON1 = 0x0020

WM_LBUTTONDOWN = 0x0201
WM_SERCURSOR = 0x20
WM_MOUSEACTIVATE = 0x21
WM_MOUSEMOVE = 0x0200
WM_LBUTTONUP = 0x0202
WM_PARENTNOTIFY = 0x210
WM_MOUSEWHEEL = 0x020A

MK_LBUTTON = 0x0001
HTCLIENT = 1

PostMessage = windll.user32.PostMessageW
SendMessage = windll.user32.SendMessageW

FindWindow = win32gui.FindWindow
FindWindowEx = win32gui.FindWindowEx
IsWindow = win32gui.IsWindow


class Windows:
    LOCK = False  # 主要是为了截图互斥，防止竞争设备上下文导致的错误

    # mumu_sc = MuMuScreenCap(
    #     0, "H:\MuMuPlayer-12.0-1", displayId=0
    # )  # mumu自身的ipc截图方式，创建链接木木模拟器的实例
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # windows截图的方式,必须获取窗口句柄handle
        # log.debug("初始化Windows类")
        # log.debug(f"获取窗口句柄:{self.handle}")
        # log.debug(f"id:{id(self)}")

        pass

    def del_cache(self):
        if "par_handle" in self.__dict__:
            del self.__dict__["par_handle"]
        if "handle" in self.__dict__:
            del self.__dict__["handle"]
        log.file("删除句柄缓存")

    @cached_property
    def par_handle(self) -> int:
        return win32gui.FindWindow(None, "MuMu模拟器12")

    @cached_property
    def handle(self) -> int:
        return win32gui.FindWindowEx(self.par_handle, None, None, "MuMuPlayer")

    def is_handle_valid(self) -> bool:
        if self.handle == 0:
            return False
        else:
            return IsWindow(self.handle)

    def screenshot(self, area: list, save_img=False, method="win_shot", debug=False) -> np.ndarray:
        if not self.is_handle_valid():
            log.file(f"窗口句柄: {self.handle} 已失效")
            self.del_cache()
            return None

        # 截图方式
        match method:
            case "win_shot":
                while Windows.LOCK:  # locked
                    time.sleep(0.01)  # wait for release lock
                else:
                    Windows.LOCK = True  # set lock

                    hwindc = None
                    srcdc = None
                    memdc = None
                    bmp = None
                    img = None

                    try:
                        # 计算截图区域
                        w, h = area[2] - area[0], area[3] - area[1]

                        # 获取窗口设备上下文
                        hwindc = win32gui.GetWindowDC(self.handle)
                        srcdc = win32ui.CreateDCFromHandle(hwindc)
                        memdc = srcdc.CreateCompatibleDC()
                        bmp = win32ui.CreateBitmap()
                        bmp.CreateCompatibleBitmap(srcdc, w, h)
                        memdc.SelectObject(bmp)

                        # 从源设备上下文复制位图到内存设备上下文
                        memdc.BitBlt((0, 0), (w, h), srcdc, (area[0], area[1]), win32con.SRCCOPY)

                        # 获取位图数据并转换为图像数组
                        signedIntsArray = bmp.GetBitmapBits(True)
                        img = np.frombuffer(signedIntsArray, dtype="uint8").reshape(h, w, 4)
                        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                        if debug:
                            cv2.imshow("截图", img)
                            cv2.waitKey(0)

                    except Exception as e:
                        log.error(f"截图失败，错误信息: {e}")
                        if win32gui.IsWindow(self.handle):
                            log.error(f"窗口句柄: {self.handle} 仍然有效")
                        else:
                            log.error(f"窗口句柄: {self.handle} 已失效")
                            self.del_cache()

                        return None

                    finally:
                        # 清理资源
                        if srcdc:
                            srcdc.DeleteDC()
                        if memdc:
                            memdc.DeleteDC()
                        if hwindc:
                            win32gui.ReleaseDC(self.handle, hwindc)
                        if bmp:
                            win32gui.DeleteObject(bmp.GetHandle())
                        if Windows.LOCK:
                            Windows.LOCK = False  # release lock
            case "nemu_ipc":
                # try:
                #     whole_img = self.mumu_sc.screencap_raw()
                #     img = whole_img[area[1] : area[3], area[0] : area[2]]
                # except Exception as e:
                #     log.error(f"截图失败，错误信息: {e}")
                #     return None
                pass

        # 保存图像或返回处理后的图像
        if save_img:
            timestamp = time.strftime("(%Y-%m-%d)  %H时%M分", time.localtime())
            path = f"task/dg/awards/{timestamp}.jpg"
            cv2.imencode(".jpg", img)[1].tofile(path)
            log.info(f"截图成功，保存路径为:\n{path}")
            return None  # 如果保存图像，则返回 None

        return img

    def get_window_name(self, hwnd) -> str:
        return win32gui.GetWindowText(hwnd)

    def is_window_top(self) -> bool:
        try:
            # 获取top窗口的句柄
            top_window_hwnd = win32gui.GetForegroundWindow()
            # print(f"前置窗口句柄:{top_window_hwnd}and 名字:{self.get_window_name(top_window_hwnd)}，模拟器句柄:{self.par_handle}")
            if self.par_handle == top_window_hwnd or self.get_window_name(top_window_hwnd) == "八尺琼勾玉":  # 防止脚本gui置顶导致的不后置
                return True
            else:
                return False
        except Exception as e:
            log.error(f"获取前置窗口句柄失败，错误信息: {e}")
            return False
        finally:
            top_window_hwnd = None

    def set_window_bottom(self):
        win32gui.SetWindowPos(self.par_handle, win32con.HWND_BOTTOM, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
        log.file(f"窗口置底: {self.par_handle}")

    def is_windows_exist(self) -> bool:
        return IsWindow(self.par_handle)

    def notifyparent(self, x, y):
        msg = WM_PARENTNOTIFY
        wparam = WM_LBUTTONDOWN
        Lparam = y << 16 | x
        SendMessage(self.par_handle, msg, wparam, Lparam)

    def mouse_move(self, x, y):
        msg = WM_MOUSEMOVE
        wparam = MK_LBUTTON
        Lparam = y << 16 | x
        PostMessage(self.handle, msg, wparam, Lparam)

    def mouseactivate(self):
        msg = WM_MOUSEACTIVATE
        wparam = self.par_handle
        Lparam = WM_LBUTTONDOWN << 16 | HTCLIENT
        SendMessage(self.handle, msg, wparam, Lparam)

    def setcursor(self):
        msg = WM_SERCURSOR
        wparam = self.handle
        Lparam = WM_LBUTTONDOWN << 16 | HTCLIENT
        SendMessage(self.handle, msg, wparam, Lparam)

    def left_down(self, x, y):
        msg = WM_LBUTTONDOWN
        wparam = MK_LBUTTON
        Lparam = y << 16 | x
        PostMessage(self.handle, msg, wparam, Lparam)

    def left_up(self, x, y):
        msg = WM_LBUTTONUP
        wparam = 0
        Lparam = y << 16 | x
        PostMessage(self.handle, msg, wparam, Lparam)

    def wheel_scroll(self, delta, x, y):
        msg = WM_MOUSEWHEEL
        wparam = delta << 16
        Lparam = y << 16 | x
        PostMessage(self.handle, msg, wparam, Lparam)

    def get_window_rect(self) -> list:
        return win32gui.GetWindowRect(self.handle)

    def x_button_down(self, x, y):
        msg = WM_XBUTTONDOWN  # type: ignore
        wparam = MK_XBUTTON1  # type: ignore
        Lparam = y << 16 | x
        PostMessage(self.handle, msg, wparam, Lparam)

    def x_button_up(self, x, y):
        msg = WM_XBUTTONUP  # type: ignore
        wparam = MK_XBUTTON1  # type: ignore
        Lparam = y << 16 | x
        PostMessage(self.handle, msg, wparam, Lparam)


if __name__ == "__main__":
    import sys

    sys.path.append("your_path_to_Mytool")

    w = Windows()
    print(f"窗口句柄:parent_handle={w.par_handle}, handle= {w.handle}\n")
    # 分身N1
    par_handle = w.get_handle("#N1 阴阳师 - MuMu模拟器12")
    handle = w.get_handleEx(par_handle, "MuMuPlayer")
    print(f"分身N1的窗口句柄: par={par_handle}, child={handle}")
