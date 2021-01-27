#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# 号来
# 阴阳师藏宝阁衍生小工具，用于提取游戏帐号数据要点并生成报告。
#
# 了解更多请前往 GitHub 查看项目：https://github.com/nguaduot/yys-cbg-bench
#
# author: @nguaduot 痒痒鼠@南瓜多糖
# version: 1.6.210128
# date: 20210128

import datetime
import getopt
import json
import multiprocessing
import os
from os import path
import re
import subprocess
import sys
import threading
from threading import Thread
import time
import urllib.parse
from urllib import request

from modules import output
from modules import pick_dwarf
from modules import yhsuit

PROG = 'yys-cbg-bench'
AUTH = 'nguaduot'
VER = '1.6'
VERSION = '1.6.210128'
REL = 'github.com/nguaduot/yys-cbg-bench'
COPYRIGHT = '%s v%s @%s %s' % (PROG, VERSION, AUTH, REL)
HELP = (
    '+ 选项：'
    '\n  -h, --help     帮助'
    '\n  -v, --version  程序版本'
    '\n  -l, --lite     输出结果精简化(未指定则输出完整结果)'
    '\n  -u, --url      藏宝阁商品详情链接'
    '\n+ 若未指定 -u, 程序会读取未知参数, 若也无未知参数, 不启动程序'
    '\n+ 不带任何参数也可启动程序, 会有参数输入引导',
    '输出结果:',
    '{上架中/已售出/已取回/未上架}: ¥{售价，公示期/已取回状态将提示“!”} {签到天数}天 '
    '!{若不满级则显示等级提示} '
    '!{若检测到合服则显示提示, 多服合一无法获知归属服, 需留心}'
    '\n  金币 {金币} '
    '黑蛋 {\'御行达摩\'数量+推测已消耗量(据此可了解练度)} '
    '体力 {体力} '
    '勾玉 {勾玉} '
    '蓝票 {神秘的符咒+现世符咒} '
    '御札 {御札/金御札} '
    '魂玉 {留存魂玉数量, 大于0时显示}'
    '\n  关键成就: {风姿度, 据此可了解外观向收集量(皮肤/头像框等)} '
    '{成就点数, 5000+可报名特邀测试} {已达成的最高非酋成就} {探索关卡的妖怪是否全部发现}',
    '图鉴SP&SSR式神: {\'500天未收录SSR\'未使用则显示} {\'999天未收录SP\'未使用则显示}'
    '\n  当下未拥有式神...{提示除联动的最新SP/SSR式神}: '
    '{于当下版本的未拥有SP数量}+{于当下版本的未拥有SSR数量}'
    '\n    SP碎片收集: '
    '{未拥有式神(图鉴已点亮也可能未拥有, 需留心)} {该式神碎片量, 据此可知有无碗} ...'
    '\n    SSR碎片收集: '
    '{未拥有式神(图鉴已点亮也可能未拥有, 需留心)} {该式神碎片量, 据此可知有无碗} ...'
    '\n  关键多号机拥有情况: {式神} {该式神拥有数量} ...',
    '联动式神拥有&碎片收集情况:'
    '\n  {联动期数}: {该期式神} '
    '{拥有数量(低稀有度低星式神无法获知)}/{碎片量(低稀有度式神无法获知)} ...'
    '\n  ...',
    '已收集皮肤: {曜之阁已开启则显示}'
    '\n  庭院: 初语谧景 + {除初始之外的其他庭院} ...'
    '\n  氪金典藏...{提示最新皮肤}: {已收集的氪金式神典藏皮肤数量}'
    '\n    {皮肤名} ...',
    '六星满级/满级/六星御魂: {六星满级御魂数量}/{各星级满级御魂总量}/'
    '{藏宝阁未提供未满级御魂数据, 因此六星御魂总量无法查到, 请知悉}/'
    '\n  满级普通御魂: {满级非首领御魂数量}'
    '\n    {两件套属性} {该类御魂数量}'
    '\n    ...'
    '\n  满级首领御魂: {满级首领御魂数量}'
    '\n    荒骷髅 {\'荒骷髅\'数量}'
    '\n    歌伎 {\'鬼灵歌伎\'数量}',
    '散一速: {散件套一速} 招财 {招财套一速}'
    '\n  [{位置}] {该位置散一速套御魂, 以及其余速度满收益御魂} {副属性\'速度\'值} ...'
    '\n  ...',
    '高分暴击&暴伤御魂: {高分暴击御魂数量}+{高分暴击伤害御魂数量}'
    '\n  陆|暴击 输出分:'
    '\n    {陆号位主属性\'暴击\'的高分御魂} '
    '{该御魂分数, 按有效属性\'攻击加成\'/\'速度\'/\'暴击\'/\'暴击伤害\'评分, '
    '非首领御魂5+, 首领御魂7+} ...'
    '\n    ...'
    '\n  陆|暴击伤害 输出分&副属性暴击值:'
    '\n    {陆号位主属性\'暴击伤害\'的高分御魂} '
    '{该御魂分数, 按有效属性\'攻击加成\'/\'速度\'/\'暴击\'/\'暴击伤害\'评分, '
    '非首领御魂5+, 首领御魂7+}: 暴击 {副属性\'暴击\'值}'
    '\n    ...',
    '部分御魂方案:'
    '\n  {是否能做}: {何用途的何式神} {御魂套装} '
    '{加速计算的分数限制, 按有效属性\'攻击加成\'/\'速度\'/\'暴击\'/\'暴击伤害\'评分}'
    '\n  ...'
    '\n* 通过计算御魂方案来粗略了解御魂池及练度, 内置的几种方案(从易到难排序):'
    '\n  1. 真蛇副本用到的超星针歌小小黑, 攻暴值未作限制, 基本满暴就能用'
    '\n  2. 探索困28副本用到的超星破荒/破歌茨林, 破荒攻暴 15815+, 破歌 15723+'
    '\n     数据参考: https://nga.178.com/read.php?tid=21014251'
    '\n  3. 觉醒十层副本用到的高速破荒茨林, 速度 160+, 攻暴 15810+'
    '\n     数据参考: https://nga.178.com/read.php?tid=15698562'
    '\n  4. 御魂十层副本用到的高速狂荒/破荒玉藻前, 速度 162+, '
    '狂荒攻暴 15696~20090, 破荒 17843~20090'
    '\n     数据参考: https://nga.178.com/read.php?tid=20569256'
    '\n  5. 探索困28副本用到的超星破荒玉藻前, 攻暴 21644+'
    '\n     数据参考: https://nga.178.com/read.php?tid=21014251'
    '\n* 计算过程可能比较耗时, 已最大程度优化, 分派大量子进程同时计算, CPU核心全利用. '
    '\'痒痒鼠, 烤机不?\''
)

# TODO: 以下常量需留意随版本更新而检查更新
HERO_RARITY = ['', 'N', 'R', 'SR', 'SSR', 'SP']  # 式神稀有度
HEROES_X = {
    '第一期': {'奴良陆生': 4},
    '第二期': {'卖药郎': 4},
    '第三期': {'鬼灯': 4, '阿香': 3, '蜜桃&芥子': 2},
    '第四期': {'犬夜叉': 4, '杀生丸': 4, '桔梗': 4},
    '第五期': {'黑崎一护': 4, '朽木露琪亚': 3},
    '第六期': {'灶门炭治郎': 4, '灶门祢豆子': 4}
}  # 各期联动式神及其稀有度
HEROES_ABBR = {
    # 联动
    '奴良陆生': '陆生',
    '蜜桃&芥子': '蜜桃',
    '黑崎一护': '一护',
    '朽木露琪亚': '露琪亚',
    '灶门炭治郎': '炭治郎',
    '灶门祢豆子': '祢豆子',
    # SP
    '少羽大天狗': '小天狗',
    '炼狱茨木童子': '茨林',
    '稻荷神御馔津': '神御',
    '苍风一目连': '苍连',
    '赤影妖刀姬': '赤刀',
    '骁浪荒川之主': '浪川',
    '烬天玉藻前': '烬',
    '鬼王酒吞童子': '鬼吞',
    '天剑韧心鬼切': '奶切',
    '聆海金鱼姬': '大金鱼',
    '浮世青行灯': '大灯',
    '待宵姑获鸟': '大姑',
    '麓铭大岳丸': '鹿丸',
    '夜溟彼岸花': '夜溟花',
    # SSR
    '酒吞童子': '酒吞',
    '荒川之主': '荒川',
    '茨木童子': '茨木',
    '八岐大蛇': '大蛇'
}  # 尽量不超过四个字, 使用 HEROES_ABBR.get(x, x) 取值而非 HEROES_ABBR[x]
YUHUN_ABBR = {
    '涅槃之火': '涅槃',
    '地藏像': '地藏',
    '日女巳时': '日女',
    '招财猫': '招财',
    '魍魉之匣': '魍魉',
    '鬼灵歌伎': '歌伎'
}  # 使用 YUHUN_ABBR.get(x, x) 取值而非 YUHUN_ABBR[x]
ATTR_ABBR = {
    '暴击伤害': '暴伤',
    '效果命中': '命中',
    '效果抵抗': '抵抗'
}  # 使用 ATTR_ABBR.get(x, x) 取值而非 ATTR_ABBR[x]
RMB_HERO_SKINS = {
    '神宫金社': -1,  # 荒（限定活动获取）
    '青莲蜕梦': 128,  # 玉藻前
    '响魂醉曲': 128,  # 酒吞
    '蝶步韶华': 128,  # 不知火
    # '冷宴狐影': 0,  # 烬（已回炉未上架）
    '花引冥烛': 128,  # 彼岸花
    '古桥水巷': 128,  # 椒图
    '永夜无眠': 168,  # 泷夜叉姬
    '化烟': 108,  # 清姬
    # '胧月': 0,  # 辉夜姬（非氪金，为百绘罗衣作品，通过活动获取）
    '金鳞航梦': 148,  # 铃鹿御前
    '紫藤花烬': 108,  # 姑获鸟
    '锦羽金鹏': 128,  # 小天狗
    '琥珀龙魂': 148,  # 大岳丸
    '百鬼夜行': 148,  # 烬
    '福鲤霓裳': 188  # 缘结神
}  # 氪金式神皮肤（一般为“典藏”，且附赠同名头像框）
HEROES_PANEL = {
    '炼狱茨木童子': {
        '攻击': 3323.2, '防御': 379.26, '生命': 10253.8,
        '速度': 112, '暴击': 0.15, '暴击伤害': 1.5,
        '效果命中': 0, '效果抵抗': 0
    },
    '玉藻前': {
        '攻击': 3350, '防御': 352.8, '生命': 12532.2,
        '速度': 110, '暴击': 0.12, '暴击伤害': 1.6,
        '效果命中': 0, '效果抵抗': 0
    },
    '黑童子': {
        '攻击': 3376.8, '防御': 383.67, '生命': 9912.04,
        '速度': 109, '暴击': 0.09, '暴击伤害': 1.5,
        '效果命中': 0, '效果抵抗': 0
    }
}  # 式神基础面板

LITE = False  # 输出结果精简化(且不考核御魂池)
USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
              ' AppleWebKit/537.36 (KHTML, like Gecko)'
              ' Chrome/84.0.4147.89 Safari/537.36')

SERVER = {}  # 区服, 用以检测多服合一
HERO = {}  # 式神，用以检测全图鉴
DATA_SOURCE = {}  # 商品源数据
DATA_RESULT = []  # 分析结果

lock = threading.Lock()
thread_fetch_config = None

callback_cio = None  # 回调方法


def save(url_equip):
    dir_cbg = path.join(path.dirname(path.abspath(sys.argv[0])), 'cbg')
    if not path.isdir(dir_cbg):
        os.mkdir(dir_cbg)
    if not DATA_SOURCE:
        return
    # 删除 Windows 文件名中不允许出现的字符, 以及无法正常显示且会导致 IO 异常的控制字符
    # 使用当前卖家角色昵称 equip_name，而非 seller_name，其会随买家再次上架而改变
    seller = re.sub(
        r'[\\/:?"<>|\u0000-\u001F\u007F-\u009F]', '',
        DATA_SOURCE['equip']['equip_name']
    )
    t = datetime.datetime.strptime(DATA_SOURCE['equip']['create_time'],
                                   '%Y-%m-%d %H:%M:%S')
    file_base = path.join(dir_cbg, 'cbg_%s_%s_%s_%s' % (
        DATA_SOURCE['equip']['area_name'], DATA_SOURCE['equip']['server_name'],
        seller, t.strftime('%Y%m%d%H%M%S')
    ))
    file_source = '%s.json' % file_base
    # file_fluxxu = path.join(dir_cbg, ('yyx_snapshot_cbg_%s.json'
    #                                   % data_source['equip']['seller_name']))
    file_fluxxu = '%s_yyx_snapshot.json' % file_base
    file_result = '%s_bench%s.json' % (file_base, '_lite' if LITE else '')
    file_result_2 = '%s_bench%s.txt' % (file_base, '_lite' if LITE else '')
    file_result_3 = '%s_bench%s.png' % (file_base, '_lite' if LITE else '')
    # if path.isfile(file_source):
    #     cio('源数据已存在 \'%s\'' % path.basename(file_source), 'info')
    with open(file_source, 'w', encoding='utf-8') as f:
        json.dump(DATA_SOURCE, f)
    cio('已保存源数据 \'%s\'' % path.basename(file_source), 'info')
    # if path.isfile(file_fluxxu):
    #     cio('痒痒熊快照格式数据已存在 \'%s\'' % '*_yyx_snapshot.json', 'info')
    data_fluxxu = data_cbg2fluxxu(DATA_SOURCE, url_equip)
    with open(file_fluxxu, 'w', encoding='utf-8') as f:
        json.dump(data_fluxxu, f)
    cio('已保存痒痒熊快照格式数据 \'%s\'' % '*_yyx_snapshot.json', 'info')
    if not DATA_RESULT:
        return
    with open(file_result, 'w', encoding='utf-8') as f:
        json.dump(DATA_RESULT, f)
    cio('已保存分析结果 \'*_%s\'' % file_result.rsplit('_', 1)[1], 'info')
    with open(file_result_2, 'w', encoding='utf-8') as f:
        f.write('\n'.join([item['out'] for item in DATA_RESULT]))
    cio('已保存分析结果 \'*_%s\'' % file_result_2.rsplit('_', 1)[1], 'info')
    if output.enabled():
        output.text2img(file_result_3, [item['out'] for item in DATA_RESULT],
                        head=path.basename(file_result_3), foot=COPYRIGHT)
        cio('已保存分析结果 \'*_%s\'' % file_result_3.rsplit('_', 1)[1], 'info')
        view(file_result_3)
    else:
        cio('\'PIL\'库或字体缺失, 未将结果生成图片 \'*_%s\''
            % file_result_3.rsplit('_', 1)[1], 'warn')


def panel_str2val(str_val):
    if str_val.endswith('%'):
        return float(str_val[:-1]) / 100
    return float(str_val)


def infer_damo_yx_cost(data):
    """推测黑蛋消耗量

    统计 SP、SSR 阶式神技能升级情况来推测消耗的黑蛋数。
    并非准确，但可参考。

    Args:
        data: data_source['equip']['equip_desc']

    Returns:
        int: 黑蛋消耗量
    """
    heroes_onmyoji = {
        10: '晴明', 11: '神乐', 13: '源博雅', 12: '八百比丘尼',
        900: '神龙', 901: '白藏主', 903: '黑豹', 902: '孔雀'
    }  # 阴阳师及其御灵稀有度均被设定为SSR, 即 item['rarity'] == 4
    data_heroes = list(data['heroes'].values())
    data_sp_ssr = [item for item in data_heroes if (
            item['rarity'] == 5 or item['rarity'] == 4
    ) and item['heroId'] not in heroes_onmyoji]
    return sum(
        [max(info[1] - 1, 0) for hero in data_sp_ssr for info in hero['skinfo']]
    )


def bench_inventory(data, data_game):
    achieves = {
        'fzbw': {
            -1: {
                'name': '!风姿 <1000'
            },
            40701: {
                'name': '风姿·春时雨 1000+',
                'desc': '风姿度达到1000'
            },
            40702: {
                'name': '风姿·花信风 3000+',
                'desc': '风姿度达到3000'
            },
            40703: {
                'name': '风姿·星月夜 5000+',
                'desc': '风姿度达到5000'
            },
            40704: {
                'name': '风姿·銮华扇 8000+',
                'desc': '风姿度达到8000'
            },
            40705: {
                'name': '风姿·神霖羽 12000+',
                'desc': '风姿度达到12000'
            }
        },  # 风姿百物系列(空间徽章-风姿百物系列仅记录5000+)
        'cj': {
            -1: {
                'name': '!成就点 <1000'
            },
            10119: {
                'name': '初入平安京 1000+',
                'desc': '成就点数突破1000'
            },
            10120: {
                'name': '浮名绊身 2000+',
                'desc': '成就点数突破2000'
            },
            10121: {
                'name': '不负盛名 3000+',
                'desc': '成就点数突破3000'
            },
            10122: {
                'name': '闻名京都 4000+',
                'desc': '成就点数突破4000'
            },
            10123: {
                'name': '名声大振 5000+',
                'desc': '成就点数突破5000'
            }
        },  # 成就点数系列
        'fq': {
            -1: {
                'name': '!非酋'
            },
            235: {
                'name': '非酋·初级 100',
                'desc': '连续100次神秘的符咒、现世符咒或勾玉召唤没有SSR'
            },
            236: {
                'name': '非酋·中级 200',
                'desc': '连续200次神秘的符咒、现世符咒或勾玉召唤没有SSR'
            },
            237: {
                'name': '非酋·高级 300',
                'desc': '连续300次神秘的符咒、现世符咒或勾玉召唤没有SSR'
            },
            238: {
                'name': '非洲·阴阳师 400',
                'desc': '连续400次神秘的符咒、现世符咒或勾玉召唤没有SSR'
            },
            239: {
                'name': '非洲·大阴阳师 500',
                'desc': '连续500次神秘的符咒、现世符咒或勾玉召唤没有SSR'
            }
        },  # 非酋系列
        'tsbg': {
            -1: {
                'name': '!探索·百鬼'
            },
            20400: {
                'name': '探索·百鬼 41',
                'desc': '发现全部探索关卡的妖怪'
            }
        }  # 探索·百鬼
    }  # 成就
    data_damo = data_game['damo_count_dict']
    data_achieve = data_game.get(
        'achieve_ids', []
    )  # 成就（注意，早期藏宝阁未包含该数据）
    result = {
        'data': {
            'status': data['equip']['status'],
            'pass_fair_show': data['equip']['pass_fair_show'] == 1,
            'price': data['equip']['price'],  # 售价(单位: 分)
            'days': data_game['sign_days'],  # 签到天数
            'lv': data_game['lv'],  # 等级
            'money':  data_game['money'],  # 金币
            'gouyu':  data_game['goyu'],  # 勾玉
            'smdfz': data_game['gameble_card'],  # 蓝票(源数据拼写错误)
            'xsfz': data_game['ar_gamble_card'],  # 紫票
            'strength':  data_game['strength'],  # 体力
            'yuzha':  data_game['soul_jade'],  # 御札
            'yuzha_gold': data_game['currency_900188'],  # 金御札
            'hunyu': data_game['hunyu'],  # 魂玉
            'damo_yx': sum(
                [num for damoes in data_damo.values()
                 for damo, num in damoes.items() if damo == '411']
            ),  # 黑蛋
            'damo_yx_cost': infer_damo_yx_cost(data_game),  # 已消耗黑蛋量
            'servers': [data['equip']['server_name']],  # 服务器
            'achieves': []  # 成就
        },
        'out': ''
    }
    for achieve in achieves.values():
        for achieve_id in list(achieve)[::-1]:
            if achieve_id in data_achieve:
                result['data']['achieves'].append(achieve[achieve_id])
                break
        else:
            result['data']['achieves'].append(achieve[-1])
    thread_fetch_config.join()  # 等待区服列表抓取完毕
    if data['equip']['serverid'] in SERVER:
        result['data']['servers'] = list(SERVER[data['equip']['serverid']])
    if result['data']['status'] == 2:
        result['out'] = '上架中: '
        if not result['data']['pass_fair_show']:
            result['out'] += '!'
    elif result['data']['status'] == 3:  # 被下单
        result['out'] = '上架中: '
    elif result['data']['status'] == 0:
        result['out'] = '已取回: '
        result['out'] += '!'
    elif result['data']['status'] == 6:
        result['out'] = '已售出: '
    else:
        result['out'] = '未上架:'
    result['out'] += '¥%.0f' % (result['data']['price'] / 100)
    result['out'] += ' %d天' % result['data']['days']
    if result['data']['lv'] < 60:
        result['out'] += ' !%d级' % result['data']['lv']
    if len(result['data']['servers']) > 1:
        result['out'] += ' !合服(%s)' % '/'.join(result['data']['servers'])
    result['out'] += ('\n  金币 %.0fw 黑蛋 %d+%d 体力 %.1fw'
                      ' 勾玉 %d 蓝票 %d+%d 御札 %d/%d') % (
        result['data']['money'] / 10000,
        result['data']['damo_yx'],
        result['data']['damo_yx_cost'],
        result['data']['strength'] / 10000,
        result['data']['gouyu'],
        result['data']['smdfz'],
        result['data']['xsfz'],
        result['data']['yuzha'],
        result['data']['yuzha_gold']
    )
    if result['data']['hunyu']:  # 仅在留存魂玉未消耗完时显示
        result['out'] += ' 魂玉 %d' % result['data']['hunyu']
    result['out'] += '\n  关键成就:'
    for achieve in result['data']['achieves']:
        result['out'] += ' %s' % achieve['name']
    return result


def bench_heroes(data):
    # 全部式神列表有以下 v1 v2 两种获取方法：
    # v2 从 game_auto_config.json 接口获取（更新并不及时）
    # v1 获取的式神列表仅代表上架时的图鉴情况，而非当下版本，即不会包含后续新出式神
    thread_fetch_config.join()  # 等待式神列表抓取完毕
    heroes_x_v2 = [hero for heroes in HEROES_X.values() for hero in heroes]
    heroes_sp_ssr_v2 = [name for hid, name in sorted(
        {**HERO[5], **HERO[4]}.items()
    ) if name not in heroes_x_v2]  # 按发布时间升序排列
    heroes_sp_v2 = [name for hid, name in sorted(HERO[5].items())
                    if name not in heroes_x_v2]  # 按发布时间升序排列
    heroes_ssr_v2 = [name for hid, name in sorted(HERO[4].items())
                     if name not in heroes_x_v2]  # 按发布时间升序排列
    # heroes_sp_ssr_v1 = [info[0] for hid, info in sorted(
    #     {**data['hero_history']['sp'], **data['hero_history']['ssr']}.items()
    # ) if type(info) is list]
    # heroes_sp_v1 = [info[0] for hid, info in sorted(
    #     data['hero_history']['sp'].items()
    # ) if type(info) is list]
    # heroes_ssr_v1 = [info[0] for hid, info in sorted(
    #     data['hero_history']['ssr'].items()
    # ) if type(info) is list]
    data_heroes = list(data['heroes'].values())
    data_sp_ssr = [item['name'] for item in data_heroes
                   if item['rarity'] == 5 or item['rarity'] == 4]
    data_fragments_sp_ssr = list(data['hero_fragment'].values())
    data_fragments_sp_ssr = {
        item['name']: item['num'] for item in data_fragments_sp_ssr
    }
    # heroes_sp_ssr_lost = [hero for hero in heroes_sp_ssr_v2
    #                       if hero not in data_sp_ssr]
    heroes_sp_lost = [hero for hero in heroes_sp_v2
                      if hero not in data_sp_ssr]
    heroes_ssr_lost = [hero for hero in heroes_ssr_v2
                       if hero not in data_sp_ssr]
    result = {'data': {
        'sp': heroes_sp_v2,
        'ssr': heroes_ssr_v2,
        'sp_lost': {hero: 0 for hero in heroes_sp_lost},
        'ssr_lost': {hero: 0 for hero in heroes_ssr_lost},
        'multi': {
            '烬天玉藻前': 0, '鬼王酒吞童子': 0,
            '酒吞童子': 0, '玉藻前': 0, '八岐大蛇': 0, '不知火': 0,
        },  # TODO: 需留意随版本更新而检查更新
        'ssr_coin': data['ssr_coin'] == 1,  # 「500天未收录SSR」是否还未使用
        'sp_coin': data.get(
            'sp_coin', 0
        ) == 1  # 「999天未收录SP」是否还未使用（注意，早期藏宝阁未包含该数据）
    }, 'out': '图鉴SP&SSR式神:'}
    for hero in result['data']['sp_lost']:
        result['data']['sp_lost'][hero] = data_fragments_sp_ssr.get(hero, 0)
    for hero in result['data']['ssr_lost']:
        result['data']['ssr_lost'][hero] = data_fragments_sp_ssr.get(hero, 0)
    for hero in result['data']['multi']:
        result['data']['multi'][hero] = len(
            [item for item in data_sp_ssr if item == hero]
        )
    if result['data']['ssr_coin']:
        result['out'] += ' 500SSR'
    if result['data']['sp_coin']:
        result['out'] += ' 999SP'
    result['out'] += '\n  当下未拥有式神...%s: %d+%d' % (
        HEROES_ABBR.get(heroes_sp_ssr_v2[-1], heroes_sp_ssr_v2[-1]),
        len(heroes_sp_lost), len(heroes_ssr_lost)
    )  # 显示最新式神，便于自行判断数据时效性
    if heroes_sp_lost:
        result['out'] += '\n    SP碎片收集:'
        for hero, num in result['data']['sp_lost'].items():
            result['out'] += ' %s %d' % (HEROES_ABBR.get(hero, hero), num)
    if heroes_ssr_lost:
        result['out'] += '\n    SSR碎片收集:'
        for hero, num in result['data']['ssr_lost'].items():
            result['out'] += ' %s %d' % (HEROES_ABBR.get(hero, hero), num)
    result['out'] += '\n  关键多号机拥有情况:'
    for hero, num in result['data']['multi'].items():
        result['out'] += ' %s %d' % (HEROES_ABBR.get(hero, hero), num)
    return result


def bench_heroes_x(data):
    """联动式神

    源数据中的式神数据仅包含全部星级 SP、SSR 阶、五星及以上其他稀有度。
    源数据中的式神碎片数据仅包含 SP、SSR 阶。
    源数据中的图鉴数据仅包含 SP、SSR、联动。
    因此对于 阿香、蜜桃&芥子、朽木露琪亚，
    可以确定未拥有，但无法确定拥有（即可能已被返消耗，如返魂），
    也无法获取其碎片保有量。

    Args:
        data:

    Returns:
    """
    data_heroes = list(data['heroes'].values())
    data_fragments = list(data['hero_fragment'].values())
    x_never_owm = [info[0] for info in data['hero_history']['x'].values()
                   if type(info) is list and info[1] == 0]
    heroes_x = {hero: len(
        [item for item in data_heroes if item['name'] == hero]
    ) for heroes in HEROES_X.values() for hero in heroes}
    fragments_sp_ssr = {
        item['name']: item['num'] for item in data_fragments
    }  # 仅包含了SSR/SP阶, 且碎片量至少一片
    result = {'data': {
        'heroes': heroes_x,
        'fragments': {hero: fragments_sp_ssr.get(hero, 0)
                      for heroes in HEROES_X.values() for hero in heroes}
    }, 'out': '联动式神拥有&碎片收集情况:'}
    for i, heroes in HEROES_X.items():
        result['out'] += '\n  %s:' % i
        for hero, rarity in heroes.items():
            if heroes_x[hero]:  # 已拥有至少一只
                num_hero = str(heroes_x[hero])
            elif hero in x_never_owm:  # 未拥有
                num_hero = '0'
            else:  # 无法确定(SR/R阶会出现这种情况: 可能有五星以下的, 可能全被消耗了)
                num_hero = '?'
            if rarity == 5 or rarity == 4:  # SP、SSR
                num_fragment = str(fragments_sp_ssr.get(hero, 0))
            else:  # 其他稀有度碎片信息未记录
                num_fragment = '-'
            result['out'] += ' %s %s/%s' % (HEROES_ABBR.get(hero, hero),
                                            num_hero, num_fragment)
    return result


def bench_skins(data):
    data_skin_yard = data['skin']['yard']  # 不会包含默认庭院皮肤
    data_skin_hero = [item[1] for item in data['skin']['ss']]
    result = {
        'data': {
            'yzg': data['yzg'],  # 曜之阁
            'skin_yards': [item[1] for item in data_skin_yard],  # 庭院
            'skin_heroes': {name: rmb for name, rmb in RMB_HERO_SKINS.items()
                            if name in data_skin_hero},  # 氪金式神皮肤
        },
        'out': '已收集皮肤:'
    }
    if result['data']['yzg']['open']:  # 曜之阁已开启
        result['out'] += ' 曜之阁'
    result['out'] += '\n  庭院: 初语谧景'
    if result['data']['skin_yards']:
        result['out'] += ' + %s' % ' '.join(result['data']['skin_yards'])
    result['out'] += '\n  氪金典藏...%s: %d' % (
        list(RMB_HERO_SKINS.keys())[-1], len(result['data']['skin_heroes'])
    )  # 显示最新皮肤，便于自行判断数据时效性
    if result['data']['skin_heroes']:
        result['out'] += '\n    %s' % ' '.join(result['data']['skin_heroes'])
    # result['out'] += '\n  氪金典藏:\n    '
    # for name, rmb in result['data']['skin_heroes'].items():
    #     result['out'] += (
    #             ' %s ¥%d' % (name, rmb)
    #     ) if rmb >= 0 else (
    #             ' %1s ¥-' % name
    #     )
    return result


def bench_yuhuns(data_game, data_yuhun):
    kinds_expand = {'狂骨', '破势', '招财猫', '蚌精', '鬼灵歌伎', '荒骷髅'}
    total = data_game['equips_summary']  # 全星级全等级御魂总数
    # level_15 = data_game['level_15']  # 满级御魂数
    data_15 = [item for item in data_yuhun if item['level'] == 15]
    data_15_6 = [item for item in data_15 if item['star'] == 6]
    result = {
        'data': {
            'total': total,
            'level_15': len(data_15),
            'level_15_star_6': len(data_15_6),
            'attr_dbl': {},
            'attr_sgl': {}
        },
        'out': '六星满级/满级/六星御魂: %d/%d/<=%d' % (
            len(data_15_6), len(data_15), total
        )
    }
    for attr_dbl, preset in pick_dwarf.ATTRS_DBL.items():
        result['data']['attr_dbl'][attr_dbl] = {}
        for kind in preset[1]:
            result['data']['attr_dbl'][attr_dbl][kind] = len(
                [item for item in data_15 if item['kind'] == kind]
            )
    for kind in pick_dwarf.KINDS_NAME_SGL:
        result['data']['attr_sgl'][kind] = len(
            [item for item in data_15 if item['kind'] == kind]
        )
    result['out'] += '\n  满级普通御魂: %d' % sum(
        [num for kinds in result['data']['attr_dbl'].values()
         for num in kinds.values()]
    )
    for attr_dbl, kinds in result['data']['attr_dbl'].items():
        result['out'] += '\n    %s %d' % (attr_dbl, sum(kinds.values()))
        for kind in kinds_expand:
            if kind in kinds:
                result['out'] += ': %s %d' % (
                    YUHUN_ABBR.get(kind, kind), kinds[kind]
                )
    result['out'] += '\n  满级首领御魂: %d' % sum(
        result['data']['attr_sgl'].values()
    )
    for kind in kinds_expand:
        if kind in result['data']['attr_sgl']:
            result['out'] += '\n    %s %d' % (
                YUHUN_ABBR.get(kind, kind), result['data']['attr_sgl'][kind]
            )
    if LITE:
        result['out'] = re.sub(r'\n {2}[^首领]+$', '', result['out'], flags=re.M)
    return result


def bench_speed(data):
    k, a1, a2 = '招财猫', '速度', '效果命中'
    data123456, data123456_zcm = [], []
    for i in range(6):
        data123456.append(sorted(
            [item for item in data if item['pos'] == i + 1],
            key=lambda item: (item['main2'].get(a1, 0)
                              + item['subs2'].get(a1, 0)),
            reverse=True
        ))
        data123456_zcm.append(sorted(
            [item for item in data
             if item['pos'] == i + 1 and item['kind'] == k],
            key=lambda item: (item['main2'].get(a1, 0)
                              + item['subs2'].get(a1, 0)),
            reverse=True
        ))
    result = {'data': [{
        'suit': [[], [], [], [], [], []],
        'value': 0
    }, {
        'suit': [],
        'value': 0
    }], 'out': ''}
    suit = [[None, None], [None, None], [None, None],
            [None, None], [None, None], [None, None]]  # 散一速套、招财一速套
    for i, data_pos in enumerate(data123456_zcm):
        if data_pos:
            suit[i][1] = data_pos[0]
    for i, data_pos in enumerate(data123456):
        if not data_pos:
            continue
        suit[i][0] = data_pos[0]
        result['data'][0]['suit'][i].append(data_pos[0])
        for item in data_pos[1:]:  # 追加满速
            if pick_dwarf.score_attrs(item, [a1]) != 6:
                break
            result['data'][0]['suit'][i].append(item)
    suit.sort(key=lambda x: ((x[0]['main2'].get(a1, 0)
                              + x[0]['subs2'].get(a1, 0) if x[0] else 0)
                             - (x[1]['main2'].get(a1, 0)
                                + x[1]['subs2'].get(a1, 0) if x[1] else 0)),
              reverse=True)
    suit[0][1], suit[1][1] = suit[0][0], suit[1][0]
    result['data'][0]['value'] = yhsuit.gross([items[0] for items in suit], a1)
    result['data'][1]['suit'] = [items[1] for items in suit]
    result['data'][1]['value'] = yhsuit.gross(result['data'][1]['suit'], a1)
    result['out'] = '散一速: +{:.2f} 招财 +{:.2f}'.format(
        result['data'][0]['value'], result['data'][1]['value']
    )
    for i, yuhuns_pos in enumerate(result['data'][0]['suit']):
        result['out'] += '\n  [%s]' % pick_dwarf.POS[i]
        for j, item in enumerate(yuhuns_pos):
            kind = ('{0}|{1}' if a2 in item['main2'] else '{0}').format(
                YUHUN_ABBR.get(item['kind'], item['kind']),
                ATTR_ABBR.get(a2, a2)
            )
            speed_main = item['main2'].get(a1, 0)
            speed_main = ('%.0f' % speed_main) if speed_main else ''
            score_speed = pick_dwarf.score_attrs(item, [a1])
            speed_sub = (('%.2f' if j == 0 else '%.1f') if score_speed == 6
                         else '%.0f') % item['subs2'].get(a1, 0)
            result['out'] += ' %s %s+%s' % (kind, speed_main, speed_sub)
    if LITE:
        result['out'] = re.sub(r'\n {2}[^贰]+$', '', result['out'], flags=re.M)
    return result


def bench_crit(data):
    k1, k2 = '暴击', '暴击伤害'
    attrs_useful = ['攻击加成', '速度', '暴击', '暴击伤害']
    data1_6 = [item for item in data if k1 in item['main2']]
    data2_6 = [item for item in data if k2 in item['main2']]
    result = {'data': {
        'crit_rate': [],
        'crit_power': []
    }, 'out': '高分暴击&暴伤御魂: '}
    lines1 = {}
    for item in data1_6:
        score = pick_dwarf.score_attrs(item, attrs_useful)
        if score < (7 if 'sgl' in item['attrs'] else 5):
            continue
        result['data']['crit_rate'].append(item)
        if item['kind'] in lines1:
            lines1[item['kind']] += ' %s %d' % (
                YUHUN_ABBR.get(item['kind'], item['kind']), score
            )
        else:
            lines1[item['kind']] = '\n    %s %d' % (
                YUHUN_ABBR.get(item['kind'], item['kind']), score
            )
    lines2 = []
    for item in data2_6:
        score = pick_dwarf.score_attrs(item, attrs_useful)
        if score < (7 if 'sgl' in item['attrs'] else 5):
            continue
        result['data']['crit_power'].append(item)
        lines2.append('\n    %s %d: %s' % (
            YUHUN_ABBR.get(item['kind'], item['kind']), score,
            (pick_dwarf.ATTRS_SUB[k1][2] % 0).format(
                ATTR_ABBR.get(k1, k1), item['subs2'].get(k1, 0)
            )
        ))
    result['out'] += '%d+%d' % (len(result['data']['crit_rate']),
                                len(result['data']['crit_power']))
    result['out'] += '\n  陆|%s 输出分:' % ATTR_ABBR.get(k1, k1)
    result['out'] += ''.join(sorted(lines1.values()))
    result['out'] += '\n  陆|%s 输出分&副属性暴击值:' % ATTR_ABBR.get(k2, k2)
    result['out'] += ''.join(sorted(lines2))
    if LITE:
        result['out'] = re.sub(r'\n {2}.+$', '', result['out'], flags=re.M)
    return result


def bench_zs_htz(data):
    panel_base = HEROES_PANEL['黑童子']  # 小小黑基础面板
    suits42 = ('针女', '鬼灵歌伎')
    attrs246 = [['攻击加成'],
                ['攻击加成'],
                ['暴击']]
    attrs_threshold = {
        '速度': 128, '暴击': 1
    }  # 属性限制
    damage_threshold = ((0, sys.maxsize),)  # 攻暴要求
    acc = (3, 1, 3, 1, 3, 1)  # 加速设置
    suit = yhsuit.cal(data, panel_base, suits42, attrs246,
                      attrs_threshold, damage_threshold, acc)
    return '  %s: 真蛇超星小小黑 针歌 %s' % (
        '这个没问题' if suit else '可能做不了', ''.join(map(str, acc))
    )


def bench_k28_cl(data):
    panel_base = HEROES_PANEL['炼狱茨木童子']  # 茨林基础面板
    suits42 = ('破势', '荒骷髅')
    suits42_alt = ('破势', '鬼灵歌伎')
    attrs246 = [['攻击加成'],
                ['攻击加成'],
                ['暴击']]
    attrs_threshold = {
        '速度': 128, '暴击': 1
    }  # 属性限制
    damage_threshold = ((15815, sys.maxsize),)  # 攻暴要求
    damage_threshold_alt = ((15723, sys.maxsize),)
    acc = (3, 1, 3, 1, 3, 1)  # 加速设置
    suit = yhsuit.cal(data, panel_base, suits42, attrs246,
                      attrs_threshold, damage_threshold, acc)
    if not suit:
        suit = yhsuit.cal(data, panel_base, suits42_alt, attrs246,
                          attrs_threshold, damage_threshold_alt, acc)
    return '  %s: 困28超星茨林 破荒/破歌 %s' % (
        '这个没问题' if suit else '可能做不了', ''.join(map(str, acc))
    )


def bench_j10_cl(data):
    panel_base = HEROES_PANEL['炼狱茨木童子']  # 茨林基础面板
    suits42 = ('破势', '荒骷髅')
    attrs246 = [['速度', '攻击加成'],
                ['攻击加成'],
                ['暴击', '暴击伤害']]
    attrs_threshold = {
        '速度': 160, '暴击': 1
    }  # 属性限制
    damage_threshold = ((15390, 15443), (15810, sys.maxsize))  # 攻暴要求
    acc = (5, 2, 5, 4, 5, 3)  # 加速设置
    suit = yhsuit.cal(data, panel_base, suits42, attrs246,
                      attrs_threshold, damage_threshold, acc)
    return '  %s: 觉10高速茨林 破荒 %s' % (
        '这个没问题' if suit else '可能做不了', ''.join(map(str, acc))
    )


def bench_h10_yzq(data):
    panel_base = HEROES_PANEL['玉藻前']  # 玉藻前基础面板
    suits42 = ('狂骨', '荒骷髅')
    suits42_alt = ('破势', '荒骷髅')
    attrs246 = [['速度'],
                ['攻击加成'],
                ['暴击', '暴击伤害']]
    attrs_threshold = {
        '速度': 162, '暴击': 1
    }  # 属性限制
    damage_threshold = ((15696, 20090),)  # 攻暴要求
    damage_threshold_alt = ((17843, 20090),)
    acc = (5, 3, 5, 4, 5, 3)  # 加速设置
    suit = yhsuit.cal(data, panel_base, suits42, attrs246,
                      attrs_threshold, damage_threshold, acc)
    if not suit:
        suit = yhsuit.cal(data, panel_base, suits42_alt, attrs246,
                          attrs_threshold, damage_threshold_alt, acc)
    return '  %s: 魂10高速玉藻前 狂荒/破荒 %s' % (
        '这个没问题' if suit else '可能做不了', ''.join(map(str, acc))
    )


def bench_k28_yzq(data):
    panel_base = HEROES_PANEL['玉藻前']  # 玉藻前基础面板
    suits42 = ('破势', '荒骷髅')
    attrs246 = [['攻击加成'],
                ['攻击加成'],
                ['暴击伤害']]
    attrs_threshold = {
        '速度': 128, '暴击': 1
    }  # 属性限制
    damage_threshold = ((21644, sys.maxsize),)  # 攻暴要求
    acc = (6, 5, 6, 5, 6, 4)  # 加速设置
    suit = yhsuit.cal(data, panel_base, suits42, attrs246,
                      attrs_threshold, damage_threshold, acc)
    return '  %s: 困28超星玉藻前 破荒 %s' % (
        '这个没问题' if suit else '可能做不了', ''.join(map(str, acc))
    )


def bench_suits(data_yuhun_std):
    result = {
        'data': [],
        'out': '部分御魂方案: %d' % 5
    }
    cio(result['out'])
    result_line = bench_zs_htz(data_yuhun_std)
    result['out'] += '\n%s' % result_line
    cio(result_line)
    result_line = bench_k28_cl(data_yuhun_std)
    result['out'] += '\n%s' % result_line
    cio(result_line)
    result_line = bench_j10_cl(data_yuhun_std)
    result['out'] += '\n%s' % result_line
    cio(result_line)
    result_line = bench_h10_yzq(data_yuhun_std)
    result['out'] += '\n%s' % result_line
    cio(result_line)
    result_line = bench_k28_yzq(data_yuhun_std)
    result['out'] += '\n%s' % result_line
    cio(result_line)
    return result


def bench():
    global DATA_RESULT
    if not DATA_SOURCE:
        return
    cio('正在分析数据...', 'info')
    data_game = json.loads(DATA_SOURCE['equip']['equip_desc'])
    data_yuhun_std = pick_dwarf.extract_data_cbg(DATA_SOURCE)
    if not data_yuhun_std:
        cio('数据分析失败', 'error')
        return
    if not optimize_data_for_cal(data_yuhun_std):
        cio('数据分析失败', 'error')
        return
    result_paragraph = bench_inventory(DATA_SOURCE, data_game)
    DATA_RESULT.append(result_paragraph)
    cio(result_paragraph['out'])
    result_paragraph = bench_heroes(data_game)
    DATA_RESULT.append(result_paragraph)
    cio(result_paragraph['out'])
    result_paragraph = bench_heroes_x(data_game)
    DATA_RESULT.append(result_paragraph)
    cio(result_paragraph['out'])
    result_paragraph = bench_skins(data_game)
    DATA_RESULT.append(result_paragraph)
    cio(result_paragraph['out'])
    result_paragraph = bench_yuhuns(data_game, data_yuhun_std)
    DATA_RESULT.append(result_paragraph)
    cio(result_paragraph['out'])
    result_paragraph = bench_speed(data_yuhun_std)
    DATA_RESULT.append(result_paragraph)
    cio(result_paragraph['out'])
    result_paragraph = bench_crit(data_yuhun_std)
    DATA_RESULT.append(result_paragraph)
    cio(result_paragraph['out'])
    # cio([result['out'] for result in DATA_RESULT])
    if not LITE:
        DATA_RESULT.append(bench_suits(data_yuhun_std))


def check_cbg_url(url):
    url = urllib.parse.unquote(url, encoding='utf-8')
    parsed = urllib.parse.urlparse(url)
    m = re.match(r'/cgi/mweb/equip/(\d+)/(.+)', parsed.path)
    return m is not None


def fetch_severs():
    global SERVER
    url_servers = 'https://cbg-yys.res.netease.com/js/server_list_data.js'
    url_servers += '?_=%.0f' % (time.time() * 1000)  # 非必需
    req = request.Request(url=url_servers, headers={
        'User-Agent': USER_AGENT
    })
    data = request.urlopen(req, timeout=5).read().decode('utf-8')
    r = re.search(r'({.+})', data)
    if not r:
        cio('区服列表获取失败, 将无法检测多服合一', 'error')
        return
    data = json.loads(r.group(1))
    data_servers = [server for area_server in data.values()
                    for server in area_server[1]]
    for server in data_servers:
        # [12, '网易-形影不离', '1', 'wangyixingyingbuli', 'wyxybl', [1, 2]]
        if server[0] in SERVER:
            SERVER[server[0]].add(server[1])
        else:
            SERVER[server[0]] = {server[1]}


def fetch_heroes():
    global HERO
    url_heroes = 'https://cbg-yys.res.netease.com/js/game_auto_config.js'
    req = request.Request(url=url_heroes, headers={
        'User-Agent': USER_AGENT
    })
    data = request.urlopen(req, timeout=5).read().decode('utf-8')
    r = re.search(r'({.+})', data)
    if not r:
        return
    data = json.loads(r.group(1))
    for hero in data['hero_list']:
        # [200, '桃花妖', 3, 'taohuayao']
        # 200：式神 ID
        # 3：稀有度(5 SP 4 SSR 3 SR 2 R 1 N + 呱 + 素材)
        if hero[2] in HERO:
            HERO[hero[2]][hero[0]] = hero[1]
        else:
            HERO[hero[2]] = {hero[0]: hero[1]}


def fetch_config():
    fetch_severs()
    fetch_heroes()


def fetch_data(url_player):
    global DATA_SOURCE
    url_player = urllib.parse.unquote(url_player, encoding='utf-8')
    parsed = urllib.parse.urlparse(url_player)
    # queries = urllib.parse.parse_qs(parsed.query)  # 参数可省略
    m = re.match(r'/cgi/mweb/equip/(\d+)/(.+)', parsed.path)
    if not m:
        cio('非法藏宝阁商品详情链接', 'error')
        return None
    cio('正在读取数据... timeout: 10s', 'info')
    url = 'https://yys.cbg.163.com/cgi/api/get_equip_detail'
    headers = {
        'User-Agent': USER_AGENT
    }
    params = {
        'serverid': m.group(1),
        'ordersn': m.group(2)
    }
    req = request.Request(
        url=url,
        data=urllib.parse.urlencode(params).encode('utf-8'),
        headers=headers,
        method='POST'
    )
    result = request.urlopen(req).read().decode('utf-8')
    DATA_SOURCE = json.loads(result)


def optimize_data_for_cal(data):
    if not data:
        return False
    for item in data:
        item['main2'] = {
            item['attrs']['main']['attr']: item['attrs']['main']['value']
        }
        item['subs2'] = {attr['attr']: attr['value']
                         for attr in item['attrs']['subs']}
        item['sgl2'] = {}
        if 'sgl' in item['attrs']:
            item['sgl2'] = {
                item['attrs']['sgl']['attr']: item['attrs']['sgl']['value']
            }
        attrs_dmg = [pick_dwarf.ATTRS[5], pick_dwarf.ATTRS[6],
                     pick_dwarf.ATTRS[7], pick_dwarf.ATTRS[8]]
        item['score_dmg'] = pick_dwarf.score_attrs(item, attrs_dmg)
    return True


def data_cbg2fluxxu(data, url):
    hero_attrs_id_name = {
        'attack': pick_dwarf.ATTRS[2],
        'max_hp': pick_dwarf.ATTRS[0],
        'defense': pick_dwarf.ATTRS[1],
        'speed': pick_dwarf.ATTRS[6],
        'crit_rate': pick_dwarf.ATTRS[7],
        'crit_power': pick_dwarf.ATTRS[8]
    }  # 「痒痒熊快照」式神属性ID-名字表
    hero_attrs_id_name_no_base = {
        'effect_hit_rate': pick_dwarf.ATTRS[9],
        'effect_resist_rate': pick_dwarf.ATTRS[10]
    }  # 「痒痒熊快照」式神属性ID-名字表(基础值为0)
    yuhun_attrs_name_id = {
        pick_dwarf.ATTRS[0]: 'Hp',
        pick_dwarf.ATTRS[1]: 'Defense',
        pick_dwarf.ATTRS[2]: 'Attack',
        pick_dwarf.ATTRS[3]: 'HpRate',
        pick_dwarf.ATTRS[4]: 'DefenseRate',
        pick_dwarf.ATTRS[5]: 'AttackRate',
        pick_dwarf.ATTRS[6]: 'Speed',
        pick_dwarf.ATTRS[7]: 'CritRate',
        pick_dwarf.ATTRS[8]: 'CritPower',
        pick_dwarf.ATTRS[9]: 'EffectHitRate',
        pick_dwarf.ATTRS[10]: 'EffectResistRate'
    }  # 「痒痒熊快照」御魂属性名字 - ID 表
    data_core = data['equip']
    data_game = json.loads(data_core['equip_desc'])
    data_hero = list(data_game['heroes'].values())
    data_yuhun = list(data_game['inventory'].values())
    data_hero_2 = []
    for item in data_hero:
        attrs_2 = {}
        for attr_2, attr in hero_attrs_id_name.items():
            base = panel_str2val(item['attrs'][attr]['val'])
            add_value = panel_str2val(item['attrs'][attr].get('add_val', '0'))
            attrs_2[attr_2] = {
                'base': base,
                'add_value': add_value,
                'add_rate': 0,
                'value': base + add_value
            }
        for attr_2, attr in hero_attrs_id_name_no_base.items():
            attrs_2[attr_2] = panel_str2val(item['attrs'][attr]['val'])
        data_hero_2.append({
            'id': item['heroUid'],  # 式神ID, 同 item['uid']
            'hero_id': item['heroId'],  # 式神编号
            'equips': item['equips'],  # 装备的御魂套装
            'level': item['level'],  # 等级
            'star': item['star'],  # 星级
            'awake': item['awake'],  # 觉醒状态
            'exp': item['exp'],  # TODO
            'nick_name': item.get('nick', ''),  # 式神昵称
            'born': item.get('born', 0),  # 获取时间戳
            'lock': item.get('lock', False),  # 锁定状态
            'rarity': HERO_RARITY[item['rarity']],  # 稀有度
            'skills': [{
                'id': info[0], 'level': info[1]
            } for info in item['skinfo']],  # 技能等级
            'attrs': attrs_2  # 面板
        })
    data_yuhun_2 = []
    for i, item in enumerate(data_yuhun):
        item_std = pick_dwarf.meta_cbg2std(item)
        attrs_sub = [{
            'type': yuhun_attrs_name_id[attr['attr']],
            'value': attr['value']
        } for attr in item_std['attrs']['subs']]
        data_yuhun_2.append({
            'id': item['uuid'],  # 御魂 ID
            'suit_id': item['suitid'],  # 御魂类型编号
            'pos': item['pos'] - 1,  # 位置
            'quality': item['qua'],  # 星级
            'level': item['level'],  # 等级
            'equip_id': item['itemId'],  # TODO
            'born': 0,  # 获取时间戳(未记录)
            'lock': item['lock'],  # 锁定状态
            'garbage': item['isuseless'],  # 弃置状态
            'base_attr': {
                'type': yuhun_attrs_name_id[item_std['attrs']['main']['attr']],
                'value': item_std['attrs']['main']['value']
            },  # 主属性
            'attrs': attrs_sub,  # 副属性
            'single_attrs': [{
                'type': yuhun_attrs_name_id[item_std['attrs']['sgl']['attr']],
                'value': item_std['attrs']['sgl']['value']
            }] if 'sgl' in item_std['attrs'] else [],  # 固有属性
            'random_attrs': attrs_sub,  # 与 attrs 记录重复, 用意不明
            'random_attr_rates': []  # 似乎是想记录副属性成长系数, 但实际未记录
        })
    data_core_2 = {
        'player': {
            'id': 0,  # TODO: 非 data_core['equipid']
            'server_id': 0,  # TODO: 非 data_core['serverid']
            'name': data_core['equip_name'],  # 当前卖家角色昵称
            'level': data_core['equip_level']  # 等级
        },
        'currency': {
            'coin': data_game['money'],  # 金币
            'jade': data_game['goyu'],  # 勾玉
            'action_point': data_game['strength'],  # 体力
            'auto_point': data_game['currency_900273'],  # 樱饼
            'honor': data_game['honor_score'],  # 荣誉
            'medal': data_game['medal'],  # 勋章
            'contrib': 0,  # TODO: 功勋
            'totem_pass': data_game['currency_900215'],  # 御灵镜之玥
            's_jade': data_game['hunyu'],  # 魂玉
            'skin_token': data_game['skin_coupon'],  # 皮肤券
            'realm_raid_pass': 0,  # TODO: 结界突破券
            'broken_amulet': 0,  # 破碎的符咒
            'mystery_amulet': data_game['gameble_card'],  # 神秘的符咒
            'ar_amulet': data_game['ar_gamble_card'],  # 现世符咒
            'ofuda': data_game['soul_jade'],  # 御札
            'gold_ofuda': data_game['currency_900188'],  # 金御札
            'scale': data_game['currency_900216'],  # 八岐大蛇鳞片
            'reverse_scale': data_game['currency_900217'],  # 大蛇的逆鳞
            'demon_soul': data_game['currency_900218'],  # 逢魔之魂
            'foolery_pass': data_game['currency_900041'],  # 痴念之卷
            'sp_skin_token': data_game['currency_906058'],  # SP 皮肤券
        },
        'heroes': data_hero_2,  # 式神
        'hero_equips': data_yuhun_2,  # 御魂
        'hero_equip_presets': [],  # 御魂方案(未记录)
        'hero_book_shards': [{
            'hero_id': int(hero_id),
            'shards': info['num'],
            'books': 0,  # (未记录)
            'book_max_shards': 0  # 合成量(未记录)
        } for hero_id, info in data_game['hero_fragment'].items()],  # 式神碎片
        'realm_cards': [],  # TODO (未记录)
        'story_tasks': []  # TODO (未记录)
    }
    return {
        'version': '0.99.7-cbg',
        'timestamp': datetime.datetime.strptime(
            data['equip']['create_time'], '%Y-%m-%d %H:%M:%S'
        ).strftime('%Y-%m-%dT%H:%M:%S+08:00'),
        'cbg_url': url,
        'data': data_core_2
    }


# 依赖 pywin32 库, 放弃
# if platform.system() == 'Windows':
#     import win32clipboard
#     import win32con
# def clipboard():
#     if platform.system() != 'Windows':
#         return None
#     win32clipboard.OpenClipboard()
#     try:
#         content = win32clipboard.GetClipboardData(win32con.CF_UNICODETEXT)
#         if content and check_cbg_url(content.strip()):
#             return content.strip()
#     finally:
#         win32clipboard.CloseClipboard()
#     return None


def cio(content, tag=None, input_or_print=False):
    lock.acquire()
    try:
        if input_or_print:
            if type(content) in (tuple, list, set):
                result = []
                for piece in content:
                    result.append(input(
                        pick_dwarf.log(piece, tag) if tag else piece
                    ))
                return result
            else:
                return input(pick_dwarf.log(content, tag) if tag else content)
        else:
            if type(content) in (tuple, list, set):
                for piece in content:
                    out = pick_dwarf.log(piece, tag) if tag else piece
                    print(out)
                    if callback_cio:
                        callback_cio(out)
            else:
                out = pick_dwarf.log(content, tag) if tag else content
                print(out)
                if callback_cio:
                    callback_cio(out)
    finally:
        lock.release()


def view(file):
    if pick_dwarf.run_as_exe() and path.exists(file):
        # subprocess.run(['start', file])
        subprocess.run(['explorer', file])


def check_modules():
    try:
        import PIL
    except ModuleNotFoundError:
        cio('\'PIL\'库缺失, 图片生成功能已禁用 \'pip install pillow\'', 'warn')


def parse_args(args):
    global LITE
    LITE = False
    try:
        opts, args = getopt.getopt(
            args, 'hvlu:', ['help', 'version', 'lite', 'url=']
        )
    except getopt.GetoptError:
        opts, args = [('--undefined', '')], []
    url_player, helped = None, False
    for opt, value in opts:
        if opt in ('-h', '--help'):
            cio(COPYRIGHT)
            cio('\n'.join(HELP))
            if output.enabled():
                file_save = '%s_help.png' % path.splitext(
                    path.abspath(sys.argv[0])
                )[0]
                output.text2img(file_save, HELP,
                                head=path.basename(file_save), foot=COPYRIGHT)
                view(file_save)
            helped = True
        elif opt in ('-v', '--version'):
            cio(VERSION)
            helped = True
        elif opt in ('-l', '--lite'):
            LITE = True
        elif opt in ('-u', '--url'):
            url_player = value
    if not url_player and args:
        url_player = args[0]
    if not helped and not url_player:
        cio(COPYRIGHT)
        cio(HELP)
    return url_player


def main(callback=None):
    global thread_fetch_config
    global LITE
    global callback_cio
    callback_cio = callback
    thread_fetch_config = Thread(target=fetch_config)
    thread_fetch_config.start()
    if len(sys.argv) > 1:
        url_equip = parse_args(sys.argv[1:])
        if not url_equip:
            return
        cio(COPYRIGHT)
        check_modules()
    else:
        cio(COPYRIGHT)
        check_modules()
        url_equip = cio('藏宝阁链接: ', 'input', True)
        LITE = True if cio(
            '输出完整/精简结果? (直接回车即指定前者) ', 'input', True
        ) else False
    fetch_data(url_equip)
    bench()
    save(url_equip)


if __name__ == '__main__':
    # 由于使用 PyInstaller 打包 EXE 后运行机制发生变化，多进程代码会异常，
    # 添加该行代码使 multiprocessing 模块能正常工作。
    # https://github.com/pyinstaller/pyinstaller/wiki/Recipe-Multiprocessing
    multiprocessing.freeze_support()
    try:
        main()
    except Exception:
        raise
    finally:
        if pick_dwarf.run_as_exe():  # 避免窗口一闪而逝
            os.system('pause')
