import psutil
import subprocess
from time import sleep


def start_app(app_path):
    return subprocess.Popen(app_path)


def is_app_running(app_name):
    for proc in psutil.process_iter():
        print(proc.name())
        if proc.name() == app_name:
            return True
    return False


if __name__ == "__main__":
    is_app_running("MuMuPlayer.exe")

    # app_name = "MuMuVMMHeadless.exe"
    # if is_app_running(app_name):
    #     print(f"{app_name} is running")
    # else:
    #     print(f"{app_name} is not running")
    #     app_path = r"H:\MuMuPlayer-12.0-1\shell\MuMuPlayer.exe -p com.netease.onmyoji.wyzymnqsd_cps -v 0"
    #     start_app(app_path)
