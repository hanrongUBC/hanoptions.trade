# 交易研习手册 · hanoptions.trade

纯静态网站，没有构建步骤：改完文件推到 `main` 分支即自动上线（GitHub Pages，Deploy from a branch → main / root）。

```
index.html        首页：五本书摊在桌上，下面是每本的简介和目录（由 .build/build_home.py 生成）
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
- 想改首页（书名、简介、目录、封面颜色）：改 `.build/build_home.py` 里的 `BOOKS`，运行 `python3 .build/build_home.py` 重新生成 `index.html`。新增一本书时在 `BOOKS` 里加一项，并写一个封面图案函数。手册的章节目录会自动从各自的 HTML 里读取。
