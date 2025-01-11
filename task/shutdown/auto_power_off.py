# this code will shutdown the system by set parms

import os


class AutoPowerOff:
    def __init__(self, *args, **kwargs):
        pass

    def loop(self):
        self.shutdown()
        pass

    def set_parms(self, *args, **kwargs):
        self.delay_shutdown_time = int(kwargs.get("延迟时间", 0))
        pass

    def shutdown(self):
        os.system(f"shutdown -s -f -t {self.delay_shutdown_time}")
        pass
