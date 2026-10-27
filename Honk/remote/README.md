# Honk 远程自定义规则

适用于支持 `rule_set` 的 Honk 修改版，原版不保证支持。列表使用 classical/text 格式，不包含出站动作；不是完整 `.dae` 配置。仍在 `Clash/Direct.list`、`Proxy.list`、`AI.list` 维护域名，运行 `python scripts/generate_honk_rules.py` 同步生成。

把 `sources.dae` 的声明及路由引用合入主配置，自定义规则放在公共大规则和 fallback 前。可在 `/providers/rules` 查看来源并单独更新。下载成功且激活后缓存，失败保留旧规则。首次没有缓存时，必须下载成功才能启动。

示例下载走 `🇭🇰 港台自动`，该组必须存在且可用；可按网络修改 route。不能把电脑开启本机代理当作路由器可下载的依据。interval: 86400 为每天更新。

`Honk/Direct.dae`、`Proxy.dae`、`AI.dae` 已改为远程来源声明；与合并版 sources.dae 二选一，不要重复引用。
