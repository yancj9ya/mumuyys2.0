# this file is used to launch the client program

import psutil
import subprocess
from threading import Thread
from time import sleep
from task.based.Mytool.imageRec import ImageRec


class Client:
    def __init__(self, client_ctrl):
        self.imgrec = ImageRec()
        self.running = client_ctrl
        self.app_process_name = "MuMuPlayer.exe"
        self.app_path = r"H:\MuMuPlayer-12.0-1\shell\MuMuPlayer.exe -p com.netease.onmyoji.wyzymnqsd_cps -v 0"

    def is_app_started(self):
        for proc in psutil.process_iter():
            if proc.name() == self.app_process_name:
                return True
        return False

    def client_start(self):
        if not self.is_app_started():
            t = Thread(target=self.client_launch, args=(self.app_path, self.running))
            t.daemon = True
            t.start()
        else:
            print(f"alreadly started {self.app_path}")

    def client_launch(self, app_path, process_ctrl):
        self.process = subprocess.Popen(app_path)
        while process_ctrl.state == "RUNNING":
            sleep(1)
        else:
            self.process.kill()

    def client_stop(self):
        if hasattr(self, "process"):
            self.running.stop()
        else:
            # print("client not start by program")
            pass

    def verify_app_start_finish(self):
        app_server = ["PIGEON/config/app_server.bmp", (11, 465, 256, 678), "app_server"]
        if res := self.imgrec.match_img(app_server):
            print(f"app_server found {res}")
            return True
        else:
            self.imgrec.win.del_cache()
            return False
        pass
