# Egern 基础去广告模块

版本：2.0.0（2026-10-20）。原生 Egern YAML：396 条规则，其中 219 条为按域名边界匹配的 `domain_suffix`，177 条为精确 `domain`。

这是对初版 18 条规则的实质扩展，不是全能去广告工具。基础版仍不做 HTTPS 解密、不含证书、脚本、URL 重写、DNS 改写或远程规则集，不修改节点/订阅，也不收集或上传浏览记录。Egern 自身日志行为由现有配置控制。

## 相比初版增强了什么

- 腾讯广告：除原有少量 SDK 主机外，覆盖选定广点通请求、广告素材 `gdtimg.com` / `ugdtimg.com` 及广告子域。
- 百度广告：增加 `mobads.baidu.com`、部分广告配置与广告点击服务，而非阻断整个百度。
- 字节 / 快手：增加 Pangle（`pangle.io`）、快手广告联盟 `adkwai.com` 和选定广告 SDK 主机。
- 阿里广告：增加 Tanx 及汇川广告服务的选定主机，不封淘宝/阿里云/阿里 CDN 父域。
- Google、Unity / ironSource、AppLovin / Vungle、InMobi、TopOn、Sigmob、Amazon Ads 等广告服务：扩大选定请求/素材主机覆盖。
- 许可来源明确支持子域匹配的条目使用 `domain_suffix`，例如 `pangle.io` 同时覆盖其子域；不是所有条目都升级成父域封锁。
- 每条规则增加 `Wabi广告 · 平台名` 标识，便于在命中记录里区分是不是这个模块生效。

这些规则可能减少由对应第三方广告网络加载的开屏、横幅、插屏、广告视频/奖励广告；具体效果取决于 App 实际请求、缓存、连接和规则优先级。规则多不等于已验证去掉更多实际广告；没有 Egern 真机实测。

## 添加或更新

不要把本模块当作完整代理配置导入，也不要覆盖节点、订阅。先备份现有配置。

模块 URL 与初版相同：

```text
https://raw.githubusercontent.com/zhaohantao1360-hash/wabi-workspace/main/egern/adblock-lite.yaml
```

1. 初次添加：Egern → 工具 → 模块 → 右上角「+」，粘贴地址、保存并启用「基础去广告 · 无需解密」。
2. 已安装初版：在已有远程模块中执行更新/重新下载，查看描述是否出现 `v2.0.0`、`396`。不要同时添加两份相同模块。界面措辞以所用版本为准；如果找不到更新入口，可先移除旧项，再用同一 URL 添加。
3. 确认 Egern 隧道运行，彻底关闭并重开待测试的 App，或刷新网页。无需开 MITM 或安装证书。

Egern 文档中，远程模块默认更新间隔为 86400 秒（24 小时）；这不是本项目持续维护或每日更新规则的承诺。本版本冻结了来源，没有运行时第三方规则/脚本下载。`main` 地址将来若有新提交，下载内容会随之变化。

通过配置文件管理模块时，将这一项追加到现有 `modules` 数组，不要创建第二个同名顶层键或替换整个配置：

```yaml
modules:
  - name: "基础去广告 · 无需解密"
    url: "https://raw.githubusercontent.com/zhaohantao1360-hash/wabi-workspace/main/egern/adblock-lite.yaml"
    enabled: true
    update_interval: 86400
```

## 如何验证有没有效果

先看模块描述确认为 v2，再使用你实际会出现广告的 App/网页做开关对比。缓存与广告随机投放会影响单次结果。

- 连接/规则记录中，查看请求是否命中 `Wabi广告 · …`，结果是否 `REJECT`。例如 `mobads.baidu.com`、`pangle.io` 子域或 `adsmind.gdtimg.com`。只见其他规则拒绝，不能证明本模块生效。
- 命中说明请求被拦截；相关广告同时消失，才说明对该广告有效。没有请求命中，也可能是 App 没使用这些广告服务。
- 主配置/其他模块可能抢先匹配，导致此模块无法命中；Egern 采用首条匹配规则。应查看实际命中原因，不要为了测试盲目修改兜底分流、全局封锁或开启 HTTPS 解密。
- 日志截图对外分享前，遮住账号、Cookie、令牌及完整请求参数。这个模块本身不需要这些信息。

## 参考配置：采用与未采用的能力

本次完整审阅了用户提供的 [BlockAdvertisers-hark.yaml](https://raw.githubusercontent.com/zhaohantao1360-hash/Hark/main/BlockAdvertisers-hark.yaml)（审阅快照哈希见 `sources.json`）：330 条规则、4 条拼多多路径重写、3 个 MITM 主机。该文件本身没有 JavaScript 或远程规则集，但含宽泛关键词、IP、统计/推送域名及强制直连例外；它不能直接视为仅拦广告的零风险列表。

参考了其“按广告平台覆盖请求与素材”的思路，没有整体复制上游可莉集合。Hark 仓库在审阅时未提供许可证；域名集合按独立、可分发来源重新筛选：HaGeZi LIGHT 固定快照（GPL-3.0）和原有 StevenBlack/hosts 固定快照（MIT）。每条条目的来源、类型与快照 SHA-256 都记录在 `sources.json`。

没有采用：

- 拼多多 HTTPS 路径重写：需要 MITM，本版不附带、不启用。仅拦域名无法等价实现路径级去广告。
- `adstrategy`、`pangolin` 等跨业务关键词及 IP 封锁：范围/归属与误伤难控制。
- 极光/个推/Mob 等整域推送、短信验证、深链和统计平台封锁：可能影响通知、登录、分享或安装来源识别，不为了凑规则数量引入。
- 强制 `DIRECT` 例外：不替用户改变这些业务流量的原有代理路径。
- 未经独立来源核对的参考域名、需要证书的功能、会员解锁或账号权限绕过。

## 限制与误拦

- 不能保证去除 X（推特）官方 App「推广」帖子、抖音信息流、YouTube 贴片、与正常内容同域的广告、缓存广告或广告空白占位。
- 不拦共用的 `qq.com`、`google.com`、`baidu.com`、`taobao.com`、`apple.com`、`snssdk.com` 等父域；但不代表实际登录/支付/播放功能都测试通过。
- 广告点击跳转、看广告领积分、某些游戏奖励、广告主控制台或使用广告平台内容的功能可能受影响。实际 App 可能继续显示空白或等待超时。
- 只有流量经过 Egern 且域名可被识别、实际命中规则才有效；绕过隧道的流量/只有 IP 的连接不在此保证范围内。
- 本版本没有安装 Egern 真机、没有流量抓取、没有解密用户 HTTPS，也没有验证广告实际消失。模拟匹配不能替代真机。

## 停用与回退

功能异常时，先在 Egern 的模块列表停用或移除此模块，再重开目标 App 对比；不需卸载证书，因为本模块没有证书。

如需回退到原版，可将模块 URL 换成这个不可变的 v1 提交地址（18 条规则）：

```text
https://raw.githubusercontent.com/zhaohantao1360-hash/wabi-workspace/fadb631c5cf33f813d6a08310a13aed36c993887/egern/adblock-lite.yaml
```

不要同时启用 v1 和 v2。若仅某个广告域名需要放行，可保存本地副本并移除实际命中的那条规则；修改远程下载缓存可能被下次更新覆盖。

## 许可与可维护源码

- 组合 v2 模块、`sources.json`、构建与测试脚本采用 GPL-3.0-only，见 [LICENSE-GPL-3.0.txt](LICENSE-GPL-3.0.txt)。HaGeZi 原作者/贡献者的来源信息随冻结条目保留。
- StevenBlack 部分保留 MIT 许可：[THIRD-PARTY-LICENSE.txt](THIRD-PARTY-LICENSE.txt)，模块中亦保留完整通知。其他原有仓库文件不因本次更新改变许可。
- 没有将全部 HaGeZi LIGHT 列表搬入；只选取明确广告平台范围中的条目。原生 suffix 来源才保留子域语义；hosts 来源只采用精确主机。上游列表不是厂商担保，不保证域名永远只用于广告。
- 可编辑来源：`sources.json`。离线运行 `python egern/build_adblock.py` 可重建一模一样的模块，不会联网、不上传配置。更新快照需要人工核对来源/许可/范围后更新记录；未增加 Actions 或自动同步。

## 可重复本地检查

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python egern/build_adblock.py
.venv/bin/python egern/test_adblock.py
```

可选：另行下载 `sources.json` 中两个固定快照，传给检查脚本；脚本自身不联网：

```sh
.venv/bin/python egern/test_adblock.py \
  --upstream-hosts /path/to/stevenblack-hosts \
  --hagezi-domains /path/to/hagezi-light-domains
```

本轮通过：重复键拒绝、YAML 与原生字段结构、396 条规则去重/冗余检查、v1 覆盖保留、2450 个简化匹配正反例（含 46 个正常业务域名对照）、固定快照哈希与逐条成员校验，以及构建结果可复现。正常域名对照仅证明这些规则不匹配该域名，不等于相应 App 已实测正常。

Egern 官方格式依据：
- [模块与远程更新](https://egernapp.com/docs/configuration/modules/)
- [域名边界匹配、规则字段与首条匹配](https://egernapp.com/docs/configuration/rules/)
- [模块入口](https://egernapp.com/zh-CN/docs/configuration/widgets/)
