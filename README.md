# Shared Surge rules

可公开、跨设备共用的域名分流名单。只共享分类，各设备保留节点、策略组、进程规则、私人域名、内网和 DNS 设置。本仓库不是完整 Surge 配置，不包含代理凭据。

| 文件 | 内容 |
| --- | --- |
| `rules/ai-services.list` | AI 服务及现有登录、支付、共享 CDN 依赖；部分依赖也服务非 AI 网站 |
| `rules/china-direct-v2.list` | China + ChinaMax 的具体域名、人工补充和 `.cn` 基线；须与前置海外例外配对 |
| `rules/overseas-services.list` | 明确的海外服务族，优先于国内名单用于路由和 DNS |
| `rules/china-direct.list` | 兼容旧配置的具体域名版本，不增加 `.cn`，避免未迁移设备提前扩大直连 |
| `rules/model-downloads.list` | 模型下载站域名；不把整个共享云存储归为下载 |

## 引用

以下只是插入片段，策略组须在设备本地定义。原有内网/公司等专用规则应保留正确优先级，AI 应在国内规则之前；已有 AI 进程规则仍留在本地。最后由本地代理组兜底。

```ini
[Rule]
RULE-SET,https://raw.githubusercontent.com/mkdirmushroom/surge-shared-rules/main/rules/model-downloads.list,模型下载,no-resolve,extended-matching,update-interval=3600
RULE-SET,https://raw.githubusercontent.com/mkdirmushroom/surge-shared-rules/main/rules/ai-services.list,AI,no-resolve,extended-matching,update-interval=3600
RULE-SET,https://raw.githubusercontent.com/mkdirmushroom/surge-shared-rules/main/rules/overseas-services.list,兜底,no-resolve,extended-matching,update-interval=3600
RULE-SET,https://raw.githubusercontent.com/mkdirmushroom/surge-shared-rules/main/rules/china-direct-v2.list,DIRECT,no-resolve,extended-matching,update-interval=3600

[Host]
RULE-SET:https://raw.githubusercontent.com/mkdirmushroom/surge-shared-rules/main/rules/ai-services.list = server:https://1.1.1.1/dns-query
RULE-SET:https://raw.githubusercontent.com/mkdirmushroom/surge-shared-rules/main/rules/overseas-services.list = server:https://1.1.1.1/dns-query
RULE-SET:https://raw.githubusercontent.com/mkdirmushroom/surge-shared-rules/main/rules/china-direct-v2.list = server:https://dns.alidns.com/dns-query
```

`extended-matching` 使域名规则同时匹配 Surge 已识别的 TLS SNI / HTTP Host，适用于连接目标是 IP 但仍带域名信息的请求。没有 SNI/Host 的裸 IP 请求仍依赖 IP 或明确的本地例外；不要因此放开整个云厂商 ASN。

DNS 映射和路由引用同一个 URL。本机 DNS 映射不强制 Snell 代理请求改为本地解析；域名代理默认仍在出口端解析。`[Host]` 规则集映射在 Mac 5.10+ 支持；手机端需按实际 Surge 版本验证。使用普通外部规则，不依赖 Mac 6.9 的嵌套规则集。

Parsec 的点对点 UDP、内网、Apple/iCloud 例外属于本地策略，不在公共 AI 名单中决定。不要通过整个 Parsec 进程强制代理来统一普通网站分流。

## 更新和回滚

1. 日常补充修改 `source/*.list`；运行 `python3 scripts/build.py`，检查生成 diff。
2. 运行 `python3 scripts/build.py --check` 和 `python3 scripts/check-routing.py`；确认没有私人域名、IP、节点、订阅或凭据，再提交。
3. 推送后，各设备按 Surge 外部资源更新周期获取；不是立即远程重载。
4. 上游国内名单使用已审核快照。升级时从明确的上游 commit 获取 `China_Domain.list` / `ChinaMax_All.list`，更新 `upstream/provenance.json` 的 revision/hash，重新生成并审核 diff。构建从上游只提取具体 DOMAIN / DOMAIN-SUFFIX，丢弃上游顶级域名及其他规则类型；v2 在过滤后单独加入经过明确选择的 `.cn` 基线。不会无人审核地把上游变化直接发布。
5. 回滚使用 Git revert；也可把本地 URL 的 `main` 改为审核过的 commit SHA，固定版本。

远程资源首次获取必须成功。GitHub 不可达时更新可能失败；缓存行为应以设备实际状态为准。首次迁移前应下载验证并保留完整本地备份。国内名单可能遗漏或错分；除 `.cn` 基线和本地明确例外外，未知域名由设备的代理组兜底。

## 来源与许可

- [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)：国内域名数据及部分 OpenAI/Gemini 域名，GPL-2.0；原始国内文件保留作者注释，版本及 SHA-256 见 `upstream/provenance.json`。
- [SukkaW/Surge](https://github.com/SukkaW/Surge)：参考其按用途拆分规则、优先使用域名集合的组织方式；未复制该项目代码或列表。
- [Surge RULE-SET](https://manual.nssurge.com/rules/ruleset.html) 与 [DNS 映射](https://manual.nssurge.com/dns/local-dns-mapping.html)：语法与优先级依据。

本仓库按随附 GPL-2.0 许可发布。仅维护公开域名事实和规则；不接受完整用户配置、账户数据或日志。

## Priority and coverage safeguards

国内扩展采用 blackmatrix7 ChinaMax 已固定版本的域名部分，并保留原 China 名单补充。ChinaMax 上游标记为实验性；本仓库不直接启用其整包规则。`scripts/build.py` 排除与 AI、模型下载及 `source/china-exclusions.list` 海外服务族相交的域名规则（包括会覆盖这些域名的父级后缀），同时验证典型国内服务和海外边界。名单仍无法保证覆盖所有国内站点或识别所有上游误分类。

设备端顺序：既有必要的基础连接/明确覆盖规则 → AI 应用进程 → 模型下载和 AI 域名 → 其他服务/公司/内网/Apple 等明确规则 → 已知海外规则 → 国内名单 → LAN / GEOIP no-resolve → FINAL 兜底。进程例外与 Apple/iCloud 直连仍按设备原有用途保留。模型下载独立出口只适用于未被 AI 应用进程规则提前选中的连接。

`GEOIP,CN,DIRECT,no-resolve` 不主动解析未知域名，避免为了分流而增加海外 DNS 等待；未知域名仍代理兜底。国内 DNS 与路由使用同一份过滤后名单，不能只在 DNS 中添加域名就假定它会直连。v2 明确采用 `.cn` 直连基线，补足上游用 `cn` 汇总后丢失的国内域名；不放开 `.ms` 等其他顶级域名。`.cn` 是覆盖率取舍，不是服务所在地证明：未知海外服务若使用 `.cn` 仍可能被直连，需要补充到前置海外或 AI 名单。已知 Google/Microsoft 的 `.cn` 域名已加入海外例外。

GitHub 只分发域名数据，**不会同步策略组、FINAL 或设备配置**。各设备统一定义「兜底」并使用 `FINAL,兜底,dns-failed`；设备配置修改后由使用者手动重载。远程规则数据则会按既有资源更新周期获取，可能在不重载整份配置时生效。

## v2 migration

先在 `[Rule]` 和 `[Host]` 同时加入 `overseas-services.list`，置于国内名单之前，并保持 AI 优先，再将两处国内 URL 切到 `china-direct-v2.list`。校验并手动重载整份配置后，配对顺序才会生效。不能单独替换国内 URL，也不要将 v2 内容发布到旧 URL。共享名单更新后按 `update-interval=3600` 获取；设备配置、策略组与上游快照不会因此自动同步。

公开 CI 检查生成一致性、来源与域名边界，以及路由/DNS 分类样例。设备的进程、平台、内网与策略组回归应在私有配置中另行校验；公共分类测试不替代 Surge 原生校验或实际设备运行验证。
