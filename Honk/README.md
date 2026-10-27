# Honk 远程自定义规则

本目录现在面向支持 `rule_set` 的 Honk 修改版。原版核心和原生 dae 不保证识别此扩展，升级前不要直接替换正在使用的配置。

## 文件职责

- `groups.dae`：自动选择、地区和服务分组；不再创建机场策略组。机场以真实 subscription 来源显示在支持的面板卡片中。
- `rule-providers.dae`：只声明来源名称、链接、格式、下载出口和更新间隔。
- `remote/Direct.list`、`Proxy.list`、`AI.list`：不含出站动作的 classical/text 规则正文，由核心通过 HTTPS 下载。
- `routing.dae`：只编排匹配条件与出站，按 Nikki 顺序接入自定义规则和公共分类，fallback 最后。
- `template.dae`：主配置，引用全局、私密订阅、分组、来源声明和 routing.dae。旧 Direct.dae/Proxy.dae/AI.dae 已由远程 .list 正文替代，不再部署。

## 部署

保留 LuCI 生成的 `system.dae` 和本地私密 `subscriptions.dae`。把 template.dae 放到 `/etc/honk/config.dae`，groups.dae 放到 `/etc/honk/groups.dae`；把 rule-providers.dae 和 routing.dae 放到 `/etc/honk/`。只有这两份编排文件需要本地部署；.list 正文由核心远程下载。旧 rules/*.dae 不再由此模板引用。

下载出口默认 `🇭🇰 港台自动`，该组必须存在并可连接；可根据网络改为 direct 或其他可用组。首次没有有效缓存时，下载失败会拒绝启动；成功后保留最后有效缓存。更新失败不会替换当前规则。

自定义规则优先于公共 GeoSite/GeoIP 规则，保留 Nikki 的顺序：my-direct、my-proxy、快手/抖音直连、my-ai，再按服务分流；重叠条目以先匹配者为准。fallback 必须最后。通过 `/rules` 核对顺序，通过 `/providers/rules` 查看规则来源、条目数和更新时间；`PUT /providers/rules/{name}` 单独更新。公共分类仍使用 GeoSite/GeoIP 数据库，不支持直接加载 MRS。

mitce 仅手动刷新可这样配置（仅修改版支持）：

```dae
subscription {
    mitce: 'https://YOUR-SUBSCRIPTION-URL' {
        auto_update: false
        interval: 0
        cache: true
    }
}
```

无缓存时需先手动刷新一次。不要把真实订阅链接或密码提交到仓库。

## 维护

名单在 `Clash/*.list` 维护，然后运行：

```sh
python scripts/generate_honk_rules.py
python scripts/generate_honk_rules.py --check
```

生成器保留精确匹配、后缀及关键词的含义和顺序，只生成远程列表正文，不修改来源声明和路由动作。`🚀 节点选择`、`🤖 ChatGPT` 和下载组必须与 groups.dae 一致。配置片段不是完整配置，不要用仅合并 node 块的 LuCI 导入入口导入。