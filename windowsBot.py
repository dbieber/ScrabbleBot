import win32api, win32con
import time

def click(x0, y0):
    x0 = int(x0)
    y0 = int(y0)
    win32api.SetCursorPos((x0,y0))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0)
    time.sleep(0.5)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0)
    time.sleep(0.1)


def drag(x0, y0, x1, y1): # TODO add smoothness options
    x0 = int(x0)
    y0 = int(y0)
    x1 = int(x1)
    y1 = int(y1)
    win32api.SetCursorPos((x0,y0))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0)
    time.sleep(1.5)
    win32api.SetCursorPos((x1,y1))
    time.sleep(1.25)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0)
    time.sleep(1.25)
