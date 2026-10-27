# Honk 远程自定义规则

本目录现在面向支持 `rule_set` 的 Honk 修改版。原版核心和原生 dae 不保证识别此扩展，升级前不要直接替换正在使用的配置。

## 文件职责

- `groups.dae`：自动选择、地区和服务分组；不再创建机场策略组。机场以真实 subscription 来源显示在支持的面板卡片中。
- `Direct.dae`、`Proxy.dae`、`AI.dae`：声明远程来源并把来源名称绑定到出站，文件中不再逐条写域名。
- `remote/Direct.list`、`Proxy.list`、`AI.list`：不含出站动作的 classical/text 规则正文，由核心通过 HTTPS 下载。
- `template.dae`：主配置模板，按局域网保护、自定义规则、公共分类的顺序 include 本地配置片段。
- `remote/sources.dae`：三份来源声明和路由引用的合并版。与上述三个 .dae 二选一，不能重复 include。

## 部署

保留 LuCI 生成的 `system.dae` 和本地私密 `subscriptions.dae`。把 template.dae 放到 `/etc/honk/config.dae`，groups.dae 放到 `/etc/honk/groups.dae`；三个 .dae 和 examples/local.dae、examples/public.dae 放到 `/etc/honk/rules/`。这些配置片段需要先放到本地；它们声明的 .list 正文由核心远程下载。

下载出口默认 `🇭🇰 港台自动`，该组必须存在并可连接；可根据网络改为 direct 或其他可用组。首次没有有效缓存时，下载失败会拒绝启动；成功后保留最后有效缓存。更新失败不会替换当前规则。

自定义规则优先于公共 GeoSite/GeoIP 规则，列表顺序为 my-direct、my-proxy、my-ai；重叠条目以先匹配者为准。fallback 必须最后。通过 `/rules` 核对顺序，通过 `/providers/rules` 查看规则来源、条目数和更新时间；`PUT /providers/rules/{name}` 单独更新。公共分类仍使用 GeoSite/GeoIP 数据库，不支持直接加载 MRS。

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

生成器保留精确匹配、后缀及关键词的含义和顺序，同时生成 Honk 远程正文及配置引用。`🚀 节点选择`、`🤖 ChatGPT` 和下载组必须与 groups.dae 一致。配置片段不是完整配置，不要用仅合并 node 块的 LuCI 导入入口导入。