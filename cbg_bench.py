#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# 号来
# 提取藏宝阁上阴阳师游戏帐号数据的要点并生成报告。
#
# TODO: 仍在开发中，未正式发布
#
# 了解更多请前往 GitHub 查看项目：https://github.com/nguaduot/yys-cbg-bench
#
# author: @nguaduot 痒痒鼠@南瓜多糖
# version: 1.0.200728
# date: 20200728


import datetime
import getopt
import json
import multiprocessing
from multiprocessing import Process
import os
from os import path
import re
import sys
import threading
from threading import Thread
import time
import urllib.parse
from urllib import request

from modules import pick_dwarf
from modules import yh_suit


PROG = 'yys-cbg-bench'
AUTH = 'nguaduot'
VER = '1.0'
VERSION = '1.0.200728'
REL = 'github.com/nguaduot/yys-cbg-bench'
COPYRIGHT = '%s v%s @%s %s' % (PROG, VERSION, AUTH, REL)
HELP = (
    '+ 选项：'
    '\n  -h, --help     帮助'
    '\n  -v, --version  程序版本'
    '\n  -u, --url      藏宝阁商品详情链接'
    '\n+ 若未指定 -u, 程序会读取未知参数, 若也无未知参数, 不启动程序'
    '\n+ 不带任何参数也可启动程序, 会有参数输入引导'
    '\n输出解释:'
    '\n签到: {天数} ¥{售价} {若检测到合服则显示提示, 多服合一无法获知归属服, 需留心}'
    '\n  金币 {金币} '
    '黑蛋 {\'御行达摩\'数量+推测已消耗量(据此可了解练度)} '
    '体力 {体力} '
    '勾玉 {勾玉} '
    '蓝票 {神秘的符咒+现世符咒} '
    '御札 {御札/金御札}'
    '\n  庭院: 初语谧景 + {除初始之外的其他庭院}'
    '\n  风姿百物: {风姿度, 据此可了解外观向收集量(皮肤/头像框等)}'
    '\n图鉴SP/SSR式神: {\'500天未收录SSR\'未使用则显示} {\'999天未收录SP\'未使用则显示}'
    '\n  未拥有式神 & 保有碎片:'
    '\n    SP({SP阶式神总数-未拥有数}): '
    '{未拥有式神(图鉴已点亮也可能未拥有, 需留心)} {该式神碎片量, 据此可知有无碗} ...'
    '\n    ...'
    '\n  部分多号机: {式神} {该式神拥有数量} ...'
    '\n联动式神拥有情况:'
    '\n  {联动期数}: {该期式神} '
    '{拥有数量(低稀有度低星式神无法获知)}/{碎片量(低稀有度式神无法获知)} ...'
    '\n  ...'
    '\n六星满级/满级御魂: {六星满级御魂数量}/{各星级满级御魂总量}'
    '\n  满级普通御魂: {满级非首领御魂数量}'
    '\n    {两件套属性} {该类御魂数量}'
    '\n    ...'
    '\n  满级首领御魂: {满级首领御魂数量}'
    '\n    荒骷髅 {\'荒骷髅\'数量}'
    '\n    歌伎 {\'鬼灵歌伎\'数量}'
    '\n散一速: {散件套一速} 招财 {招财套一速}'
    '\n  [{位置}] {该位置散一速套御魂, 以及其余速度满收益御魂} {副属性\'速度\'值} ...'
    '\n  ...'
    '\n暴击(输出分: 非首领 5+ 首领 7+):'
    '\n  {六号位主属性\'暴击\'的高分御魂} '
    '{该御魂分数, 按有效属性\'攻击加成\'/\'速度\'/\'暴击\'/\'暴击伤害\'评分} ...'
    '\n  ...'
    '\n暴击伤害(输出分: 非首领 5+ 首领 7+):'
    '\n  {六号位主属性\'暴击伤害\'的高分御魂} '
    '{该御魂分数, 按有效属性\'攻击加成\'/\'速度\'/\'暴击\'/\'暴击伤害\'评分}: '
    '暴击 {副属性\'暴击\'值}'
    '\n  ...'
    '\n部分御魂方案:'
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


HERO_RARITY = ['', 'N', 'R', 'SR', 'SSR', 'SP']  # 式神稀有度
HEROES_X = {
    '第一期': {'奴良陆生': 4},
    '第二期': {'卖药郎': 4},
    '第三期': {'鬼灯': 4, '阿香': 3, '蜜桃&芥子': 2},
    '第四期': {'犬夜叉': 4, '杀生丸': 4, '桔梗': 4},
    '第五期': {'黑崎一护': 4, '朽木露琪亚': 3}
}  # 各期联动式神及其稀有度
HEROES_ABBR = {
    '少羽大天狗': '小天狗',
    '炼狱茨木童子': '茨林',
    '稻荷神御馔津': '神御',
    '苍风一目连': '苍连',
    '赤影妖刀姬': '赤刀',
    '御怨般若': '御怨般若',
    '骁浪荒川之主': '浪川',
    '烬天玉藻前': '烬',
    '鬼王酒吞童子': '鬼吞',
    '天剑韧心鬼切': '奶切',
    '聆海金鱼姬': '大金鱼',
    '浮世青行灯': '浮世青灯',
    '缚骨清姬': '缚骨清姬',
    '酒吞童子': '酒吞',
    '荒川之主': '荒川',
    '茨木童子': '茨木',
    '八岐大蛇': '大蛇',
    '奴良陆生': '陆生',
    '蜜桃&芥子': '蜜桃',
    '黑崎一护': '一护',
    '朽木露琪亚': '露琪亚',
}  # 尽量不超过四个字，使用 HEROES_ABBR.get(x, x) 取值而非 HEROES_ABBR[x]
YUHUN_ABBR = {
    '涅槃之火': '涅槃',
    '地藏像': '地藏',
    '日女巳时': '日女',
    '招财猫': '招财',
    '魍魉之匣': '魍魉',
    '鬼灵歌伎': '歌伎'
}  # 使用 YUHUN_ABBR.get(x, x) 取值而非 YUHUN_ABBR[x]
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

USER_AGENT = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
              ' AppleWebKit/537.36 (KHTML, like Gecko)'
              ' Chrome/84.0.4147.89 Safari/537.36')

SERVER = {}  # 区服，用以检测多服合一
DATA_SOURCE = {}  # 商品源数据
DATA_RESULT = []  # 分析结果

lock = threading.Lock()
thread_fetch_config: Thread = None
thread_fetch_data: Thread = None
thread_bench: Thread = None
thread_save: Thread = None


def save(url_equip):
    dir_cbg = path.join(path.dirname(path.abspath(sys.argv[0])), 'cbg')
    if not path.isdir(dir_cbg):
        os.mkdir(dir_cbg)
    thread_fetch_data.join()  # 等待商品数据抓取完毕
    if not DATA_SOURCE:
        return
    seller = re.sub(
        r'[\\/:?"<>|\u0000-\u001F\u007F-\u009F]', '',
        DATA_SOURCE['equip']['seller_name']
    )  # 删除 Windows 文件名中不允许出现的字符，以及无法正常显示且会导致 IO 异常的控制字符
    t = datetime.datetime.strptime(DATA_SOURCE['equip']['create_time'],
                                   '%Y-%m-%d %H:%M:%S')  # 2020-07-20 01:20:57
    file_base = path.join(dir_cbg, 'cbg_%s_%s_%s_%s' % (
        DATA_SOURCE['equip']['area_name'], DATA_SOURCE['equip']['server_name'],
        seller, t.strftime('%Y%m%d%H%M%S')
    ))
    file_source = '%s.json' % file_base
    # file_fluxxu = path.join(dir_cbg, ('yyx_snapshot_cbg_%s.json'
    #                                   % data_source['equip']['seller_name']))
    file_fluxxu = '%s_yyx_snapshot.json' % file_base
    file_result = '%s_bench.json' % file_base
    if path.isfile(file_source):
        cio('源数据已存在 \'%s\'' % path.basename(file_source), 'info')
    else:
        with open(file_source, 'w', encoding='utf-8') as f:
            json.dump(DATA_SOURCE, f)
        cio('已保存源数据 \'%s\'' % path.basename(file_source), 'info')
    if path.isfile(file_fluxxu):
        cio('痒痒熊快照格式数据已存在 \'%s\'' % '*_yyx_snapshot.json', 'info')
    else:
        data_fluxxu = data_cbg2fluxxu(DATA_SOURCE, url_equip)
        with open(file_fluxxu, 'w', encoding='utf-8') as f:
            json.dump(data_fluxxu, f)
        cio('已保存痒痒熊快照格式数据 \'%s\'' % '*_yyx_snapshot.json', 'info')
    thread_bench.join()  # 等待数据分析完毕
    if not DATA_RESULT:
        return
    with open(file_result, 'w', encoding='utf-8') as f:
        json.dump(DATA_RESULT, f)
    cio('已保存分析结果 \'%s\'' % '*_bench.json', 'info')


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
    }  # 阴阳师及其御灵稀有度均被设定为 SSR，即 item['rarity'] == 4
    data_heroes = list(data['heroes'].values())
    data_sp_ssr = [item for item in data_heroes if (
            item['rarity'] == 5 or item['rarity'] == 4
    ) and item['heroId'] not in heroes_onmyoji]
    return sum(
        [max(info[1] - 1, 0) for hero in data_sp_ssr for info in hero['skinfo']]
    )


def bench_inventory(data, data_game):
    honors_fzbw = {
        950121: {
            'name': '风姿·春时雨',
            'value': 1000
        },
        950122: {
            'name': '风姿·花信风',
            'value': 3000
        },
        950123: {
            'name': '风姿·星月夜',
            'value': 5000
        },
        950124: {
            'name': '风姿·銮华扇',
            'value': 8000
        },
        950125: {
            'name': '风姿·神霖羽',
            'value': 12000
        }
    }
    data_damo = data_game['damo_count_dict']
    data_yard = data_game['skin']['yard']  # 不会包含默认庭院皮肤
    data_honors = data_game['honors']  # 徽章
    result = {
        'data': {
            'days': data_game['sign_days'],
            'price': data['equip']['price'],
            'money':  data_game['money'],
            'gouyu':  data_game['goyu'],
            'smdfz': data_game['gameble_card'],  # 源数据拼写错误
            'xsfz': data_game['ar_gamble_card'],
            # 'hunyu': data_game['hunyu'],
            'strength':  data_game['strength'],
            'yuzha':  data_game['soul_jade'],
            'yuzha_gold': data_game['currency_900188'],
            'damo_yx': sum(
                [num for damoes in data_damo.values()
                 for damo, num in damoes.items() if damo == '411']
            ),
            'damo_yx_cost': infer_damo_yx_cost(data_game),
            'servers': [],
            'yards': [item[1] for item in data_yard],
            'fzbw': {}
        },
        'out': '签到: %d ¥%.0f' % (
            data_game['sign_days'], data['equip']['price'] / 100
        )
    }
    for honor_id in list(honors_fzbw)[::-1]:
        if honor_id in data_honors:
            result['data']['fzbw'] = honors_fzbw[honor_id]
            break
    thread_fetch_config.join()  # 等待区服列表抓取完毕
    if data['equip']['serverid'] in SERVER:
        servers = SERVER[data['equip']['serverid']]
        result['data']['servers'] = list(servers)
        if len(servers) > 1:
            result['out'] += ' !合服(%s)' % '/'.join(servers)
    result['out'] += '\n  金币 %.0fw 黑蛋 %d+%d 体力 %.1fw 勾玉 %d 蓝票 %d+%d 御札 %d/%d' % (
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
    result['out'] += '\n  庭院: 初语谧景 + %s' % ' '.join(result['data']['yards'])
    result['out'] += '\n  风姿百物: %s' % ('%s(%d+)' % (
        result['data']['fzbw']['name'], result['data']['fzbw']['value']
    ) if result['data']['fzbw'] else '<1000')
    return result


def bench_heroes(data):
    heroes_sp = set([info[0] for info in data['hero_history']['sp'].values()
                     if type(info) is list])
    heroes_ssr = set([info[0] for info in data['hero_history']['ssr'].values()
                     if type(info) is list])
    data_heroes = list(data['heroes'].values())
    data_sp_ssr = [item for item in data_heroes
                   if item['rarity'] == 5 or item['rarity'] == 4]
    data_fragments_sp_ssr = list(data['hero_fragment'].values())
    data_fragments_sp_ssr = {
        item['name']: item['num'] for item in data_fragments_sp_ssr
    }
    heroes_sp_lost = heroes_sp - {
        item['name'] for item in data_sp_ssr if item['rarity'] == 5
    }
    heroes_ssr_lost = heroes_ssr - {
        item['name'] for item in data_sp_ssr if item['rarity'] == 4
    }
    result = {'data': {
        'sp': {hero: 0 for hero in heroes_sp_lost},
        'ssr': {hero: 0 for hero in heroes_ssr_lost},
        'mult': {
            '烬天玉藻前': 0, '鬼王酒吞童子': 0,
            '酒吞童子': 0, '玉藻前': 0, '八岐大蛇': 0, '不知火': 0, '云外镜': 0,
        },
        'ssr_coin': data['ssr_coin'] == 1,  # 「500 天未收录 SSR」是否还未使用
        'sp_coin': data['sp_coin'] == 1  # 「999 天未收录 SP」是否还未使用
    }, 'out': '图鉴SP/SSR式神:'}
    for hero in result['data']['sp']:
        result['data']['sp'][hero] = data_fragments_sp_ssr.get(hero, 0)
    for hero in result['data']['ssr']:
        result['data']['ssr'][hero] = data_fragments_sp_ssr.get(hero, 0)
    for hero in result['data']['mult']:
        result['data']['mult'][hero] = len(
            [item for item in data_sp_ssr if item['name'] == hero]
        )
    if result['data']['ssr_coin']:
        result['out'] += ' 500SSR'
    if result['data']['sp_coin']:
        result['out'] += ' 999SP'
    result['out'] += '\n  未拥有式神 & 保有碎片:'
    result['out'] += '\n    SP(%d-%d):' % (len(heroes_sp), len(heroes_sp_lost))
    for hero, num in result['data']['sp'].items():
        result['out'] += ' %s %d' % (HEROES_ABBR.get(hero, hero), num)
    result['out'] += '\n    SSR(%d-%d):' % (len(heroes_ssr),
                                            len(heroes_ssr_lost))
    for hero, num in result['data']['ssr'].items():
        result['out'] += ' %s %d' % (HEROES_ABBR.get(hero, hero), num)
    result['out'] += '\n  部分多号机:'
    for hero, num in result['data']['mult'].items():
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
    }  # 仅包含了 SSR、SP 阶，且碎片量至少一片
    result = {'data': {
        'heroes': heroes_x,
        'fragments': {hero: fragments_sp_ssr.get(hero, 0)
                      for heroes in HEROES_X.values() for hero in heroes}
    }, 'out': '联动式神拥有情况:'}
    for i, heroes in HEROES_X.items():
        result['out'] += '\n  %s:' % i
        for hero, rarity in heroes.items():
            if heroes_x[hero]:  # 已拥有至少一只
                num_hero = str(heroes_x[hero])
            elif hero in x_never_owm:  # 未拥有
                num_hero = '0'
            else:  # 无法确定（SR、R 阶会出现这种情况：可能有五星以下的，可能全被消耗了）
                num_hero = '?'
            if rarity == 5 or rarity == 4:  # SP、SSR
                num_fragment = str(fragments_sp_ssr.get(hero, 0))
            else:  # 其他稀有度碎片信息未记录
                num_fragment = '-'
            result['out'] += ' %s %s/%s' % (HEROES_ABBR.get(hero, hero),
                                            num_hero, num_fragment)
    return result


def bench_yuhuns(data):
    kinds_expand = {'狂骨', '破势', '招财猫', '蚌精', '鬼灵歌伎', '荒骷髅'}
    data_15 = [item for item in data if item['level'] == 15]
    data_15_6 = [item for item in data_15 if item['star'] == 6]
    result = {
        'data': {
            'level_15': len(data_15),
            'level_15_star_6': len(data_15_6),
            'attr_dbl': {},
            'attr_sgl': {}
        },
        'out': '六星满级/满级御魂: %d/%d' % (len(data_15_6), len(data_15))
    }
    for attr_dbl, preset in pick_dwarf.ATTRS_DBL.items():
        result['data']['attr_dbl'][attr_dbl] = {}
        for kind in preset[1]:
            result['data']['attr_dbl'][attr_dbl][kind] = len(
                [item for item in data_15 if item['kind'] == kind]
            )
    for kind in pick_dwarf.KINDS[37:43]:
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
    return result


def bench_speed(data):
    k, a = '招财猫', '速度'
    data123456, data123456_zcm = [], []
    for i in range(6):
        data123456.append(sorted(
            [item for item in data if item['pos'] == i + 1],
            key=lambda item: item['main2'].get(a, 0) + item['subs2'].get(a, 0),
            reverse=True
        ))
        data123456_zcm.append(sorted(
            [item for item in data
             if item['pos'] == i + 1 and item['kind'] == k],
            key=lambda item: item['main2'].get(a, 0) + item['subs2'].get(a, 0),
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
            if pick_dwarf.score_attrs(item, [a]) != 6:
                break
            result['data'][0]['suit'][i].append(item)
    suit.sort(key=lambda x: ((x[0]['main2'].get(a, 0)
                              + x[0]['subs2'].get(a, 0) if x[0] else 0)
                             - (x[1]['main2'].get(a, 0)
                                + x[1]['subs2'].get(a, 0) if x[1] else 0)),
              reverse=True)
    suit[0][1], suit[1][1] = suit[0][0], suit[1][0]
    result['data'][0]['value'] = yh_suit.gross([items[0] for items in suit], a)
    result['data'][1]['suit'] = [items[1] for items in suit]
    result['data'][1]['value'] = yh_suit.gross(result['data'][1]['suit'], a)
    result['out'] = '散一速: +{:.2f} 招财 +{:.2f}'.format(
        result['data'][0]['value'], result['data'][1]['value']
    )
    for i, yuhuns_pos in enumerate(result['data'][0]['suit']):
        result['out'] += '\n  [%s]' % pick_dwarf.POS[i]
        for j, item in enumerate(yuhuns_pos):
            speed_main = item['main2'].get(a, 0)
            speed_main = ('%.0f' % speed_main) if speed_main else ''
            score_speed = pick_dwarf.score_attrs(item, [a])
            speed_sub = (('%.2f' if j == 0 else '%.1f') if score_speed == 6
                         else '%.0f') % item['subs2'].get(a, 0)
            result['out'] += ' %s %s+%s' % (
                YUHUN_ABBR.get(item['kind'], item['kind']),
                speed_main, speed_sub
            )
    return result


def bench_crit_rate(data):
    k = '暴击'
    attrs_useful = [pick_dwarf.ATTRS[5], pick_dwarf.ATTRS[6],
                    pick_dwarf.ATTRS[7], pick_dwarf.ATTRS[6]]
    data_6 = [item for item in data if k in item['main2']]
    result = {'data': [], 'out': '暴击(输出分: 非首领 5+ 首领 7+):'}
    lines = {}
    for item in data_6:
        score = pick_dwarf.score_attrs(item, attrs_useful)
        if score < (7 if 'sgl' in item['attrs'] else 5):
            continue
        result['data'].append(item)
        if item['kind'] in lines:
            lines[item['kind']] += ' %s %d' % (
                YUHUN_ABBR.get(item['kind'], item['kind']), score
            )
        else:
            lines[item['kind']] = '\n  %s %d' % (
                YUHUN_ABBR.get(item['kind'], item['kind']), score
            )
    result['out'] += ''.join(sorted(lines.values()))
    return result


def bench_crit_power(data):
    k1, k2 = '暴击伤害', '暴击'
    attrs_useful = [pick_dwarf.ATTRS[5], pick_dwarf.ATTRS[6],
                    pick_dwarf.ATTRS[7], pick_dwarf.ATTRS[6]]
    data_6 = [item for item in data if k1 in item['main2']]
    result = {'data': [], 'out': '暴击伤害(输出分: 非首领 5+ 首领 7+):'}
    lines = []
    for item in data_6:
        score = pick_dwarf.score_attrs(item, attrs_useful)
        if score < (7 if 'sgl' in item['attrs'] else 5):
            continue
        result['data'].append(item)
        lines.append('\n  %s %d: %s' % (
            YUHUN_ABBR.get(item['kind'], item['kind']), score,
            (pick_dwarf.ATTRS_SUB[k2][2] % 0).format(k2, item['subs2'].get(k2, 0))
        ))
    result['out'] += ''.join(sorted(lines))
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
    suit = yh_suit.cal(data, panel_base, suits42, attrs246,
                       attrs_threshold, damage_threshold, acc)
    cio('  %s: 真蛇超星小小黑 针歌 %s' % (
        '这个没问题' if suit else '可能做不了', ''.join(map(str, acc))
    ))


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
    suit = yh_suit.cal(data, panel_base, suits42, attrs246,
                       attrs_threshold, damage_threshold, acc)
    if not suit:
        suit = yh_suit.cal(data, panel_base, suits42_alt, attrs246,
                           attrs_threshold, damage_threshold_alt, acc)
    cio('  %s: 困28超星茨林 破荒/破歌 %s' % (
        '这个没问题' if suit else '可能做不了', ''.join(map(str, acc))
    ))


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
    suit = yh_suit.cal(data, panel_base, suits42, attrs246,
                       attrs_threshold, damage_threshold, acc)
    cio('  %s: 觉10高速茨林 破荒 %s' % (
        '这个没问题' if suit else '可能做不了', ''.join(map(str, acc))
    ))


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
    suit = yh_suit.cal(data, panel_base, suits42, attrs246,
                       attrs_threshold, damage_threshold, acc)
    if not suit:
        suit = yh_suit.cal(data, panel_base, suits42_alt, attrs246,
                           attrs_threshold, damage_threshold_alt, acc)
    cio('  %s: 魂10高速玉藻前 狂荒/破荒 %s' % (
        '这个没问题' if suit else '可能做不了', ''.join(map(str, acc))
    ))


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
    suit = yh_suit.cal(data, panel_base, suits42, attrs246,
                       attrs_threshold, damage_threshold, acc)
    cio('  %s: 困28超星玉藻前 破荒 %s' % (
        '这个没问题' if suit else '可能做不了', ''.join(map(str, acc))
    ))


def bench_suits():
    thread_fetch_data.join()  # 等待商品数据抓取完毕
    if not DATA_SOURCE:
        return
    data_yuhun_std = pick_dwarf.extract_data_cbg(DATA_SOURCE)
    if not data_yuhun_std:
        cio('无法考核御魂池', 'error')
        return
    if not optimize_data_for_cal(data_yuhun_std):
        cio('无法考核御魂池', 'error')
        return
    cio('正在考核御魂池... (额外分析, CPU核心全开, 等待过久可手动结束)', 'info')
    cio('部分御魂方案: %d' % 5)
    Process(target=bench_zs_htz, args=(data_yuhun_std,)).start()
    Process(target=bench_k28_cl, args=(data_yuhun_std,)).start()
    Process(target=bench_j10_cl, args=(data_yuhun_std,)).start()
    Process(target=bench_h10_yzq, args=(data_yuhun_std,)).start()
    Process(target=bench_k28_yzq, args=(data_yuhun_std,)).start()
    # bench_k28_yzq(data_yuhun_std)


def bench():
    global DATA_RESULT
    thread_fetch_data.join()  # 等待商品数据抓取完毕
    if not DATA_SOURCE:
        return
    cio('正在分析数据...', 'info')
    data_game = json.loads(DATA_SOURCE['equip']['equip_desc'])
    data_yuhun_std = pick_dwarf.extract_data_cbg(DATA_SOURCE)
    # with open('', 'r', encoding='utf-8') as f:
    #     data = json.loads(f.read())
    # data_yuhun_std = pick_dwarf.extract_data_cbg(data)
    if not data_yuhun_std:
        cio('数据分析失败', 'error')
        return
    if not optimize_data_for_cal(data_yuhun_std):
        cio('数据分析失败', 'error')
        return
    DATA_RESULT.append(bench_inventory(DATA_SOURCE, data_game))
    DATA_RESULT.append(bench_heroes(data_game))
    DATA_RESULT.append(bench_heroes_x(data_game))
    DATA_RESULT.append(bench_yuhuns(data_yuhun_std))
    DATA_RESULT.append(bench_speed(data_yuhun_std))
    DATA_RESULT.append(bench_crit_rate(data_yuhun_std))
    DATA_RESULT.append(bench_crit_power(data_yuhun_std))
    cio([result['out'] for result in DATA_RESULT])


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
        cio('区服列表获取失败，将无法检测多服合一', 'error')
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


# def fetch_heroes():
#     url_heroes = 'https://cbg-yys.res.netease.com/js/game_auto_config.js'
#     req = request.Request(url=url_heroes, headers={
#         'User-Agent': USER_AGENT
#     })
#     data = request.urlopen(req, timeout=5).read().decode('utf-8')
#     r = re.search(r'({.+})', data)
#     if not r:
#         return
#     data = json.loads(r.group(1))
#     for hero in data['hero_list']:
#         # [200, '桃花妖', 3, 'taohuayao']
#         # 200：式神 ID
#         # 3：稀有度（5 SP 4 SSR 3 SR 2 R 1 N + 呱 + 素材）
#         if hero[2] in HEROES:
#             HEROES[hero[2]][hero[0]] = hero[1]
#         else:
#             HEROES[hero[2]] = {hero[0]: hero[1]}


def fetch_config():
    fetch_severs()


def fetch_data(url_player):
    global DATA_SOURCE
    cio('正在读取数据... timeout: 10s', 'info')
    url_player = urllib.parse.unquote(url_player, encoding='utf-8')
    parsed = urllib.parse.urlparse(url_player)
    # queries = urllib.parse.parse_qs(parsed.query)  # 参数可省略
    m = re.match(r'/cgi/mweb/equip/(\d+)/(.+)', parsed.path)
    if not m:
        cio('非法藏宝阁商品详情链接', 'error')
        return None
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
    }  # 「痒痒熊快照」式神属性 ID - 名字表
    hero_attrs_id_name_no_base = {
        'effect_hit_rate': pick_dwarf.ATTRS[9],
        'effect_resist_rate': pick_dwarf.ATTRS[10]
    }  # 「痒痒熊快照」式神属性 ID - 名字表（基础值为 0）
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
            'id': item['heroUid'],  # 式神 ID，同 item['uid']
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
            'born': 0,  # 获取时间戳（未记录）
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
            'random_attrs': attrs_sub,  # 与 attrs 记录重复，用意不明
            'random_attr_rates': []  # 似乎是想记录副属性成长系数，但实际未记录
        })
    data_core_2 = {
        'player': {
            'id': 0,  # TODO: 非 data_core['equipid']
            'server_id': 0,  # TODO: 非 data_core['serverid']
            'name': data_core['equip_name'],  # TODO: 游戏名 or 卖家名？
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
        'hero_equip_presets': [],  # 御魂方案（未记录）
        'hero_book_shards': [{
            'hero_id': int(hero_id),
            'shards': info['num'],
            'books': 0,  # （未记录）
            'book_max_shards': 0  # 合成量（未记录）
        } for hero_id, info in data_game['hero_fragment'].items()],  # 式神碎片
        'realm_cards': [],  # TODO （未记录）
        'story_tasks': []  # TODO （未记录）
    }
    return {
        'version': '0.99.7-cbg',
        'timestamp': datetime.datetime.strptime(
            data['equip']['create_time'], '%Y-%m-%d %H:%M:%S'
        ).strftime('%Y-%m-%dT%H:%M:%S+08:00'),
        'cbg_url': url,
        'data': data_core_2
    }


# 依赖 pywin32 库，放弃
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
                    print(pick_dwarf.log(piece, tag) if tag else piece)
            else:
                print(pick_dwarf.log(content, tag) if tag else content)
    finally:
        lock.release()


def parse_args(args):
    try:
        opts, args = getopt.getopt(args, 'hvu:', ['help', 'version', 'url='])
    except getopt.GetoptError:
        opts, args = [('-h', '')], []
    url_player, helped = None, False
    for opt, value in opts:
        if opt in ('-h', '--help'):
            cio(COPYRIGHT)
            cio(HELP)
            helped = True
        elif opt in ('-v', '--version'):
            cio(VERSION)
            helped = True
        elif opt in ('-u', '--url'):
            url_player = value
    if not url_player and args:
        url_player = args[0]
    if not helped and not url_player:
        cio(COPYRIGHT)
        cio(HELP)
    return url_player


def main():
    global thread_fetch_config, thread_fetch_data, thread_bench, thread_save
    thread_fetch_config = Thread(target=fetch_config)
    thread_fetch_config.start()
    if len(sys.argv) > 1:
        url_equip = parse_args(sys.argv[1:])
        if not url_equip:
            return
        cio(COPYRIGHT)
    else:
        cio(COPYRIGHT)
        url_equip = cio('藏宝阁链接: ', 'input', True)
    thread_fetch_data = Thread(target=fetch_data, args=(url_equip,))
    thread_fetch_data.start()
    thread_bench = Thread(target=bench)
    thread_bench.start()
    thread_save = Thread(target=save, args=(url_equip,))
    thread_save.start()
    thread_save.join()
    bench_suits()


if __name__ == '__main__':
    # 由于使用 pyinstaller 打包 EXE 后运行机制发生变化，多进程代码会异常。
    # 添加该行代码使 multiprocessing 模块能正常工作。
    # https://github.com/pyinstaller/pyinstaller/wiki/Recipe-Multiprocessing
    multiprocessing.freeze_support()
    main()