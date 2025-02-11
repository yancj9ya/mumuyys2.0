from page.page_switch import nav
from tool.soulchange.soulchange import SoulChange
from tool.soulchange.res.img_info_auto_create import *
from tool.Mytool.imageRec import ImageRec
from tool.Mytool.windows import Windows
import time

import ctypes
from ctypes import wintypes
import sys
from PIL import Image
import win32gui

# 初始化DLL并设置正确的类型
user32 = ctypes.WinDLL("user32", use_last_error=True)
gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)


# 定义结构体
class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long), ("top", ctypes.c_long), ("right", ctypes.c_long), ("bottom", ctypes.c_long)]


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", wintypes.DWORD),
        ("biWidth", ctypes.c_long),
        ("biHeight", ctypes.c_long),
        ("biPlanes", wintypes.WORD),
        ("biBitCount", wintypes.WORD),
        ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD),
        ("biXPelsPerMeter", ctypes.c_long),
        ("biYPelsPerMeter", ctypes.c_long),
        ("biClrUsed", wintypes.DWORD),
        ("biClrImportant", wintypes.DWORD),
    ]


class BITMAPINFO(ctypes.Structure):
    _fields_ = [("bmiHeader", BITMAPINFOHEADER), ("bmiColors", wintypes.DWORD * 3)]


# 定义API函数原型
user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
user32.FindWindowW.restype = wintypes.HWND

user32.GetClientRect.argtypes = [wintypes.HWND, ctypes.POINTER(RECT)]
user32.GetClientRect.restype = wintypes.BOOL

user32.PrintWindow.argtypes = [wintypes.HWND, wintypes.HDC, ctypes.c_uint]
user32.PrintWindow.restype = wintypes.BOOL

gdi32.CreateCompatibleDC.argtypes = [wintypes.HDC]
gdi32.CreateCompatibleDC.restype = wintypes.HDC

gdi32.CreateCompatibleBitmap.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int]
gdi32.CreateCompatibleBitmap.restype = wintypes.HBITMAP  # 关键修正

gdi32.SelectObject.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
gdi32.SelectObject.restype = wintypes.HGDIOBJ

gdi32.GetDIBits.argtypes = [wintypes.HDC, wintypes.HBITMAP, wintypes.UINT, wintypes.UINT, ctypes.c_void_p, ctypes.POINTER(BITMAPINFO), wintypes.UINT]
gdi32.GetDIBits.restype = ctypes.c_int

gdi32.DeleteObject.argtypes = [wintypes.HGDIOBJ]
gdi32.DeleteObject.restype = wintypes.BOOL

user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
user32.ReleaseDC.restype = ctypes.c_int


def capture_minimized_window(window_title: str, output_path: str) -> bool:
    try:
        # 获取窗口句柄
        hwnd = user32.FindWindowW(None, window_title)
        # hwnd = win32gui.FindWindowEx(hwnd, None, None, "MuMuPlayer")
        if hwnd == 0:
            print(f"窗口未找到，错误代码: {ctypes.get_last_error()}")
            return False

        # 获取窗口尺寸
        rect = RECT()
        if not user32.GetClientRect(hwnd, ctypes.byref(rect)):
            print(f"获取尺寸失败，错误代码: {ctypes.get_last_error()}")
            return False

        width = rect.right - rect.left
        height = rect.bottom - rect.top
        if width == 0 or height == 0:
            print("窗口尺寸无效")
            return False

        # 创建设备上下文
        hdc_screen = user32.GetDC(None)
        if hdc_screen == 0:
            print(f"获取设备上下文失败，错误代码: {ctypes.get_last_error()}")
            return False

        hdc_mem = gdi32.CreateCompatibleDC(hdc_screen)
        if hdc_mem == 0:
            print(f"创建内存DC失败，错误代码: {ctypes.get_last_error()}")
            user32.ReleaseDC(None, hdc_screen)
            return False

        # 创建兼容位图
        hbitmap = gdi32.CreateCompatibleBitmap(hdc_screen, width, height)
        if hbitmap == 0:
            print(f"创建位图失败，错误代码: {ctypes.get_last_error()}")
            gdi32.DeleteDC(hdc_mem)
            user32.ReleaseDC(None, hdc_screen)
            return False

        # 选择位图到设备上下文
        old_bitmap = gdi32.SelectObject(hdc_mem, hbitmap)
        if old_bitmap == 0:
            print(f"选择位图失败，错误代码: {ctypes.get_last_error()}")
            gdi32.DeleteObject(hbitmap)
            gdi32.DeleteDC(hdc_mem)
            user32.ReleaseDC(None, hdc_screen)
            return False

        # 调用PrintWindow捕获
        result = user32.PrintWindow(hwnd, hdc_mem, 0x00000002)  # PW_CLIENTONLY
        if not result:
            print(f"PrintWindow失败，错误代码: {ctypes.get_last_error()}")
            gdi32.SelectObject(hdc_mem, old_bitmap)
            gdi32.DeleteObject(hbitmap)
            gdi32.DeleteDC(hdc_mem)
            user32.ReleaseDC(None, hdc_screen)
            return False

        # 准备位图信息
        bmpinfo = BITMAPINFO()
        bmpinfo.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmpinfo.bmiHeader.biWidth = width
        bmpinfo.bmiHeader.biHeight = -height  # 顶部到底部
        bmpinfo.bmiHeader.biPlanes = 1
        bmpinfo.bmiHeader.biBitCount = 32
        bmpinfo.bmiHeader.biCompression = 0  # BI_RGB
        bmpinfo.bmiHeader.biSizeImage = 0

        # 获取位图数据
        buffer = ctypes.create_string_buffer(width * height * 4)
        success = gdi32.GetDIBits(hdc_mem, hbitmap, 0, height, buffer, ctypes.byref(bmpinfo), 0)  # DIB_RGB_COLORS

        if not success:
            print(f"GetDIBits失败，错误代码: {ctypes.get_last_error()}")
            gdi32.SelectObject(hdc_mem, old_bitmap)
            gdi32.DeleteObject(hbitmap)
            gdi32.DeleteDC(hdc_mem)
            user32.ReleaseDC(None, hdc_screen)
            return False

        # 转换为PIL图像并保存
        img = Image.frombuffer("RGBA", (width, height), buffer, "raw", "BGRA", 0, 1)
        img.save(output_path)
        print(f"截图已保存至: {output_path}")

    except Exception as e:
        print(f"发生异常: {str(e)}")
        return False
    finally:
        # 清理资源
        if "old_bitmap" in locals() and old_bitmap != 0:
            gdi32.SelectObject(hdc_mem, old_bitmap)
        if "hbitmap" in locals() and hbitmap != 0:
            gdi32.DeleteObject(hbitmap)
        if "hdc_mem" in locals() and hdc_mem != 0:
            gdi32.DeleteDC(hdc_mem)
        if "hdc_screen" in locals() and hdc_screen != 0:
            user32.ReleaseDC(None, hdc_screen)

    return True


if __name__ == "__main__":

    window_title = "MuMu模拟器12"
    output_path = "screenshot.png"

    success = capture_minimized_window(window_title, output_path)


# if __name__ == "__main__":
#     # IMAGE_REC = ImageRec()

#     # CHECKED = ["tool/soulchange/res/CHECKED.bmp", [1234, 167, 1252, 218], "CHECKED"]  # [1236, 100, 1253, 149]
#     # UNCHECK = ["tool/soulchange/res/UNCHECK.bmp", [1234, 167, 1252, 218], "UNCHECK"]  # [1234, 167, 1252, 218]
#     # GROUP_LIST = [GROUP1, GROUP2, GROUP3, GROUP4, GROUP5, GROUP6, GROUP7]

#     # for group in GROUP_LIST:
#     #     CHECKED[1] = group
#     #     # print(CHECKED)
#     #     res = IMAGE_REC.match_color_img_by_hist(CHECKED)  # CHECKED UNCHECK
#     #     # print(CHECKED[2], res)
#     #     print(f"{res}-{bool(res)}:{GROUP_LIST.index(group)}")

#     wn = Windows()
#     print(wn.par_handle)
#     print(wn.handle)
#     # wn.mouseactivateX()
#     # wn.setcursorX()
#     wn.x_button_down(735, 547)
#     time.sleep(0.1)
#     wn.x_button_up(735, 547)
