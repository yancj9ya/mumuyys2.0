import ctypes
import numpy as np
import cv2
from Mytool.nemu.mumuapi import MuMuApi
from Mytool.Mylogger import logger

MUMU_API_DLL_PATH = "\\shell\\sdk\\external_renderer_ipc.dll"

ctypes.windll.user32.SetProcessDPIAware()


class MuMuScreenCap:
    def __init__(
        self,
        instanceIndex,
        emulatorInstallPath: str,
        dllPath: str = None,
        displayId: int = 0,
        quality: int = 100,
    ):
        """
        __init__ MumuApi 截图

        Args:
            instanceIndex (int): 模拟器实例的编号
            emulatorInstallPath (str): 模拟器安装路径
            dllPath (str, optional): dll文件存放路径. Defaults to None.
            displayId (int, optional): 显示窗口id. Defaults to 0.
        """
        self.quality = quality
        self.displayId = displayId
        self.instanceIndex = instanceIndex
        self.emulatorInstallPath = emulatorInstallPath
        self.dllPath = dllPath or f"{emulatorInstallPath}{MUMU_API_DLL_PATH}"
        self.nemu = MuMuApi(self.dllPath)

        # 连接模拟器
        self.handle = self.nemu.connect(self.emulatorInstallPath, self.instanceIndex)
        if not self.handle:
            raise ConnectionError("连接模拟器失败")

        self.__getDisplayInfo()

    def __getDisplayInfo(self):
        self.width = ctypes.c_int(0)
        self.height = ctypes.c_int(0)

        result = self.nemu.captureDisplay(
            self.handle,
            self.displayId,
            0,
            ctypes.byref(self.width),
            ctypes.byref(self.height),
            None,
        )
        if result != 0:
            raise RuntimeError("获取显示尺寸失败")

        # 根据宽度和高度计算缓冲区大小并创建像素数据缓冲区
        self.bufferSize = self.width.value * self.height.value * 4
        self.pixels = (ctypes.c_ubyte * self.bufferSize)()

    def screencap_raw(self) -> np.ndarray:
        result = self.nemu.captureDisplay(
            self.handle,
            self.displayId,
            self.bufferSize,
            self.width,
            self.height,
            self.pixels,
        )
        if result > 1:
            raise BufferError("截图错误")

        return self.__buffer2bytes()

    def __buffer2bytes(self) -> np.ndarray:
        # 直接使用像素缓冲区并仅重塑一次
        pixel_array = np.frombuffer(self.pixels, dtype=np.uint8).reshape(
            (self.height.value, self.width.value, 4)
        )
        flipped_rgb_pixel_array = pixel_array[::-1, :, [2, 1, 0]]

        # 采用Opencv方案编码
        _, data = cv2.imencode(".jpg", flipped_rgb_pixel_array)
        img = cv2.imdecode(data, cv2.IMREAD_COLOR)

        if img is None:
            raise RuntimeError("图像解码失败")

        return img

    def __del__(self):
        try:
            self.nemu.disconnect(self.handle)
            logger.debug("mumu screencap released")
        except Exception as e:
            logger.error(f"释放资源时出错: {e}")


if __name__ == "__main__":
    try:
        mumu = MuMuScreenCap(0, "H:\\MuMuPlayer-12.0-1", displayId=0)
        img = mumu.screencap_raw()
        print(type(img), img.shape)
        cv2.imshow("mumu", img)
        cv2.waitKey(0)
    except Exception as e:
        logger.error(f"出现错误: {e}")
    finally:
        cv2.destroyAllWindows()
