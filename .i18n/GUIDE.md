# hanoptions.trade — Chinese → English translation guide

The site is five self-study handbooks on US options and trading, written in Chinese. You are producing
the English edition that sits under `/en/`. Readers are English speakers learning to trade; many are
beginners. The English must read as if it were written in English by a careful author: plain, direct,
concrete, precise with numbers. Not a word-for-word gloss, and never more flowery than the original.

## Voice and style
- American English. Short, active sentences. Keep the author's concrete, slightly dry teaching voice.
- Translate meaning, not word order. Reorder clauses (and inline HTML elements) freely to make natural English.
- Do not add explanations, caveats or content that is not in the Chinese. Do not drop content either.
- Headings and labels in sentence case ("Delta and Gamma", "Three ways to read delta", "Before you trade").
- Second person ("you") where the Chinese addresses the reader.
- Chart labels, legend items, button text and table headers: short. A chart axis label must stay about as
  short as the Chinese ("股价（美元）" → "Stock price ($)").

## Typography and numbers
- Chinese punctuation → English punctuation: ，→ ,  。→ .  ：→ :  ；→ ;  （）→ ()  、→ ,  ？→ ?  ！→ !
  「」『』“” → “ ” (curly double quotes), ‘ ’ for quotes inside quotes. —— → — (em dash, no spaces).
  The ideographic space "　" → a normal space (or nothing, if it only separated words).
- Keep every number, ticker, price, percentage, date and formula exactly. Never round or change values.
- 万 / 亿: 14 万 → 140,000; 3.5 万 → 35,000; 12 亿美元 → $1.2 billion; 3000 亿 → 300 billion.
- Money: "120 美元" → "$120"; "每股 2.5 美元" → "$2.50 per share" only if the source shows cents; otherwise "$2.5 per share".
- Dates: "2026 年 10 月 9 日" → "October 9, 2026"; "10 月初" → "early October"; keep "9/30", "10/14" as they are.
- "第 4 章" → "Chapter 4"; "4.1" section numbers unchanged; "图 4.1" → "Figure 4.1"; "表 4.2" → "Table 4.2";
  "案例 1" → "Case 1"; "第一部分" → "Part 1"; "第一册" → "Volume 1".
- Units: "天" → "days", "笔" (trades) → "trades", "张" (contracts) → "contracts", "股" → "shares", "点" (vol points) → "vol points" / "points".
- "+0.35R", "2R", "Delta", "Gamma", "IV", "VIX", "SPY", "0DTE" stay as written.
- Use the minus sign "−" wherever the source uses it.

## Inline English glosses
The Chinese often gives the English term after a Chinese word:
`止损<span class="ek">（Stop-loss）</span>` or `快速变大（Gamma）`. In English, merge them: write just the English
term ("stop-loss"), and **delete the whole `<span class="ek">…</span>` element** and the parenthesis. The checker
allows `span.ek` to disappear. Keep a parenthetical only when it adds information (e.g. an abbreviation: "implied volatility (IV)").

## Segment kinds (the word after the id)
- `html` — inner HTML of one block element. Keep every tag and every attribute exactly (same href, class, id,
  data-*; same number of each tag). You may move inline elements to fit English word order. Translate only
  human-readable text, plus the values of title / alt / aria-label / placeholder / data-title if they are Chinese.
- `text` — a run of plain text between tags. Plain text out; entities like `&nbsp;` may stay.
- `attr` — an attribute value (title, aria-label, data-title, meta description, …). Plain text, no HTML.
- `js` — a JavaScript string shown to readers (chart labels, readouts, buttons). Plain text, keep any HTML tags
  it already has. Watch spacing: a JS string is often glued to numbers in code, e.g. `d + " 天"` → `" days"`
  (keep the leading space), `"第 " + n + " 章"` → `"Chapter "` and `""` style pieces. The `## code:` line shows the
  surrounding code so you can see how the piece is used. Leading/trailing spaces on the line are kept, so " days"
  keeps its space. If English needs nothing at all in that spot, write the token `<empty>` on the line.
- `tpl` — a JavaScript template literal. `{0}`, `{1}`, … stand for `${…}` expressions: keep each placeholder exactly
  once, move them where English grammar needs them. Keep every HTML tag/attribute it contains.

## Output format (strict)
For every batch you are given, read `.i18n/src/<batch>.txt` and write the translation into the directory
`.i18n/en/<batch>/` as one or more files `part-01.txt`, `part-02.txt`, … (write in chunks of ~80–120 segments so
no single write is huge; parts are read in name order). Each file contains only:

```
@@ <id> <kind>
<translation, may span several lines>
@@ <id> <kind>
<translation>
```

- Copy each `@@ <id> <kind>` header line exactly, in the same order as the source. Translate every segment.
- Do not copy the `## code:` / `## source:` comment lines. No other commentary in the files.
- Then run the checker and fix everything it reports, until it prints `0 problems, 0 unknown ids`:
  `cd /home/claude/hanoptions.trade && python3 .build/i18n.py check <batch>`

## Canonical titles (use exactly these wherever the title appears: <title>, headings, menus, cards, pager)
Site and series
- 交易研习手册 → Trading Study Handbooks · 研习手册 → study handbook · hanoptions.trade stays as is
- 美股期权课 → US Options Course · 交易心理学 → Trading Psychology · 宏观交易框架 → Macro Trading Framework
- 政策叙事投资 → Policy Narrative Investing · 超卖反弹清单（2026 年 9–10 月）→ Oversold Rebound List (Sep–Oct 2026)
- 课程首页 → Course home · 上一章 → Previous · 下一章 → Next · 返回 → Back · 完成 → Done · 回到课程首页 → Back to course home
- 本章目录 → In this chapter · 学完本章你能 → After this chapter you can · 前置知识 → Prerequisites · 本章约定 → Conventions
- 清单与自测 → Checklist and self-test · 自测 → Self-test · 开篇 → Opening · 导读 → Introduction · 附录 → Appendix

US Options Course (parts and chapters)
- 第一部分 基础 → Part 1 Foundations · 第二部分 核心变量 → Part 2 The core variables · 第三部分 策略 → Part 3 Strategies
- 第四部分 组合与风险管理 → Part 4 Portfolio and risk management · 第五部分 心性与进阶 → Part 5 Mindset and next steps · 附录 速查 → Appendix Quick reference
- 1 期权是什么，钱从哪里来 → What an option is, and where the money comes from
- 2 美股期权实务 → US options in practice
- 3 期权定价的直觉 → An intuition for option pricing
- 4 Delta 与 Gamma → Delta and gamma
- 5 Theta 与 Vega → Theta and vega
- 6 波动率 → Volatility
- 7 买方策略 → Strategies for buyers
- 8 卖方策略 → Strategies for sellers
- 9 中性与波动率策略 → Neutral and volatility strategies
- 10 事件交易 → Trading events
- 11 对冲与组合保护 → Hedging and portfolio protection
- 12 组合 Greeks 与调仓 → Portfolio Greeks and adjustments
- 13 期权的风险管理 → Risk management for options
- 14 系统与流程 → Systems and process
- 15 心理与常见死法 → Psychology and how accounts die
- 16 进阶方向与总结 → Where to go next, and a summary
- 附录：术语、速查与模板 → Appendix: glossary, quick reference and templates

Trading Psychology
- 导读：交易为什么是心理游戏 → Introduction: why trading is a mental game
- 概率思维：用一百笔交易看一笔交易 → Probabilistic thinking: judge one trade by a hundred
- 认知偏差：大脑的默认设置 → Cognitive biases: the brain's default settings
- 情绪与状态：当身体替你下单 → Emotion and state: when your body places the order
- 仓位即心理：正期望也会亏光 → Position size is psychology: a positive edge can still go to zero
- 纪律与规则：把决定提前做完 → Discipline and rules: make the decision before you need it
- 连胜与连败：随机性比你想象的更长 → Streaks: randomness runs longer than you think
- 独立判断：信息、叙事与跟单 → Independent judgment: information, narratives and copy trading
- 复盘：把亏损变成学费 → Review: turning losses into tuition
- 心性与生活：交易之外的那部分 → Temperament and life: the part outside trading
- 工具箱：清单、协议与自评 → Toolkit: checklists, protocols and self-assessment

Macro Trading Framework
- 导读：宏观交易在做什么 → Introduction: what macro trading is for
- 跨资产仪表盘：先看七个数字 → The cross-asset dashboard: seven numbers first
- 传导链与二阶思维 → Transmission chains and second-order thinking
- 利率、美联储与估值 → Rates, the Fed and valuation
- 美元、黄金与能源 → The dollar, gold and energy
- 市场体制：四个变量与三个阶段 → Market regimes: four variables, three phases
- 广度与轮动：指数的假象 → Breadth and rotation: the illusion of the index
- 资金流与期权结构 → Flows and options positioning
- 叙事与信息 → Narratives and information
- 日历、季节性与事件剧本 → Calendars, seasonality and event playbooks
- 从观点到交易 → From view to trade
- 工具箱：晨报、触发线与练习 → Toolkit: morning brief, trigger lines and exercises

Policy Narrative Investing
- 导读：交易政策，不交易口号 → Introduction: trade the policy, not the slogan
- 叙事评分：从口号到现金流 → Scoring narratives: from slogan to cash flow
- 先决定不碰什么：国家与市场 → First decide what to avoid: countries and markets
- 西半球与供应链重组 → The Western Hemisphere and supply-chain realignment
- 国防：战争会结束，备战不会 → Defense: wars end, preparing for them doesn't
- 资源独立：能源、关键矿产与黄金 → Resource independence: energy, critical minerals and gold
- 制造业回流与关税 → Reshoring and tariffs
- 人工智能、电力与机器人 → AI, power and robotics
- 民生主题：通胀分层、农业与医疗 → Household themes: uneven inflation, agriculture and healthcare
- 选举与政策周期 → Elections and policy cycles
- 执行：ETF、两组个股与期权工具 → Execution: ETFs, two stock baskets and options
- 工具箱：主题地图、叙事卡片与练习 → Toolkit: theme map, narrative cards and exercises

Oversold Rebound List
- 导读：这份清单从哪里来 → Introduction: where this list came from
- 方法：一家公司看三面 → Method: three angles on each company
- 总览：二十家放在一起 → Overview: all twenty side by side
- 工具箱：清单、模板与练习 → Toolkit: checklists, templates and exercises
- 基本面 / 消息面 / 技术面 → fundamentals / news / technicals
- Companies (ticker + English name): MCD McDonald's · WEN Wendy's · PEP PepsiCo · MDLZ Mondelez · HSY Hershey ·
  PRMB Primo Brands · LOW Lowe's · CMCSA Comcast · BAC Bank of America · BX Blackstone · VIK Viking Holdings ·
  MGM MGM Resorts · RTX RTX (Raytheon) · GD General Dynamics · WM Waste Management · JBHT J.B. Hunt ·
  SO Southern Company · DUK Duke Energy · SLB SLB (Schlumberger) · ABT Abbott Laboratories
- 群聊 → group chat · 交易者 → the trader · 买入价 → entry price

## Glossary (use consistently)
期权 option · 看涨/认购 call · 看跌/认沽 put · 权利金 premium · 行权价 strike · 到期日 expiration · 到期 expiry ·
标的 underlying · 合约 contract · 平值/实值/虚值 at-the-money (ATM) / in-the-money (ITM) / out-of-the-money (OTM) ·
内在价值 intrinsic value · 时间价值 time value · 行权 exercise · 指派 assignment · 美式/欧式 American-style / European-style ·
买卖权平价 put–call parity · 盈亏平衡点 breakeven · 到期盈亏图 payoff diagram at expiry ·
希腊字母 the Greeks · 等效股数 share equivalent · Beta 加权 beta-weighted · 二阶希腊字母 second-order Greeks ·
隐含波动率 implied volatility (IV) · 实际/历史波动率 realized / historical volatility · 波动率风险溢价 volatility risk premium ·
期限结构 term structure · 偏度 skew · 波动率微笑 volatility smile · IV 崩塌 IV crush · 预期变动 expected move ·
跨式 straddle · 宽跨式 strangle · 铁鹰 iron condor · 蝶式 butterfly · 日历价差 calendar spread · 对角价差 diagonal spread ·
垂直价差 vertical spread · 借记价差 debit spread · 信用价差 credit spread · 备兑开仓 covered call ·
现金担保卖沽 cash-secured put · 轮子策略 the wheel · 保护性看跌 protective put · 领口 collar · 看跌价差保护 put-spread hedge ·
尾部风险 tail risk · 尾部预算 tail-hedge budget · LEAPS LEAPS · 滚仓 roll · 平仓 close the position · 开仓 open ·
保证金 margin · 保证金追缴 margin call · 账户 account · 仓位 position (size) · 杠杆 leverage · 爆仓 blow up the account ·
胜率 win rate · 盈亏比 payoff ratio · 期望值 expectancy · 回撤 drawdown · 连败 losing streak · 止损 stop-loss ·
交易日志 trading journal · 复盘 review · 做市商 market maker · 流动性 liquidity · 买卖价差 bid–ask spread ·
限价单/市价单 limit order / market order · 财报 earnings (report) · 财报季 earnings season ·
美联储 the Fed · 降息/加息 rate cut / rate hike · 美债收益率 Treasury yield · 收益率曲线 yield curve · 倒挂 inversion ·
通胀 inflation · 就业 jobs / employment · 美元指数 dollar index (DXY) · 广度 breadth · 轮动 rotation · 体制 regime ·
资金流 flows · 叙事 narrative · 主题投资 thematic investing · 关税 tariffs · 供应链 supply chain · 制造业回流 reshoring ·
关键矿产 critical minerals · 国防 defense · 超卖 oversold · 反弹 rebound · 均线/50 日线 50-day moving average ·
200 日线 200-day moving average · 远期市盈率 forward P/E · 股息率 dividend yield · 下次财报 next earnings
