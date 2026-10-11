# 交易研习手册 · hanoptions.trade

纯静态网站，没有构建步骤：改完文件推到 `main` 分支即自动上线（GitHub Pages，Deploy from a branch → main / root）。

```
index.html        首页：五本书摊在桌上，下面是每本的简介和目录（由 .build/build_home.py 生成）
options/          美股期权课（index + ch01–ch16 + appendix；样式和脚本在 options/assets/）
psychology/       交易心理学（单页，章节用 #c0 … #c10 定位）
macro/            宏观交易框架（单页，#c0 … #c11）
policy/           政策叙事投资（单页，#c0 … #c11）
rebound/          超卖反弹清单 2026 年 9–10 月（单页，#c0 … #c23；数据截至 2026-10-09）
en/               英文版（由 .build/i18n.py 生成，不要手改；结构和中文版一一对应）
CNAME             自定义域名 hanoptions.trade，不要删
.build/           整理手册页面、生成首页和英文版的脚本，网站本身不依赖它
.i18n/            英文翻译：src/ 待译段落，en/ 译文，GUIDE.md 翻译规范与术语表
```

- 线上地址：https://hanoptions.trade
- 想改某一章：直接编辑对应的 HTML 文件提交即可。
- 想改首页（书名、简介、目录、封面颜色）：改 `.build/build_home.py` 里的 `BOOKS`，运行 `python3 .build/build_home.py` 重新生成 `index.html`。新增一本书时在 `BOOKS` 里加一项，并写一个封面图案函数。手册的章节目录会自动从各自的 HTML 里读取。

## 英文版

每一页右上角的 English / 中文 按钮在两种语言的同一页之间切换（单页手册会保留当前章节）。
浏览器语言不是中文的访客，第一次打开首页会自动进英文版；手动切换过以后按读者的选择。

改了中文内容之后更新英文版：

```
python3 .build/i18n.py extract          # 重新抽取段落；改过的段落会得到新的 id
python3 .build/i18n.py status           # 看哪些批次有缺失（missing）的段落
#   把缺失段落翻译后写进 .i18n/en/<批次>/ 的新 part 文件，按 .i18n/GUIDE.md 的格式
python3 .build/i18n.py check <批次>     # 逐批检查
python3 .build/site_i18n.py chinese     # 给中文页面补上 English 按钮（新增页面时）
python3 .build/i18n.py apply            # 生成 en/ 下的英文页面
python3 .build/build_home.py            # 重新生成中英文首页
```
