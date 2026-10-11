# 交易研习手册 · hanoptions.trade

纯静态网站，没有构建步骤：改完文件推到 `main` 分支即自动上线（GitHub Pages，Deploy from a branch → main / root）。

```
index.html        首页：五本手册的书架与目录
options/          美股期权课（index + ch01–ch16 + appendix；样式和脚本在 options/assets/）
psychology/       交易心理学（单页，章节用 #c0 … #c10 定位）
macro/            宏观交易框架（单页，#c0 … #c11）
policy/           政策叙事投资（单页，#c0 … #c11）
rebound/          超卖反弹清单 2026 年 9–10 月（单页，#c0 … #c23；数据截至 2026-10-09）
CNAME             自定义域名 hanoptions.trade，不要删
.build/           整理手册页面时用的脚本，网站本身不依赖它
```

- 线上地址：https://hanoptions.trade
- 想改某一章：直接编辑对应的 HTML 文件提交即可。
