#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
模块：工具
"""

from os import path
import sys

# PyInstaller 需将 fonts 文件夹打包进 .exe，运行时释放到临时文件夹
# *.spec
# a = Analysis(..., datas=[('fonts', 'fonts')], ...)
# 中英混排等宽字体: 等距更纱黑体 SC
# https://github.com/be5invis/Sarasa-Gothic
__font = path.join('fonts', 'sarasa-mono-sc-regular.ttf')
# 中英混排等宽字体: Google Noto Sans Mono SC
# https://github.com/googlefonts/noto-cjk
# __font = path.join('fonts', 'NotoSansMonoCJKsc-Regular.otf')


def res_path(relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller.
    base_path = getattr(sys, '_MEIPASS',
                        path.dirname(path.dirname(path.abspath(__file__))))
    return path.join(base_path, relative_path)


def font():
    return res_path(__font)


def font_ok():
    return path.exists(font())


if __name__ == '__main__':
    print('module: util')
