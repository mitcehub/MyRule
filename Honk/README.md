# Honk 自定义补充规则

与本仓库 `Clash/`、`Singbox/` 对应，只维护自定义补充名单。公共域名、IP 分类继续使用单独更新的 GeoSite / GeoIP；机场订阅、节点和地区分组不放在这些规则文件里。

| 文件 | 内容 | 出站目标 |
| --- | --- | --- |
| `Direct.dae` | 自定义直连名单 | 内置 `direct` |
| `Proxy.dae` | 自定义代理名单 | `Proxy` 分组 |
| `AI.dae` | 自定义 AI 名单 | `ChatGPT` 分组 |

`Proxy`、`ChatGPT` 区分大小写，必须在主配置的 `group` 中定义。其他模板使用不同名称时，需要相应修改目标。

## 维护名单

以本仓库 `Clash/*.list` 为共同名单源，修改后在仓库根目录运行：

```sh
python scripts/generate_honk_rules.py
python scripts/generate_honk_rules.py --check
```

生成器保留 `DOMAIN`、`DOMAIN-SUFFIX`、`DOMAIN-KEYWORD` 的匹配含义和文件内顺序；遇到不支持的规则会报错，不会静默丢弃。生成的 `.dae` 应与名单一起提交，避免手动修改生成文件后被下次生成覆盖。这个脚本目前只生成 Honk 文件，不修改现有 Clash 和 Singbox 文件。

## 在 Honk 中使用

先把三份 `.dae` 下载到路由器 `/etc/honk/rules/`。将 `examples/local.dae`、`examples/public.dae` 作为局域网保护和公共分类的接入示例，核对分组和 Geo 分类后也放到该目录，再让主配置引用本地文件：

```dae
include {
    system.dae
    rules/local.dae
    rules/Direct.dae
    rules/Proxy.dae
    rules/AI.dae
    rules/public.dae
}
```

主配置只保留节点/订阅、分组、DNS 与上述 `include`，不要再留顶层 `routing` 块。路由器上实测，入口文件的规则会排在被引用文件之前，不能只靠将 `include` 写在文件开头来改变优先级。

所有顶层流量规则按上述顺序放进片段，实际顺序为“局域网保护 → 自定义直连 → 自定义代理 → 自定义 AI → 公共分类与兜底”。通过 Honk 的 `/rules` 接口复核最终顺序。移除主配置中重复的旧规则，但保留 `dns` 内的 DNS 路由。

示例引用的是 Honk 的 Geo 分类，并没有复制公共大规则的具体域名、IP 内容；公共库仍独立下载、更新。示例的分组和分类沿用本仓库作者的配置，使用其他模板时需要核对，不代表任何 Geo 数据库都包含所有标签。

这三份文件是 `include` 片段，不是完整配置，不要在 LuCI 的“导入配置”中逐个导入，否则现有导入器可能替换整块路由配置。

发布后的原始文件地址：

```text
https://raw.githubusercontent.com/mitcehub/MyRule/main/Honk/Direct.dae
https://raw.githubusercontent.com/mitcehub/MyRule/main/Honk/Proxy.dae
https://raw.githubusercontent.com/mitcehub/MyRule/main/Honk/AI.dae
```

`include` 读取本地文件，不会自行下载 HTTP 地址。更新时应先下载到临时目录，结合当前分组验证成功后再替换，并保留上一个可用版本。此次目录和生成器本身没有设置路由器定时更新，也没有添加 GitHub 自动提交工作流。

公共分类使用单独更新的 `geosite.dat` / `geoip.dat`。本目录不复制公共大规则，不解析 Clash `.mrs`，也不把机场链接或凭据提交到 GitHub。
