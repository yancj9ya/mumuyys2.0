import win32con
import win32gui
import win32ui
import time
from ctypes import windll

WM_LBUTTONDOWN = 0x0201
WM_SERCURSOR = 0x20
WM_MOUSEACTIVATE = 0x21
WM_MOUSEMOVE = 0x0200
WM_LBUTTONUP = 0x0202
WM_PARENTNOTIFY = 0x210

MK_LBUTTON = 0x0001
HTCLIENT = 1

PostMessage = windll.user32.PostMessageW
SendMessage = windll.user32.SendMessageW

FindWindow = win32gui.FindWindow
FindWindowEx = win32gui.FindWindowEx

mainhandle = FindWindow(None, "MuMu模拟器12")
mpyerhandle = FindWindowEx(mainhandle,None,None, "MuMuPlayer")

print(mainhandle,mpyerhandle)
def notifyparent(hwnd,x,y):
    msg=WM_PARENTNOTIFY
    wparam=WM_LBUTTONDOWN
    Lparam=y << 16 | x
    SendMessage(hwnd,msg,wparam,Lparam)
    
def mouseactivate(hwnd,thandle):
    msg=WM_MOUSEACTIVATE
    wparam=thandle
    Lparam=WM_LBUTTONDOWN << 16 | HTCLIENT
    SendMessage(hwnd,msg,wparam,Lparam)

def setcursor(hwnd,thandle):
    msg=WM_SERCURSOR
    wparam=thandle
    Lparam=WM_LBUTTONDOWN << 16 | HTCLIENT
    SendMessage(hwnd,msg,wparam,Lparam)
def left_down(hwnd,x,y):
    msg=WM_LBUTTONDOWN
    wparam=MK_LBUTTON
    Lparam=y << 16 | x
    PostMessage(hwnd,msg,wparam,Lparam)

def left_up(hwnd,x,y):
    msg=WM_LBUTTONUP
    wparam=0
    Lparam=y << 16 | x
    PostMessage(hwnd,msg,wparam,Lparam)
    
notifyparent(mainhandle,46,42)
mouseactivate(mpyerhandle,mainhandle)
#mouseactivate(mainhandle,mainhandle)
setcursor(mpyerhandle,mpyerhandle)
left_down(mpyerhandle,46,42)
time.sleep(0.2)
left_up(mpyerhandle,46,42)
