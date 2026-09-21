# Shared Surge rules

可公开、跨设备共用的域名分流名单。只共享分类，各设备保留节点、策略组、进程规则、私人域名、内网和 DNS 设置。本仓库不是完整 Surge 配置，不包含代理凭据。

| 文件 | 内容 |
| --- | --- |
| `rules/ai-services.list` | AI 服务及现有登录、支付、共享 CDN 依赖；部分依赖也服务非 AI 网站 |
| `rules/china-direct.list` | 国内纯域名名单及人工补充，不含关键词、IP、ASN 或进程规则 |
| `rules/model-downloads.list` | 模型下载站域名；不把整个共享云存储归为下载 |

## 引用

以下只是插入片段，策略组须在设备本地定义。原有内网/公司等专用规则应保留正确优先级，AI 应在国内规则之前；已有 AI 进程规则仍留在本地。最后由本地代理组兜底。

```ini
[Rule]
RULE-SET,https://raw.githubusercontent.com/mkdirmushroom/surge-shared-rules/main/rules/model-downloads.list,模型下载,no-resolve,update-interval=86400
RULE-SET,https://raw.githubusercontent.com/mkdirmushroom/surge-shared-rules/main/rules/ai-services.list,AI,no-resolve,update-interval=86400
RULE-SET,https://raw.githubusercontent.com/mkdirmushroom/surge-shared-rules/main/rules/china-direct.list,DIRECT,no-resolve,update-interval=86400

[Host]
RULE-SET:https://raw.githubusercontent.com/mkdirmushroom/surge-shared-rules/main/rules/ai-services.list = server:https://1.1.1.1/dns-query
RULE-SET:https://raw.githubusercontent.com/mkdirmushroom/surge-shared-rules/main/rules/china-direct.list = server:https://dns.alidns.com/dns-query
```

DNS 映射和路由引用同一个 URL。本机 DNS 映射不强制 Snell 代理请求改为本地解析；域名代理默认仍在出口端解析。`[Host]` 规则集映射在 Mac 5.10+ 支持；手机端需按实际 Surge 版本验证。使用普通外部规则，不依赖 Mac 6.9 的嵌套规则集。

Parsec 的点对点 UDP、内网、Apple/iCloud 例外属于本地策略，不在公共 AI 名单中决定。不要通过整个 Parsec 进程强制代理来统一普通网站分流。

## 更新和回滚

1. 日常补充修改 `source/*.list`；运行 `python3 scripts/build.py`，检查生成 diff。
2. 运行 `python3 scripts/build.py --check`；确认没有私人域名、IP、节点、订阅或凭据，再提交。
3. 推送后，各设备按 Surge 外部资源更新周期获取；不是立即远程重载。
4. 上游国内名单使用已审核快照。升级时从明确的上游 commit 获取 `China_Domain.list`，更新 `upstream/provenance.json` 的 revision/hash，重新生成并审核 diff。不会无人审核地把上游变化直接发布。
5. 回滚使用 Git revert；也可把本地 URL 的 `main` 改为审核过的 commit SHA，固定版本。

远程资源首次获取必须成功。GitHub 不可达时更新可能失败；缓存行为应以设备实际状态为准。首次迁移前应下载验证并保留完整本地备份。国内名单可能遗漏或错分，未知域名应由设备的代理兜底处理。

## 来源与许可

- [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)：国内域名数据及部分 OpenAI/Gemini 域名，GPL-2.0；原始国内文件保留作者注释，版本及 SHA-256 见 `upstream/provenance.json`。
- [SukkaW/Surge](https://github.com/SukkaW/Surge)：参考其按用途拆分规则、优先使用域名集合的组织方式；未复制该项目代码或列表。
- [Surge RULE-SET](https://manual.nssurge.com/rules/ruleset.html) 与 [DNS 映射](https://manual.nssurge.com/dns/local-dns-mapping.html)：语法与优先级依据。

本仓库按随附 GPL-2.0 许可发布。仅维护公开域名事实和规则；不接受完整用户配置、账户数据或日志。
