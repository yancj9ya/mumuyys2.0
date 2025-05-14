from threading import Thread, Lock
import win32con
import win32gui
import time


class Pystray:
    def __init__(self, ico_path, ico_class_name, window_name="mywindowclass"):
        self._ico_path = ico_path
        self._ico_class_name = ico_class_name
        self.__window_name = window_name
        self._menu = {}
        self._lock = Lock()

    @property
    def menu(self):
        return self._menu

    @menu.setter
    def menu(self, value):
        if isinstance(value, dict):
            self._menu.update(value)
        else:
            raise TypeError("菜单必须为字典 {1024: (菜单名, fun)}")

    def left_doubleclick(self):
        print("默认：鼠标左键被双击了")

    def left_click(self):
        print("默认：鼠标左键被单击了")

    def right_doubleclick(self):
        print("默认：鼠标右键被双击了")

    def create_menu(self):
        menu = win32gui.CreatePopupMenu()
        for menu_id, (menu_name, _) in self._menu.items():
            win32gui.AppendMenu(menu, win32con.MF_STRING, menu_id, menu_name)
        return menu

    def _create_window(self):
        wc = win32gui.WNDCLASS()
        self.hinst = wc.hInstance = win32gui.GetModuleHandle(None)
        wc.lpszClassName = self.__window_name
        wc.lpfnWndProc = self.wndProc
        self.classAtom = win32gui.RegisterClass(wc)

    def create_tray_icon(self):
        self._create_window()
        self.hwnd = win32gui.CreateWindow(self.classAtom, self.__window_name, win32con.WS_OVERLAPPED | win32con.WS_SYSMENU, 0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT, 0, 0, self.hinst, None)

        icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        hicon = win32gui.LoadImage(self.hinst, self._ico_path, win32con.IMAGE_ICON, 0, 0, icon_flags)

        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        nid = (self.hwnd, 0, flags, win32con.WM_USER + 20, hicon, self._ico_class_name)
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)

    def wndProc(self, hwnd, msg, wparam, lparam):
        if msg == win32con.WM_USER + 20:
            if lparam == win32con.WM_LBUTTONDBLCLK:
                self.left_doubleclick()
            elif lparam == win32con.WM_RBUTTONDOWN:
                menu = self.create_menu()
                pos = win32gui.GetCursorPos()
                win32gui.SetForegroundWindow(hwnd)
                win32gui.TrackPopupMenu(menu, win32con.TPM_LEFTALIGN, pos[0], pos[1], 0, hwnd, None)
                win32gui.PostMessage(hwnd, win32con.WM_NULL, 0, 0)
            elif lparam == win32con.WM_LBUTTONDOWN:
                self.left_click()
            elif lparam == win32con.WM_RBUTTONDBLCLK:
                self.right_doubleclick()
        elif msg == win32con.WM_COMMAND:
            menu_id = win32gui.LOWORD(wparam)
            if menu_id in self._menu:
                _, callback = self._menu[menu_id]
                if callback:
                    with self._lock:
                        callback()
        return win32gui.DefWindowProc(hwnd, msg, wparam, lparam)

    def tray_run(self):
        self.create_tray_icon()
        while True:
            time.sleep(0.1)
            win32gui.PumpWaitingMessages()

    def run_detached(self):
        t = Thread(target=self.tray_run)
        t.daemon = True
        t.start()


if __name__ == "__main__":
    tray = Pystray("GUI/icons/icon.ico", "MyApp")
    tray.menu = {
        1024: ("菜单项1", lambda: print("执行菜单项1")),
        1025: ("退出", lambda: win32gui.DestroyWindow(tray.hwnd)),
    }
    tray.run()
