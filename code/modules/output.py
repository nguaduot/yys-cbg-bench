#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
模块：将文字内容优化排版生成图片
"""

from os import path
import re

try:
    from PIL import Image
    from PIL import ImageDraw
    from PIL import ImageFont
except ModuleNotFoundError:
    Image, ImageDraw, ImageFont = None, None, None

from modules import util


class Output(object):
    def __init__(self):
        self.__font_size = 16  # 主文本字体大小
        self.__font_size_2 = 14  # 次文本字体大小
        self.__margin = (24 + 16, 24, 24, 24)  # 页边距
        self.__margin_head = 20  # 页眉-正文间距
        self.__margin_foot = 20  # 正文-页脚间距
        self.__margin_line = 4  # 行距
        self.__margin_paragraph = 10  # 段距
        self.__unit = 4
        self.__color_bg = '#2b2b2b'  # 背景色
        self.__color_fg = '#bbbbbb'  # 前景色（文本颜色）
        self.__color_fg_2 = '#555555'  # 次前景色

    def _draw_mark_margin(self, draw, margin, size_page):
        index_end = (size_page[0] - 1, size_page[1] - 1)
        index_rectangles = (
            (0, 0, margin[0] - 1, self.__unit - 1),
            (0, 0, self.__unit - 1, margin[1] - 1),
            (index_end[0] - margin[2] + 1, 0, index_end[0], self.__unit - 1),
            (index_end[0] - self.__unit + 1, 0, index_end[0], margin[1] - 1),
            (index_end[0] - margin[2] + 1, index_end[1] - self.__unit + 1,
             index_end[0], index_end[1]),
            (index_end[0] - self.__unit + 1, index_end[1] - margin[3] + 1,
             index_end[0], index_end[1]),
            (0, index_end[1] - self.__unit + 1, margin[0] - 1, index_end[1]),
            (0, index_end[1] - margin[3] + 1, self.__unit - 1, index_end[1])
        )
        for index in index_rectangles:
            draw.rectangle(index, fill=self.__color_fg_2)

    def _draw_mark_paragraph(self, draw, index_paragraphs):
        offset = 14
        for index in index_paragraphs:
            draw.rectangle((index[0] - offset, index[1],
                            index[2] - offset + self.__unit - 1, index[3]),
                           fill=self.__color_fg_2)

    def _draw_mark_key(self, draw, font, text_line, index_area_start):
        # python re 不支持变长后发断言
        # 如 r'(?<=黑蛋 \d+\+)\d+' 会导致
        # re.error: look-behind requires fixed-width pattern
        # TODO 需及时更检查新规则
        rules = {
            '#5394ec': {  # 加分项
                r'(?<= )500SSR|999SP': (
                    0,
                ),  # 500天未收录SSR/999天未收录SP 还未使用
                r'(?<= )(风姿·.+?) (\d+)\+': (
                    1, 2, 8000, 99999
                ),  # 外观向高收集度
                r'(?<= )曜之阁': (
                    0,
                ),  # 曜之阁已开启
                r'(?<= )(.{1,4})\|命中 \+([\d\.]+)': (
                    1, 2, 14.4, 18
                ),  # 满速命中
                r'(?<= )(招财)(?:\|命中)? (?:57)?\+([\d\.]+)': (
                    1, 2, 14.4, 18
                ),  # 满速招财
                r'(?<=这个没问题: )困28超星玉藻前': (
                    0,
                )
            },
            '#cc666e': {  # 需留心
                r'(?<=上架中: |已取回: )!¥[\d\.]+': (
                    0,
                ),  # 售价为公示期或已取回，仅供参考
                r'(?<= )(!合服)\(.+\)': (
                    1,
                ),  # 多服合一
                r'(?<=御札 )\d+': (
                    0, 0, 0, 2899
                ),  # 御札储量不足（1500+1200+200*2）
                r'(?<= )!风姿': (
                    0,
                ),  # 外观向收集度过低
                r'(?<= )!探索·百鬼': (
                    0,
                ),  # 探索关卡的妖怪未全部发现
                # r'(?<=当下未拥有式神: )\d+': (
                #     0, 0, 1, 999
                # ),  # 未拥有SP数量
                # r'(?<=当下未拥有式神: )\d+\+(\d+)': (
                #     1, 1, 1, 999
                # ),  # 未拥有SSR数量
                # r'(?:陆生|卖药郎|鬼灯|阿香|蜜桃|犬夜叉|杀生丸|桔梗|一护|露琪亚)(?= 0/)': (
                #     0,
                # ),  # 未拥有联动式神
                r'(?<=\[贰\] ).+? 57(\+([\d\.]+))': (
                    1, 2, 0, 14.4
                )  # 无头骑士
            },
            self.__color_fg: {  # 要点
                r'(?<= )!(\d+)级': (
                    0, 1, 0, 44
                ),  # 等级低于45级
                r'(?<=黑蛋 )\d+\+(\d+)': (
                    1,
                ),  # 黑蛋已消耗量
                r'(?<= 魂玉 )\d+': (
                    0, 0, 10, 9999999
                ),  # 魂玉留存超过10
                r'(?<= )(名声大振) 5000\+': (
                    1,
                ),  # 成就点数超过5000(可报名特邀测试)
                r'(?<=部分多号机拥有情况: ).*?(烬 (\d+))': (
                    1, 2, 2, 999
                ),  # 魂11双烬硬件
                r'(?<= )雪月华庭|暖春翠庭': (
                    0,
                ),  # 氪金庭院皮肤
                r'(?<= )蝶步韶华': (
                    0,
                ),  # 不知火氪金典藏皮肤
                # r'(?<=散一速: )\+[\d\.]+': (
                #     0,
                # )  # 散件一速
            }
        }
        for color, patterns in rules.items():
            for pattern, span in patterns.items():
                it = re.finditer(pattern, text_line)
                for match in it:
                    if len(span) > 1 and not span[2] <= float(
                        match.group(span[1])
                    ) <= span[3]:
                        continue
                    index_x1 = font.getsize(
                        text_line[:match.span(span[0])[0]]
                    )[0]
                    index_x2 = font.getsize(
                        text_line[:match.span(span[0])[1]]
                    )[0] - 1
                    draw.rectangle((index_area_start[0] + index_x1,
                                    index_area_start[1],
                                    index_area_start[0] + index_x2,
                                    index_area_start[1] + self.__unit - 1),
                                   fill=color)

    def _size_canvas(self, font, font_2, content, head, foot):
        height_line = sum(font.getmetrics())
        height_line_2 = sum(font_2.getmetrics())
        width_lines = []
        index_line = [self.__margin[0], self.__margin[1]]
        if head:
            index_line[1] += height_line_2 + self.__margin_head
            width_lines.append(font_2.getsize(head)[0])
        for i, paragraph in enumerate(content):
            if i > 0:
                index_line[1] -= self.__margin_line
                index_line[1] += self.__margin_paragraph
            for line in paragraph.splitlines():
                index_line[1] += height_line + self.__margin_line
                width_lines.append(font.getsize(line)[0])
        if foot:
            index_line[1] -= self.__margin_line
            index_line[1] += self.__margin_foot
            index_line[1] += height_line_2 + self.__margin_line
            width_lines.append(font_2.getsize(foot)[0])
        return (max(width_lines) + self.__margin[0] + self.__margin[2],
                index_line[1] - self.__margin_line + self.__margin[3])

    def text2img(self, file_font, file_out, content, head=None, foot=None):
        if type(content) not in (tuple, list, set, dict):
            content = [str(content)]
        elif type(content) is dict:
            content = list(content.values())
        font = ImageFont.truetype(file_font, size=self.__font_size)  # 主文本字体
        font_2 = ImageFont.truetype(file_font, size=self.__font_size_2)  # 次文本字体
        size_img = self._size_canvas(font, font_2, content, head, foot)  # 预计算图片大小
        image = Image.new('RGB', size_img, self.__color_bg)
        draw = ImageDraw.Draw(image)
        # 放弃通过 font.getsize('xx')[1] 计算行高
        height_line = sum(font.getmetrics())  # 主文本行高
        height_line_2 = sum(font_2.getmetrics())  # 次文本行高
        index_line = [self.__margin[0], self.__margin[1]]  # 下一行索引
        index_paragraphs = []  # 段索引
        if head:  # 绘制页眉
            draw.text(index_line, head, fill=self.__color_fg_2, font=font_2)
            index_line[1] += height_line_2 + self.__margin_head
        for i, paragraph in enumerate(content):  # 绘制正文
            if i > 0:
                index_line[1] -= self.__margin_line
                index_line[1] += self.__margin_paragraph
            index_paragraph = [index_line[0], index_line[1], index_line[0], 0]
            for line in paragraph.splitlines():
                draw.text(index_line, line, fill=self.__color_fg, font=font)
                self._draw_mark_key(draw, font, line, (
                    index_line[0], index_line[1] + height_line
                ))
                index_line[1] += height_line + self.__margin_line
            index_paragraph[3] = index_line[1] - self.__margin_line - 1
            index_paragraphs.append(index_paragraph)
        if foot:  # 绘制页脚
            index_line[1] -= self.__margin_line
            index_line[1] += self.__margin_foot
            draw.text(index_line, foot, fill=self.__color_fg_2, font=font_2)
            index_line[1] += height_line_2 + self.__margin_line
        # self._draw_mark_margin(draw, MARGIN, size_img)
        self._draw_mark_paragraph(draw, index_paragraphs)
        image.save(file_out, 'png')
        # image.show()  # 会导致主进程挂起


def enabled():
    try:
        import PIL
    except ModuleNotFoundError:
        return False
    return util.font_ok()


def text2img(file_out, content, head=None, foot=None):
    o = Output()
    o.text2img(util.font(), file_out, content, head, foot)


if __name__ == '__main__':
    print('module: output')
