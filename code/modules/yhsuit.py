#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
模块：多进程计算御魂方案
"""

from multiprocessing import Manager
from multiprocessing import Pool

from modules import pick_dwarf


def gross(yuhuns, attr):
    if not yuhuns:
        return 0
    yuhuns = [item for item in yuhuns if item]
    total = sum(map(lambda item: (item['main2'].get(attr, 0)
                                  + item['subs2'].get(attr, 0)
                                  + item['sgl2'].get(attr, 0)),
                    yuhuns))
    if attr in pick_dwarf.ATTRS_DBL:
        present = pick_dwarf.ATTRS_DBL[attr]
        for kind in present[1]:
            if len([item for item in yuhuns if item['kind'] == kind]) >= 2:
                total += present[0]
    return total


def _damage(yh123456, hero_panel, attrs_threshold):
    if len(yh123456) != 6:
        return 0
    for attr, value in attrs_threshold.items():
        if hero_panel.get(attr, 0) + gross(yh123456, attr) < value:
            return 0
    attack = (hero_panel['攻击'] * (1 + gross(yh123456, '攻击加成'))
              + gross(yh123456, '攻击'))
    crit_power = hero_panel['暴击伤害'] + gross(yh123456, '暴击伤害')
    return attack * crit_power  # 总攻击 * 总暴伤


def _suit(yhs123456, hero_panel, attrs_thr, dmg_thr, q):
    if not q.empty():
        return
    for yh1 in yhs123456[0]:
        if not q.empty():
            break
        for yh2 in yhs123456[1]:
            if not q.empty():
                break
            for yh3 in yhs123456[2]:
                if not q.empty():
                    break
                for yh4 in yhs123456[3]:
                    if not q.empty():
                        break
                    for yh5 in yhs123456[4]:
                        if not q.empty():
                            break
                        for yh6 in yhs123456[5]:
                            dmg = _damage([yh1, yh2, yh3, yh4, yh5, yh6],
                                          hero_panel, attrs_thr)
                            for section in dmg_thr:
                                if section[0] <= dmg <= section[1]:
                                    q.put([yh1, yh2, yh3, yh4, yh5, yh6])
                                    break


def cal(data, hero_panel, suits42, attrs246, attrs_thr, dmg_thr, acc):
    """计算指定式神御魂套装

    Args:
        data (list): 标准格式御魂集
        hero_panel (dict): 式神基础面板
        suits42 (tuple): 御魂套装：4 件套、2 件套
        attrs246 (list): 指定二四六号位主属性，一个位置多条则按序计算
        attrs_thr (dict): 属性限制，如 {'暴击': 1}
        dmg_thr (tuple): 攻暴区间要求（可指定多个区间）
        acc (tuple): 为每个位置设定输出分来加速计算

    Returns:
        list: 御魂套装
    """
    attrs123456 = [['攻击'], attrs246[0], ['防御'],
                   attrs246[1], ['生命'], attrs246[2]]
    data = [item for item in data if item['level'] == 15
            and item['kind'] in suits42]
    data_s4 = [[], [], [], [], [], []]
    data_s2 = [[], [], [], [], [], []]
    for i in range(6):
        data_s4[i] = [item for item in data if (
                item['kind'] == suits42[0] and item['pos'] == i + 1
                and item['attrs']['main']['attr'] in attrs123456[i]
                and item['score_dmg'] >= acc[i]
        )]
        data_s2[i] = [item for item in data if (
                item['kind'] == suits42[1] and item['pos'] == i + 1
                and item['attrs']['main']['attr'] in attrs123456[i]
                and item['score_dmg'] >= acc[i]
        )]

    for i in range(6):
        data_s4[i].sort(key=lambda x: x['score_dmg'], reverse=True)
        data_s2[i].sort(key=lambda x: x['score_dmg'], reverse=True)
    # 使用多进程而非多线程，可真正发挥 CPU 多核心的算力
    # 此处有坑：借助 Pool 所创进程之间通信需用 multiprocessing.Manager().Queue()，
    # 而非 multiprocessing.Queue()，后者会导致子进程不执行。
    # 使用 Process 所创进程之间可用 multiprocessing.Queue() 通信。
    p = Pool()  # 默认大小为伪 CPU 核心数
    q = Manager().Queue()  # 非 q = Queue()
    for i_s2_1 in range(5):  # 将计算任务分为 15 份
        for i_s2_2 in range(i_s2_1 + 1, 6):
            yhs123456 = [(data_s2[i] if i == i_s2_1 or i == i_s2_2
                          else data_s4[i]) for i in range(6)]
            p.apply_async(_suit, args=(
                yhs123456, hero_panel, attrs_thr, dmg_thr, q
            ))
    p.close()
    p.join()
    return q.get(False) if not q.empty() else []


if __name__ == '__main__':
    print('module: yhsuit')
