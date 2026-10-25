# 全球影视评分平台榜单汇总 · Global Film & TV Ranking Dashboard

**2654 条高分影剧记录**（电影 1400 + 剧集 1254），来自 **8 个全球公认的第三方评分平台**的官方**全时段总榜**，外加 **TMDB 20 国/地区高分榜**（电影 1000 + 剧集 929）。

一个文件，双击即用：海报墙浏览、已看打卡、我的评分与短评、跨平台自动同步、手机电脑自适应。

- 🌐 在线体验：见仓库 About 区域的 Website 地址（GitHub Pages）
- 📦 离线使用：下载 `index.html`，双击用浏览器打开即可

---

## 一、收录了哪些平台

| 平台 | 所属国家/地区 | 本次采用榜单 | 评分制 | 收录/总量 |
|---|---|---|---|---|
| 豆瓣 Douban | 中国 | 豆瓣电影 Top 250 | 10 分制 | 50 / 250 |
| IMDb | 美国（Amazon 旗下） | IMDb Top 250 | 10 分制 | 50 / 250 |
| Rotten Tomatoes | 美国（Fandom 旗下） | 300 Best Movies of All Time | 百分制 | 50 / 300 |
| Metacritic | 美国（Fandom 旗下） | Best Movies of All Time（Metascore 排序） | 百分制 | 50 / 17,434 |
| Letterboxd | 新西兰 | 官方 Top 500 Films | 5 分制 | 50 / 500 |
| MyAnimeList | 美国（母公司日本 MediaDo） | Top Anime | 10 分制 | 50 / 50 |
| AniList | 美国（社区运营） | Anime 按 Average Score 降序 | 百分制 | 50 |
| AlloCiné | 法国（Webedia 旗下） | Les 300 meilleurs films | 5 分制 | 50 / 300 |

**剧集**（7 个平台，325 条）：IMDb Top 250 TV（50）、Rotten Tomatoes RT25（25）、Metacritic Best TV Shows（50）、MyDramaList Top 100 K-Dramas（50）、MyAnimeList Top Anime type=tv（50）、AniList format=TV（50）、AlloCiné Meilleures Séries（50）。

### 附：TMDB 20 国/地区高分榜（1929 条）

用 TMDB 官方 API 按「制片国家/地区」筛选后按平均分降序，每个国家各取 **电影 50 部 + 剧集 50 部**（评分人数门槛按各国体量分别设定，避免小众语言片被零票高分刷榜）。

| 国家/地区 | 电影 | 剧集 | 国家/地区 | 电影 | 剧集 |
|---|---|---|---|---|---|
| 俄罗斯 | 50 | 50 | 泰国 | 50 | 50 |
| 德国 | 50 | 50 | 瑞典 | 50 | 50 |
| 西班牙 | 50 | 50 | 丹麦 | 50 | 50 |
| 意大利 | 50 | 50 | 伊朗 | 50 | 21 |
| 英国 | 50 | 50 | 波兰 | 50 | 50 |
| 法国 | 50 | 50 | 巴西 | 50 | 50 |
| 日本 | 50 | 50 | 墨西哥 | 50 | 50 |
| 韩国 | 50 | 50 | 澳大利亚 | 50 | 50 |
| 印度 | 50 | 50 | 中国香港 | 50 | 8 |
| 中国大陆 | 50 | 50 | 中国台湾 | 50 | 50 |

**必须说明的口径**：TMDB 是**全球用户**打分，所以「俄罗斯高分榜」代表的是**全球观众对俄罗斯电影的评价**，并不等于俄罗斯本土观众口味（本土口味要看 Kinopoisk，该站需俄罗斯手机号/社交账号登录，无法公开采集）。朝鲜没有任何公开的影视评分平台，故未收录。

> 收录原则：仅第三方评分机构/评分社区；排除流媒体自有榜单（腾讯视频、爱奇艺、优酷等）与播放量排行；**只收全时段总榜，周榜/年度榜一律不收**；榜单本身不足 50 条时按实际条数收录，不做推测补齐。

## 二、功能

1. **海报墙 / 表格双视图**：随手翻海报，或进表格对比排序
2. **已看打卡 ✓**：右上角打钩，顶部圆环自动统计观影进度
3. **我的评分**：五星制，支持半星（＝1–10 分）
4. **一句短评**：随时记下观后感
5. **跨平台自动同步**：同一部作品在豆瓣勾了，IMDb / 烂番茄 / Metacritic 那边同步变绿（评分、短评同理），不用标第二遍
6. **筛选 / 搜索 / 排序 / 去重**：按电影剧集、平台、年份、地区检索，一键跨平台去重
7. **夜间模式 + 手机适配**
8. **本地存储 + 导出备份**：数据只存在你自己的浏览器，可导出 JSON

## 三、数据口径（重要）

**数据性质分三类**
- **官方榜单原文**：豆瓣、IMDb、Rotten Tomatoes、Metacritic、Letterboxd、MyDramaList、MyAnimeList、AlloCiné —— 排名/片名/评分/评分人数直接取自榜单页
- **官方公开 API 实时查询**：AniList（官方 GraphQL）
- **人工整理 / 翻译**：① 中文译名 ② 原始语言与制片地区 ③ 「折算/10」列

**评分制差异**
- 百分制：Metacritic Metascore（影评加权分）、Rotten Tomatoes Tomatometer（影评人好评百分比）、AniList Average Score（用户加权分折算）—— 三者含义完全不同
- 10 分制：豆瓣、IMDb、MyAnimeList、MyDramaList
- 5 分制：Letterboxd、AlloCiné 观众评分
- 「折算/10」＝线性换算（百分制÷10、5 分制×2），**仅便于排序浏览，不代表各平台分数等价**

**已知局限 / 诚实声明**
- **豆瓣没有剧集固定总榜**（不存在「剧集 Top 250」，只有每周更新的口碑周榜），所以剧集部分没有收录豆瓣 —— 不拿周榜凑数
- **Rotten Tomatoes 没有全时段算法榜**：电影用编辑部《300 Best Movies》，剧集用编辑部《RT25》—— 后者本身只有 25 条，按实际收录
- 评分人数口径不统一：豆瓣是打票数，MAL / AniList 是收藏人数，烂番茄 / Metacritic / Letterboxd 不公开
- Metacritic 榜单页标注北美上映/首播日期，部分老片与首映年份不同
- TMDB 国别榜是**全球用户评分**，不等于该国本土观众口味；部分小语种地区的剧集在 TMDB 上票数极少，中国香港剧集仅 8 条、伊朗剧集 21 条满足门槛，按实际条数收录
- **朝鲜**无公开影视评分平台，未收录
- 封面图仅作辨识辅助，版权归各平台/版权方所有；匹配不上时显示占位色块，不做猜测

## 四、文件结构

```
index.html                      成品页面（含全部数据，可离线打开）
data/
  rows_final.json               电影 400 条结构化数据
  rows_tv.json                  剧集 325 条结构化数据
  poster_cache.json             封面图地址缓存（IMDb 官方图片服务）
  tmdb_rows.json                TMDB 20 国/地区 1929 条
scripts/
  generate_html.py              用 template.html + data 生成 index.html
  template.html                 页面模板（样式与交互都在这里）
  fetch_posters.py              纯 HTTP 抓取封面（IMDb 官方图片服务）
  fetch_tmdb.js                 TMDB 国别榜抓取（需自备 api key，写到 .tmdb_key.txt）
  topup_tmdb.js                 条数不足 50 的国别榜降门槛补抓
  build_dataset2.py             电影榜单原始数据构建
  build_tv_dataset.py           剧集榜单原始数据构建
  mapping.py / mapping_tv.py    译名、语言、地区、评分折算映射
gh_push_contents.py             用 GitHub contents API 推送本仓库（令牌放 .gh_token.txt）
```

重新生成：`cd scripts && python generate_html.py`（会同时输出到仓库根目录和桌面）

## 五、免责声明

排名、评分、评分人数与封面图版权归各平台及其版权方所有，本项目仅作个人检索与学习之用，不用于任何商业用途。各平台榜单会随时间变化，请以官方页面为准。

## 六、License

MIT License
