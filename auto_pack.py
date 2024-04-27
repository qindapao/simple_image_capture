#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import shutil
import os

# :TODO: 给程序增加一个漂亮一点的图标


def file_remove(file_name):
    if os.path.exists(file_name):
        os.remove(file_name)


def dir_remove(dir_name):
    if os.path.isdir(dir_name):
        shutil.rmtree(dir_name)


def del_and_clear(exe_file):
    dir_remove('build')
    dir_remove('__pycache__')
    shutil.copy(f'.\\dist\\{exe_file}', f'.\\exe\\{exe_file}')
    dir_remove('dist')
    for sub_file in os.listdir('.'):
        if sub_file.endswith('spec'):
            file_remove(sub_file)


def auto_pack():
    file_remove('.\\exe\\simple_image_capture.exe')
    subprocess.check_output(['pyinstaller', '-F', '-i' , '.\\exe\\simple_image_capture.ico' , 'simple_image_capture.py'], stderr=subprocess.STDOUT)
    del_and_clear('simple_image_capture.exe')


if __name__ == '__main__':
    auto_pack()
