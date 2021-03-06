# 号来

[![Release](https://img.shields.io/badge/Release-1.6-brightgreen.svg)](https://github.com/nguaduot/yys-cbg-bench)
[![Download](https://img.shields.io/badge/Download-EXE-brightgreen.svg)](dist/%E5%8F%B7%E6%9D%A51.6.exe)

[阴阳师藏宝阁](https://yys.cbg.163.com/)衍生小工具，用于提取游戏帐号要点并生成图文报告。

其实，用处不大，藏宝阁官网展示的数据不足深挖，无非是算算一速啥的。

例：

商品页面：[阴阳师藏宝阁-夏之蝉-南瓜多糖](https://yys.cbg.163.com/cgi/mweb/equip/21/202101152201616-21-VTG7H9VQQFVSG)

生成报告：[完整结果](sample/cbg_中国区-iOS_夏之蝉_南瓜多糖_20210122225748_bench.png) | [精简结果](sample/cbg_中国区-iOS_夏之蝉_南瓜多糖_20210122225748_bench_lite.png)

> 「号来」同时发布到 NGA 论坛阴阳师板块，可回复交流：
> 
> [[心得交流] [01/28] [v1.6] 号来：藏宝阁辅助看号工具](https://nga.178.com/read.php?tid=23005018)

### 依赖

「号来」使用 Python3 编写，依赖的第三方库：

```
pip install pillow
```

### 文档

```
python cbg_bench.py -h
```

```
+ 选项：
  -h, --help     帮助
  -v, --version  程序版本
  -l, --lite     输出结果精简化(未指定则输出完整结果)
  -u, --url      藏宝阁商品详情链接
+ 若未指定 -u, 程序会读取未知参数, 若也无未知参数, 不启动程序
+ 不带任何参数也可启动程序, 会有参数输入引导
输出结果:
{上架中/已售出/已取回/未上架}: ¥{售价，公示期/已取回状态将提示“!”} {签到天数}天 !{若不满级则显示等级提示} !{若检测到合服则显示提示, 多服合一无法获知归属服, 需留心}
  金币 {金币} 黑蛋 {'御行达摩'数量+推测已消耗量(据此可了解练度)} 体力 {体力} 勾玉 {勾玉} 蓝票 {神秘的符咒+现世符咒} 御札 {御札/金御札} 魂玉 {留存魂玉数量, 大于0时显示}
  关键成就: {风姿度, 据此可了解外观向收集量(皮肤/头像框等)} {成就点数, 5000+可报名特邀测试} {已达成的最高非酋成就} {探索关卡的妖怪是否全部发现}
图鉴SP&SSR式神: {'500天未收录SSR'未使用则显示} {'999天未收录SP'未使用则显示}
  当下未拥有式神...{提示除联动的最新SP/SSR式神}: {于当下版本的未拥有SP数量}+{于当下版本的未拥有SSR数量}
    SP碎片收集: {未拥有式神(图鉴已点亮也可能未拥有, 需留心)} {该式神碎片量, 据此可知有无碗} ...
    SSR碎片收集: {未拥有式神(图鉴已点亮也可能未拥有, 需留心)} {该式神碎片量, 据此可知有无碗} ...
  关键多号机拥有情况: {式神} {该式神拥有数量} ...
联动式神拥有&碎片收集情况:
  {联动期数}: {该期式神} {拥有数量(低稀有度低星式神无法获知)}/{碎片量(低稀有度式神无法获知)} ...
  ...
已收集皮肤: {曜之阁已开启则显示}
  庭院: 初语谧景 + {除初始之外的其他庭院} ...
  氪金典藏...{提示最新皮肤}: {已收集的氪金式神典藏皮肤数量}
    {皮肤名} ...
六星满级/满级/六星御魂: {六星满级御魂数量}/{各星级满级御魂总量}/{藏宝阁未提供未满级御魂数据, 因此六星御魂总量无法查到,
请知悉}/
  满级普通御魂: {满级非首领御魂数量}
    {两件套属性} {该类御魂数量}
    ...
  满级首领御魂: {满级首领御魂数量}
    荒骷髅 {'荒骷髅'数量}
    歌伎 {'鬼灵歌伎'数量}
散一速: {散件套一速} 招财 {招财套一速}
  [{位置}] {该位置散一速套御魂, 以及其余速度满收益御魂} {副属性'速度'值} ...
  ...
高分暴击&暴伤御魂: {高分暴击御魂数量}+{高分暴击伤害御魂数量}
  陆|暴击 输出分:
    {陆号位主属性'暴击'的高分御魂} {该御魂分数, 按有效属性'攻击加成'/'速度'/'暴击'/'暴击伤害'评分, 非首领御魂5+, 首领御 魂7+} ...
    ...
  陆|暴击伤害 输出分&副属性暴击值:
    {陆号位主属性'暴击伤害'的高分御魂} {该御魂分数, 按有效属性'攻击加成'/'速度'/'暴击'/'暴击伤害'评分, 非首领御魂5+, 首 领御魂7+}: 暴击 {副属性'暴击'值}
    ...
部分御魂方案:
  {是否能做}: {何用途的何式神} {御魂套装} {加速计算的分数限制, 按有效属性'攻击加成'/'速度'/'暴击'/'暴击伤害'评分}
  ...
* 通过计算御魂方案来粗略了解御魂池及练度, 内置的几种方案(从易到难排序):
  1. 真蛇副本用到的超星针歌小小黑, 攻暴值未作限制, 基本满暴就能用
  2. 探索困28副本用到的超星破荒/破歌茨林, 破荒攻暴 15815+, 破歌 15723+
     数据参考: https://nga.178.com/read.php?tid=21014251
  3. 觉醒十层副本用到的高速破荒茨林, 速度 160+, 攻暴 15810+
     数据参考: https://nga.178.com/read.php?tid=15698562
  4. 御魂十层副本用到的高速狂荒/破荒玉藻前, 速度 162+, 狂荒攻暴 15696~20090, 破荒 17843~20090
     数据参考: https://nga.178.com/read.php?tid=20569256
  5. 探索困28副本用到的超星破荒玉藻前, 攻暴 21644+
     数据参考: https://nga.178.com/read.php?tid=21014251
* 计算过程可能比较耗时, 已最大程度优化, 分派大量子进程同时计算, CPU核心全利用. '痒痒鼠, 烤机不?'
```

[号来生成文档](sample/号来1.6_help.png)

### 作者

> “不会在记事本用 Python 写小工具的程序猿的不是好痒痒鼠！”
>
> —「夏之蝉」区@**南瓜多糖**

痒痒鼠相关问题欢迎来找我讨论，代码改进或漏洞也欢迎一起交流。

### 更新日志

v1.6.210128
+ 检测SP/SSR未拥有式神所用图鉴从上架时调整至当下。如远古时期上架的全图鉴帐号在出了新式神的当下便不再视为全图鉴
+ 增加对已购氪金典藏皮肤的显示，并和庭院皮肤一起合并到「已收集皮肤」板块
+ 增加留存魂玉显示
+ 增加最新SP/SSR显示，便于自行判断数据时效性
+ 未拥有式神按上线时间有序排列
+ 源数据已存在时采用覆盖保存而非跳过，避免再次存档时无法反映商品变动信息
+ 跟进第六期联动x鬼灭之刃
+ 修复BUG：无法解析早期收藏商品
+ 修复BUG：误将卖家名识别为角色昵称

v1.0.200817
+ 第一版发布