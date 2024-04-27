# :TODO: 可以升级支持多张图片同时识别
# :TODO: 可以增加声音提醒
# :TODO: 可以支持多块屏幕同时捕捉

import win32gui
import win32con
import cv2
import numpy as np
import pyautogui
import mss
import mss.tools
import time
import curses
import threading
import random
import json


with open('config.json', 'r', encoding='utf-8') as f:
    JSON_INFO = json.load(f)


# 初始化curses
stdscr = curses.initscr()
curses.start_color()
curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
stdscr.nodelay(1)  # 设置为非阻塞模式
stdscr.timeout(0)  # 设置超时时间为0，使得ASCII雨下得更快

def find_window_by_substring(substring):
    hwnds = []
    def window_enum_callback(hwnd, _):
        if substring in win32gui.GetWindowText(hwnd):
            hwnds.append(hwnd)
        return True  # 继续枚举窗口
    win32gui.EnumWindows(window_enum_callback, None)
    return hwnds[0] if hwnds else None

hwnd = find_window_by_substring('espace_notify')

def flash_window(hwnd):
    win32gui.FlashWindowEx(hwnd, win32con.FLASHW_ALL | win32con.FLASHW_TIMERNOFG, 0, 0)

def stop_flash_window(hwnd):
    win32gui.FlashWindowEx(hwnd, win32con.FLASHW_STOP, 0, 0)
    win32gui.FlashWindowEx(hwnd, win32con.FLASHW_STOP | win32con.FLASHW_CAPTION | win32con.FLASHW_TRAY, 0, 0)


# 创建ASCII雨
def ascii_rain(stop_event):
    while not stop_event.is_set():
        stdscr.clear()  # 清除屏幕
        for i in range(0, stdscr.getmaxyx()[1], 2):  # 在每个第二列上生成雨滴
            # 随机选择雨滴的长度和位置
            length = random.randint(5, 10)
            start = random.randint(0, stdscr.getmaxyx()[0] - length)
            for j in range(length):
                if j < length - 2:
                    stdscr.addstr(start + j, i, chr(random.randint(33, 126)), curses.color_pair(1))
                else:
                    stdscr.addstr(start + j, i, ' ', curses.color_pair(1))
        stdscr.refresh()
        time.sleep(0.1)  # 控制雨滴下落的速度

stop_event = threading.Event()
rain_thread = threading.Thread(target=ascii_rain, args=(stop_event,))

# 加载需要匹配的图像
template = cv2.imread('template.png', 0)
w, h = template.shape[::-1]

while True:
    # 截取屏幕快照
    with mss.mss() as sct:
        # 获取第二个显示器的信息
        monitor_number = JSON_INFO['monitor_number']
        mon = sct.monitors[monitor_number]

        # 要捕获的屏幕部分
        monitor = {
            "top": mon["top"],
            "left": mon["left"],
            "width": mon["width"],
            "height": mon["height"],
            "mon": monitor_number,
        }

        # 抓取数据
        sct_img = sct.grab(monitor)

        # 将屏幕截图转换为NumPy数组，并转换为灰度图像
        screenshot = cv2.cvtColor(np.array(sct_img), cv2.COLOR_RGB2GRAY)

    # 使用模板匹配
    res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.8  # 设置匹配阈值，可以根据需要调整
    loc = np.where(res >= threshold)

    if np.any(res >= threshold):
        # 找到匹配项，开始ASCII雨
        if not rain_thread.is_alive():
            rain_thread = threading.Thread(target=ascii_rain, args=(stop_event,))
            stop_event.clear()
            rain_thread.start()
        # flash_window(hwnd)  # 开始闪烁
    else:
        # 没有找到匹配项，停止ASCII雨并清除屏幕
        if rain_thread.is_alive():
            stop_event.set()
            rain_thread.join()
        stdscr.clear()  # 清除屏幕
        stdscr.refresh() # 刷新屏幕
        # stop_flash_window(hwnd)  # 停止闪烁

    # for pt in zip(*loc[::-1]):
    #     print(f'找到匹配项，位置在：{pt}')
    time.sleep(1)
