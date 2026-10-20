# Egern 基础去广告模块

版本：1.0.0。原生 Egern YAML 模块，18 条精确域名 `REJECT` 规则。

这是小型基础版：阻断选定的 Google 广告、百度广告、腾讯广告、小米广告和 Unity 广告服务主机。仅处理命中域名且经过 Egern 的流量，不做 HTTPS 解密，不安装证书，不执行 JavaScript，不修改 DNS 或节点，不包含远程规则集，不收集或上传浏览记录。Egern 自身的日志行为由现有配置控制。

## 添加到 Egern

先备份现有配置。不要把本模块当作完整代理配置导入，更不要覆盖原有节点和订阅。

1. 打开 Egern，进入「工具 → 模块」，点击右上角「+」。
2. 在 URL 中粘贴下面的模块地址，保存并启用「基础去广告 · 无需解密」。
3. 确认 Egern 隧道正在运行，再关闭并重新打开要测试的 App 或网页。无需为此模块开启 MITM 或安装证书。

```text
https://raw.githubusercontent.com/zhaohantao1360-hash/wabi-workspace/main/egern/adblock-lite.yaml
```

入口以官方当前文档为依据，不同版本的界面文字可能有差异。该地址随仓库 `main` 分支更新；Egern 远程模块默认每 24 小时更新一次。这不是后台维护或持续更新的承诺。

如果使用配置文件管理模块，可将下面一项追加到现有 `modules` 数组，不要创建两个同名顶层 `modules` 键，也不要替换整个配置：

```yaml
modules:
  - name: "基础去广告 · 无需解密"
    url: "https://raw.githubusercontent.com/zhaohantao1360-hash/wabi-workspace/main/egern/adblock-lite.yaml"
    enabled: true
    update_interval: 86400
```

## 如何停用、排查误拦截

- 在「工具 → 模块」里停用或移除本模块；配置文件方式则将对应项的 `enabled` 改为 `false` 或移除该项。
- 若网页跳转、视频、奖励广告或 App 功能异常，先停用本模块，再重开 App 比较。广告落地页、看广告领取奖励等功能可能受影响，不承诺零误伤。
- 如需保留大部分规则，可保存为本地副本，再删除造成问题的那一条 `domain` 规则；不要直接修改不认识的域名或扩大到父域名。
- 没有效果时，先确认模块已启用、资源已下载、流量经过 Egern，再在 Egern 的连接/规则记录中查看实际命中。Egern 按顺序采用首条匹配规则；现有主配置和其他模块可能影响结果。本项目未验证所有版本的模块合并次序，不建议盲目改动整份配置。

## 能力边界

- 这是精确主机匹配，不是通配符：`ad.doubleclick.net` 不会顺带匹配 `x.ad.doubleclick.net`。以缩小误拦范围为优先，覆盖率有意有限。
- 不拦整个 `qq.com`、`baidu.com`、`google.com`、`apple.com`、`alipay.com` 等共用业务域名；但这不等于验证了所有登录、支付或其他功能均正常。
- 不能处理与正常内容共用域名的广告、已缓存广告、网页空白占位、所有 App 开屏广告，也不保证去除 YouTube/视频插播广告。
- 不能绕过付费、会员或平台权限；不含解锁功能。
- 不拦截绕过 Egern、仅以 IP 连接且未能识别域名、或其他未命中这 18 个主机的流量。
- 手机同一时间通常只能运行一个同类 VPN 隧道。保留现有代理设置，不要为本模块下载陌生证书或提供账号密码。

## 来源与许可

Egern 规范：
- [模块格式与远程引用](https://egernapp.com/docs/configuration/modules/)
- [规则格式、首条匹配和 REJECT](https://egernapp.com/docs/configuration/rules/)
- [官方添加模块界面说明](https://egernapp.com/zh-CN/docs/configuration/widgets/)

域名从 StevenBlack/hosts 固定快照中人工选取，不是全量同步，也不代表上游背书。快照提交、SHA-256 与逐项列表见 [sources.json](sources.json)。第三方 MIT 许可见 [THIRD-PARTY-LICENSE.txt](THIRD-PARTY-LICENSE.txt)，模块注释中亦保留完整许可。上游聚合列表不保证每个域名永远只有广告用途。

## 本地检查

在仓库根目录，使用已有的 `requirements.txt`：

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python egern/test_adblock.py
```

可选：下载 `sources.json` 中固定的源文件，在本地核对来源（检查脚本不会自行联网）：

```sh
.venv/bin/python egern/test_adblock.py --upstream-hosts /path/to/hosts
```

已完成：YAML 解析及重复键拒绝、原生模块字段结构、18 条规则去重、无脚本/MITM/DNS 改写、84 个本地精确匹配正反例，以及全部域名在哈希核对后的固定源快照中的成员校验。

本地匹配测试只是按文档写的简化模型，不是 Egern 内核。没有 Egern 真机导入或实际流量实测；不能把本地通过当作已验证真实去广告效果或 App 兼容性。
