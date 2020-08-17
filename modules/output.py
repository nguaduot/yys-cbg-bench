#!/usr/bin/python3
# -*- coding: utf-8 -*-


from os import path
try:
    from PIL import Image
    from PIL import ImageDraw
    from PIL import ImageFont
except ModuleNotFoundError:
    pass
import re
import sys


# 中英混排等宽字体
#   等距更纱黑体 SC
#   https://github.com/be5invis/Sarasa-Gothic
#   Google Noto Sans Mono SC
#   https://github.com/googlefonts/noto-cjk
# PyInstaller 需将 fonts 文件夹打包进 .exe，运行时释放到临时文件夹
# *.spec
# a = Analysis(..., datas=[('fonts', 'fonts')], ...)
FONT_PATH = path.join('fonts', 'sarasa-mono-sc-regular.ttf')
# FONT_PATH = path.join('fonts', 'NotoSansMonoCJKsc-Regular.otf')

FONT_SIZE = 16  # 主文本字体大小
FONT_SIZE_2 = 14  # 次文本字体大小
MARGIN = (24 + 16, 24, 24, 24)  # 页边距
MARGIN_HEAD, MARGIN_FOOT = 20, 20  # 页眉-正文，正文-页脚间距
MARGIN_LINE, MARGIN_PARAGRAPH, = 4, 10  # 行距，段距
COLOR_BG = '#2b2b2b'  # 背景色
COLOR_FG = '#bbbbbb'  # 前景色（文本颜色）
COLOR_FG_2 = '#555555'  # 次前景色


def resource_path(relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller.
    base_path = getattr(sys, '_MEIPASS',
                        path.dirname(path.dirname(path.abspath(__file__))))
    return path.join(base_path, relative_path)


def draw_mark_margin(draw, margin, size_page):
    unit = 4
    index_end = (size_page[0] - 1, size_page[1] - 1)
    index_rectangles = (
        (0, 0, margin[0] - 1, unit - 1),
        (0, 0, unit - 1, margin[1] - 1),
        (index_end[0] - margin[2] + 1, 0, index_end[0], unit - 1),
        (index_end[0] - unit + 1, 0, index_end[0], margin[1] - 1),
        (index_end[0] - margin[2] + 1, index_end[1] - unit + 1,
         index_end[0], index_end[1]),
        (index_end[0] - unit + 1, index_end[1] - margin[3] + 1,
         index_end[0], index_end[1]),
        (0, index_end[1] - unit + 1, margin[0] - 1, index_end[1]),
        (0, index_end[1] - margin[3] + 1, unit - 1, index_end[1])
    )
    for index in index_rectangles:
        draw.rectangle(index, fill=COLOR_FG_2)


def draw_mark_paragraph(draw, index_paragraphs):
    unit, offset = 4, 14
    for index in index_paragraphs:
        draw.rectangle((index[0] - offset, index[1],
                        index[2] - offset + unit - 1, index[3]),
                       fill=COLOR_FG_2)


def draw_mark_key(draw, font, text_line, index_area_start):
    # python re 不支持变长后发断言
    # 如 r'(?<=黑蛋 \d+\+)\d+' 会导致
    # re.error: look-behind requires fixed-width pattern
    # TODO 需及时更检查新规则
    rules = {
        '#5394ec': {  # 加分项
            r'(?<= )500SSR|999SP': (0,),  # 500天未收录SSR/999天未收录SP 还未使用
            r'(?<=风姿百物: )(.+)\((\d+)\+\)': (1, 2, 8000, 99999),  # 外观向高收集度
            r'(?<=这个没问题: )困28超星玉藻前': (0,)
        },
        '#cc666e': {  # 需留心
            r'(?<= )(!合服)\(.+\)': (1,),  # 多服合一
            r'(?<=风姿百物: )<1000': (0,),  # 外观向收集度过低
            # r'(?<=未拥有式神: )\d+': (0, 0, 1, 999),  # 未拥有SP数量
            # r'(?<=未拥有式神: )\d+\+(\d+)': (1, 1, 1, 999),  # 未拥有SSR数量
            # r'(?:陆生|卖药郎|鬼灯|阿香|蜜桃|犬夜叉|杀生丸|桔梗|'
            # r'一护|露琪亚)(?= 0/)': (0,),  # 未拥有联动式神
            r'(?<=\[贰\] ).+ 57(\+([\d\.]+))': (1, 2, 0, 14.4)  # 无头骑士
        },
        COLOR_FG: {  # 要点
            r'(?<=黑蛋 )\d+\+(\d+)': (1,),  # 黑蛋已消耗量
            r'(?<= )雪月华庭|暖春翠庭': (0,),  # 氪金庭院皮肤
            # r'(?<=部分多号机拥有情况: ).*(烬 \d+)': (1,),  # 魂11双烬
            # r'(?<=散一速: )\+[\d\.]+': (0,)  # 散件一速
        }
    }
    unit = 4
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
                                index_area_start[1] + unit - 1),
                               fill=color)


def size_canvas(font, font_2, content, head, foot):
    height_line = sum(font.getmetrics())
    height_line_2 = sum(font_2.getmetrics())
    width_lines = []
    index_line = [MARGIN[0], MARGIN[1]]
    if head:
        index_line[1] += height_line_2 + MARGIN_HEAD
        width_lines.append(font_2.getsize(head)[0])
    for i, paragraph in enumerate(content):
        if i > 0:
            index_line[1] -= MARGIN_LINE
            index_line[1] += MARGIN_PARAGRAPH
        for line in paragraph.splitlines():
            index_line[1] += height_line + MARGIN_LINE
            width_lines.append(font.getsize(line)[0])
    if foot:
        index_line[1] -= MARGIN_LINE
        index_line[1] += MARGIN_FOOT
        index_line[1] += height_line_2 + MARGIN_LINE
        width_lines.append(font_2.getsize(foot)[0])
    return (max(width_lines) + MARGIN[0] + MARGIN[2],
            index_line[1] - MARGIN_LINE + MARGIN[3])


def text2img(file, content, head=None, foot=None):
    if type(content) not in (tuple, list, set, dict):
        content = [str(content)]
    elif type(content) is dict:
        content = list(content.values())
    font_path = resource_path(FONT_PATH)
    font = ImageFont.truetype(font_path, size=FONT_SIZE)  # 主文本字体
    font_2 = ImageFont.truetype(font_path, size=FONT_SIZE_2)  # 次文本字体
    size_img = size_canvas(font, font_2, content, head, foot)  # 预计算图片大小
    image = Image.new('RGB', size_img, COLOR_BG)
    draw = ImageDraw.Draw(image)
    # 放弃通过 font.getsize('xx')[1] 计算行高
    height_line = sum(font.getmetrics())  # 主文本行高
    height_line_2 = sum(font_2.getmetrics())  # 次文本行高
    index_line = [MARGIN[0], MARGIN[1]]  # 下一行索引
    index_paragraphs = []  # 段索引
    if head:  # 绘制页眉
        draw.text(index_line, head, fill=COLOR_FG_2, font=font_2)
        index_line[1] += height_line_2 + MARGIN_HEAD
    for i, paragraph in enumerate(content):  # 绘制正文
        if i > 0:
            index_line[1] -= MARGIN_LINE
            index_line[1] += MARGIN_PARAGRAPH
        index_paragraph = [index_line[0], index_line[1], index_line[0], 0]
        for line in paragraph.splitlines():
            draw.text(index_line, line, fill=COLOR_FG, font=font)
            draw_mark_key(draw, font, line,
                          (index_line[0], index_line[1] + height_line))
            index_line[1] += height_line + MARGIN_LINE
        index_paragraph[3] = index_line[1] - MARGIN_LINE - 1
        index_paragraphs.append(index_paragraph)
    if foot:  # 绘制页脚
        index_line[1] -= MARGIN_LINE
        index_line[1] += MARGIN_FOOT
        draw.text(index_line, foot, fill=COLOR_FG_2, font=font_2)
        index_line[1] += height_line_2 + MARGIN_LINE
    # draw_mark_margin(draw, MARGIN, size_img)
    draw_mark_paragraph(draw, index_paragraphs)
    image.save(file, 'png')
    # image.show()  # 会导致主进程挂起


def font_exists():
    return path.exists(resource_path(FONT_PATH))


def pil_exists():
    try:
        import PIL
        return True
    except ModuleNotFoundError:
        return False


if __name__ == '__main__':
    print('module: output')

