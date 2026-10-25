# -*- coding: utf-8 -*-
"""生成最终交付物：单一可交互 HTML（电影 + 剧集）。
数据：rows_final.json（电影）/ rows_tv.json（剧集，已剔除豆瓣剧集周榜）
封面：poster_cache.json（IMDb 官方图片服务，纯 HTTP 抓取）
"""
import json, os

BASE = os.path.dirname(os.path.abspath(__file__))
# 数据文件：同目录下，或上游 data/ 目录（GitHub 仓库布局）
ROOT = os.path.dirname(BASE) if os.path.basename(BASE) == 'scripts' else BASE
_cands = (os.path.join(BASE, 'data'), os.path.join(ROOT, 'data'), BASE)
DATA = next((c for c in _cands if os.path.isdir(c)), BASE)
DESKTOP = r'D:\系统文件夹\桌面'      # 成品同时放一份在桌面，方便查找
OUT = ROOT
os.makedirs(OUT, exist_ok=True)

movie_rows = json.load(open(os.path.join(DATA, 'rows_final.json'), encoding='utf-8'))
tv_rows = json.load(open(os.path.join(DATA, 'rows_tv.json'), encoding='utf-8'))
for r in movie_rows:
    r['内容类型'] = '电影'
rows = movie_rows + tv_rows
# 豆瓣没有剧集固定总榜（只有周榜），按要求不收录
rows = [r for r in rows if not (r['内容类型'] == '剧集' and str(r['平台']).startswith('豆瓣'))]

POSTERS = json.load(open(os.path.join(DATA, 'poster_cache.json'), encoding='utf-8'))

# TMDB 各国/地区高分榜（可选数据，由 github/fetch_tmdb.js 抓取后放进 data/tmdb_rows.json）
TMDB_FILE = os.path.join(DATA, 'tmdb_rows.json')
tmdb_rows, TMDB_META = [], []
if os.path.exists(TMDB_FILE):
    _tj = json.load(open(TMDB_FILE, encoding='utf-8'))
    TMDB_META = _tj.get('meta', [])
    for r in _tj.get('rows', []):
        tmdb_rows.append(dict(内容类型=r['k'], 平台=r['p'], 榜单=r['ch'], 排名=r['r'], 片名原文=r['t'],
                              中文译名=r['cn'], 原始语言=r['lang'], 制片地区=r['reg'], 上映年份=str(r['y']),
                              平台评分=str(r['sc']), 评分人数=r['v'], 作品链接=r['u'], 评分制=r['sca'],
                              数据性质=r['nat'], 备注=r['rm'], _img=r.get('img', '')))
    print('TMDB 国别榜：%d 个国家/地区，%d 条' % (len(TMDB_META), len(tmdb_rows)))
rows = rows + tmdb_rows
FETCH_TIME = "2026-10-24 19:40 – 21:20（UTC+8）"

# ---------------- 平台：短名 / 所属国家 ----------------
SHORT = {'豆瓣电影 Douban': '豆瓣', 'IMDb': 'IMDb', 'Rotten Tomatoes 烂番茄': 'Rotten Tomatoes',
         'Metacritic': 'Metacritic', 'Letterboxd': 'Letterboxd', 'MyAnimeList（MAL）': 'MyAnimeList',
         'MyAnimeList': 'MyAnimeList', 'AniList': 'AniList', 'AlloCiné（法国）': 'AlloCiné',
         'MyDramaList（MDL）': 'MyDramaList'}
COUNTRY = {
    '豆瓣': ('中国', '华语圈最大影迷评分社区'),
    'IMDb': ('美国', 'Amazon 旗下'),
    'Rotten Tomatoes': ('美国', 'Fandom 旗下'),
    'Metacritic': ('美国', 'Fandom 旗下'),
    'Letterboxd': ('新西兰', '总部奥克兰'),
    'MyAnimeList': ('美国', '母公司为日本 MediaDo'),
    'AniList': ('美国', '社区运营'),
    'AlloCiné': ('法国', 'Webedia 旗下'),
    'MyDramaList': ('美国', '运营方 Daebak Media LLC'),
}

PLATFORMS = [
 # ===== 电影 =====
 dict(k='电影', p='豆瓣', ch='豆瓣电影 Top 250', u='https://movie.douban.com/top250',
      sc='10 分制', src='注册用户打分（加权平均分）', cnt='50 / 250',
      f='华语圈最具影响力的影迷评分榜，口味偏文艺与经典，华语片占比高；入榜需达到平台票数门槛。'),
 dict(k='电影', p='IMDb', ch='IMDb Top 250', u='https://www.imdb.com/chart/top/',
      sc='10 分制', src='注册用户打分（贝叶斯加权 Top 250）', cnt='50 / 250',
      f='全球最知名的影迷评分榜，用加权评分（WR）抵消小众片刷分；偏英语片与男性向经典；需 ≥25,000 票。'),
 dict(k='电影', p='Rotten Tomatoes', ch='300 Best Movies of All Time',
      u='https://editorial.rottentomatoes.com/guide/best-movies-of-all-time/',
      sc='百分制（Tomatometer %）', src='专业影评人好评率 + 观众 Popcornmeter + 编辑人工调整',
      cnt='50 / 300', f='RT 编辑部榜单：先看影评人新鲜度，再叠加观众票、评论数与年份排序，并有编辑人工微调；必须 Certified Fresh。'),
 dict(k='电影', p='Metacritic', ch='Best Movies of All Time（按 Metascore 排序）',
      u='https://www.metacritic.com/browse/movie/all/all/all-time/metascore/',
      sc='百分制（Metascore）', src='专业影评人评分加权换算的 0–100 分', cnt='50 / 17,434',
      f='纯专业影评聚合，100 分档存在大量并列；页面标注北美上映日期，部分老片与首映年份不同。'),
 dict(k='电影', p='Letterboxd', ch='Letterboxd 官方 Top 500 Films',
      u='https://letterboxd.com/official/list/letterboxds-top-500-films/',
      sc='5 分制（加权平均分）', src='注册用户打分', cnt='50 / 500',
      f='影迷社区口味最「迷影」的一档，日本 / 苏联 / 欧洲艺术片权重明显高于好莱坞商业片；榜单页不公开评分人数。'),
 dict(k='电影', p='MyAnimeList', ch='Top Anime', u='https://myanimelist.net/topanime.php',
      sc='10 分制', src='注册用户打分（加权平均分）', cnt='50 / 50',
      f='全球最大动画数据库，本榜含 TV / OVA / 剧场版；评分人数＝收藏该作品的会员数（members）。'),
 dict(k='电影', p='AniList', ch='Anime 按 Average Score 降序', u='https://anilist.co/search/anime/top-rated',
      sc='百分制（Average Score 0–100）', src='注册用户打分（官方 GraphQL API 实时查询）', cnt='50',
      f='现代动画社区，评分用 0–100 的 Average Score；通过官方公开 API 实时排序查询，人数＝收藏用户数。'),
 dict(k='电影', p='AlloCiné', ch='Les 300 meilleurs films de tous les temps',
      u='https://www.allocine.fr/film/meilleurs/', sc='5 分制（观众评分）', src='法国观众打分（Spectateurs）',
      cnt='50 / 300', f='法语区最大影视平台，代表欧洲法语观众口味；另有「媒体评分（Presse）」与观众评分两套。'),
 # ===== 剧集 =====
 dict(k='剧集', p='IMDb', ch='IMDb Top 250 TV Shows', u='https://www.imdb.com/chart/toptv/',
      sc='10 分制', src='注册用户打分（加权评分）', cnt='50 / 250',
      f='全球剧集榜，含连续剧、迷你剧与纪录片系列；采用加权评分，票数门槛低于电影榜。'),
 dict(k='剧集', p='Rotten Tomatoes', ch="RT25: Critics' Top TV Shows of the Last 25 Years",
      u='https://editorial.rottentomatoes.com/guide/rt25-critics-top-tv-shows-of-the-last-25-years-2/',
      sc='百分制（Tomatometer %）', src='影评人投票评选 + Tomatometer 好评率', cnt='25 / 25（榜单本身仅 25 条）',
      f='RT 25 周年编辑部榜单，由影评人投票选出近 25 年最佳剧集。RT 没有全时段纯算法剧集榜，故只收录 25 条，不做补齐。'),
 dict(k='剧集', p='Metacritic', ch='Best TV Shows of All Time（按 Metascore 排序）',
      u='https://www.metacritic.com/browse/tv/all/all/all-time/metascore/',
      sc='百分制（Metascore）', src='专业影评人评分加权换算的 0–100 分', cnt='50',
      f='按 Metascore 高低排列的剧集总榜，含纪录片与自然类系列；页面标注北美首播日期。'),
 dict(k='剧集', p='MyDramaList', ch='Top 100 Best K-Dramas', u='https://mydramalist.com/shows/top_korean_dramas',
      sc='10 分制', src='注册用户打分（加权平均分）', cnt='50 / 100',
      f='亚洲剧集最大数据库与评分社区，本榜为韩剧总榜（非年度榜）；榜单页未公开评分人数，该列留空。'),
 dict(k='剧集', p='MyAnimeList', ch='Top Anime（TV 类）', u='https://myanimelist.net/topanime.php?type=tv',
      sc='10 分制', src='注册用户打分（加权平均分）', cnt='50 / 50',
      f='限定 TV 放送动画（type=tv），不含 OVA / 剧场版 / 特别篇。'),
 dict(k='剧集', p='AniList', ch='Anime（TV 格式）按 Average Score 降序', u='https://anilist.co/search/anime/top-rated',
      sc='百分制（Average Score 0–100）', src='注册用户打分（官方 GraphQL API，format=TV）', cnt='50',
      f='限定 format=TV 的动画剧集，不含电影 / OVA；通过官方公开 API 实时查询。'),
 dict(k='剧集', p='AlloCiné', ch='Meilleures Séries TV de tous les temps',
      u='https://www.allocine.fr/series/meilleures/', sc='5 分制（观众评分）', src='法国观众打分（Spectateurs）',
      cnt='50 / 300', f='法语区观众口味的剧集总榜，含法剧与美英剧（以法语 / 本地化片名展示）。'),
]
# ---------------- TMDB 国别榜：补平台卡片 ----------------
for m in TMDB_META:
    co = m['cn']
    name = 'TMDB·' + co
    kind = m.get('kind', '电影')
    COUNTRY[name] = (co, 'TMDB 数据源')
    PLATFORMS.append(dict(
        k=kind, p=name, ch=co + ('剧集高分榜' if kind == '剧集' else '影片高分榜'),
        u='https://www.themoviedb.org/' + ('tv' if kind == '剧集' else 'movie') +
          '?language=zh-CN&with_origin_country=' + m['code'],
        sc='10 分制', src='TMDB 注册用户打分（平均分）', cnt='%d / 全站' % m['n'],
        f='数据源 TMDB（美国，全球用户评分）：筛选「制片国家＝%s、评分人数≥%d」后按平均分降序取前 %d 条。'
          '代表全球观众对该国%s的评价，不等同于该国本土观众口味；中文译名取自 TMDB 中文站。'
          % (co, m['min'], m['n'], '剧集' if kind == '剧集' else '影片')))

for p in PLATFORMS:
    co, note = COUNTRY.get(p['p'], (p['p'], ''))
    p['co'] = co
    p['n'] = f"{p['p']}（{co}）"
    p['org'] = note

N_MOVIE = sum(1 for r in rows if r['内容类型'] == '电影')
N_TV = sum(1 for r in rows if r['内容类型'] == '剧集')
TOTAL = len(rows)
N_IMG = 0


def conv10(score, scale):
    try:
        v = float(str(score).replace(',', '.'))
    except Exception:
        return 0
    s = str(scale)
    if '百分' in s:
        return round(v / 10, 2)
    if '5 分' in s:
        return round(v * 2, 2)
    return round(v, 2)


data = []
for r in rows:
    p = SHORT.get(str(r['平台']), str(r['平台']))
    _id = '|'.join([r['内容类型'], str(r['平台']), str(r['片名原文']), str(r.get('上映年份') or '')])
    img = (POSTERS.get(_id) or {}).get('img') or r.get('_img', '')
    if img:
        N_IMG += 1
    try:
        v = int(str(r.get('评分人数') or '').replace(',', '')) or 0
    except Exception:
        v = 0
    data.append(dict(id=_id, k=r['内容类型'], p=p, ch=str(r['榜单']).replace('（取前 50）', '').replace('（全部 25 条）', ''),
                     r=int(r['排名']), t=r['片名原文'], cn=r['中文译名'], lang=r['原始语言'], reg=r['制片地区'],
                     y=str(r.get('上映年份') or ''), sc=str(r['平台评分']), v=v, u=r['作品链接'],
                     sca=r['评分制'], nat=r['数据性质'], rm=r['备注'],
                     n10=conv10(r['平台评分'], r['评分制']), img=img or ''))

plat = [dict(k=p['k'], p=p['p'], n=p['n'], co=p['co'], org=p['org'], ch=p['ch'], sc=p['sc'],
             src=p['src'], cnt=p['cnt'], f=p['f'], u=p['u']) for p in PLATFORMS]

NP_MOVIE = len({p['p'] for p in PLATFORMS if p['k'] == '电影'})
NP_TV = len({p['p'] for p in PLATFORMS if p['k'] == '剧集'})
N_COUNTRY = len({p['co'] for p in PLATFORMS})
STAT = json.dumps([
    ('收录条目', f'{TOTAL}'), ('电影', f'{N_MOVIE}'), ('剧集', f'{N_TV}'),
    ('电影榜单', f'{NP_MOVIE} 个'), ('剧集榜单', f'{NP_TV} 个'), ('覆盖国家/地区', f'{N_COUNTRY}'),
    ('评分制', '10 分制 / 百分制 / 5 分制'), ('封面命中', f'{N_IMG} / {TOTAL}'),
], ensure_ascii=False)
STAT_HTML = ''.join(f'<div><b>{b}</b>{a}</div>' for a, b in json.loads(STAT))

# TMDB 国别榜相关说明：仅在真的接入了该数据时才出现，避免回退后残留
_T1 = ('TMDB 通过其官方 API 按「制片国家 + 评分人数门槛 + 平均分降序」生成各国 / 地区影片榜与剧集榜'
       '（TMDB·俄罗斯、TMDB·德国 …），中文片名与封面直接取自 TMDB 中文站与官方图床。') if TMDB_META else ''
_T2 = '、TMDB（各国 / 地区影片榜与剧集榜）' if TMDB_META else ''
_T3 = ('<li><b>TMDB 国别榜的口径要特别注意</b>：它是「制片国家＝该国 + 全球 TMDB 用户评分」筛出来的高分作品，'
       '<b>代表全球观众对该国作品的评分，不等于该国本土观众的口味</b>；各国本土平台（俄罗斯 Кинопоиск、'
       '日本 Filmarks、德国 Moviepilot、西班牙 FilmAffinity 等）需要登录或在本机网络下被拦截，故未收录。</li>'
       ) if TMDB_META else ''

NOTES = f"""
<h4 style="margin:10px 0 4px;color:var(--ink)">数据获取方式</h4>
<ul>
<li><b>榜单正文</b>：抓取时间 {FETCH_TIME}。静态 HTTP 抓取（豆瓣 Top 250、MyAnimeList、MyDramaList、AlloCiné 榜单页与详情页）；
对有人机验证 / 纯前端渲染的站点（IMDb、Metacritic、Rotten Tomatoes 编辑部榜、Letterboxd）用真实浏览器渲染后读取页面内嵌数据。</li>
<li><b>官方公开 API</b>：AniList 通过其官方 GraphQL 接口（graphql.anilist.co）按 averageScore 降序实时查询，电影与 TV 各 50 条；{_T1}</li>
<li><b>封面图</b>：通过 IMDb 官方图片服务按「片名 + 年份 + 类型」匹配，命中 {N_IMG}/{TOTAL} 条；标题必须实质匹配（同词 / 包含 / 年份吻合）才采用，未命中显示占位色块，不使用猜测图。</li>
<li><b>工具</b>：Python（urllib / JSON 解析 / 并发抓取）、Playwright + Edge（受限站点渲染）、openpyxl 与自写模板生成交付文件。</li>
</ul>
<h4 style="margin:12px 0 4px;color:var(--ink)">数据性质区分</h4>
<ul>
<li><b>官方榜单原文</b>：豆瓣、IMDb、Rotten Tomatoes、Metacritic、Letterboxd、MyDramaList、MyAnimeList、AlloCiné —— 排名 / 片名 / 评分 / 评分人数直接来自榜单页或官方接口。</li>
<li><b>官方公开 API 实时查询</b>：AniList（GraphQL）{_T2}。</li>
<li><b>人工整理 / 翻译</b>：① 中文译名；② 原始语言与制片地区；③ 「折算/10」列（百分制÷10、5 分制×2 的线性换算，仅便于跨平台排序，<b>不等于各平台分数等价</b>）。</li>
</ul>
<h4 style="margin:12px 0 4px;color:var(--ink)">评分制差异</h4>
<ul>
<li><b>百分制</b>：Metacritic Metascore（影评加权分）、Rotten Tomatoes Tomatometer（影评人好评百分比）、AniList Average Score（用户加权分折算）——三者含义完全不同。</li>
<li><b>10 分制</b>：豆瓣、IMDb、MyAnimeList、MyDramaList。</li>
<li><b>5 分制</b>：Letterboxd、AlloCiné 观众评分。</li>
</ul>
<h4 style="margin:12px 0 4px;color:var(--ink)">收录原则与已知局限</h4>
<ul>
<li>仅收录第三方评分 / 评分机构类平台的公开榜单；已排除流媒体自有榜单（腾讯视频、爱奇艺、优酷等）与播放量排行。</li>
<li>每平台每榜取前 50 条；榜单本身不足 50 条时按实际条数收录并标注，<b>不用推测数据补齐</b> —— 目前仅 Rotten Tomatoes 剧集榜（RT25，25 条）属于此情况。</li>
<li><b>豆瓣没有剧集固定总榜</b>（不存在「剧集 Top 250」一类榜单，只有每周更新的口碑周榜），因此剧集部分不收录豆瓣，避免把当期周榜当成历史总榜。</li>
<li>Rotten Tomatoes 无全时段纯算法榜：电影为编辑部《300 Best Movies of All Time》，剧集为编辑部《RT25》。</li>
<li>Letterboxd 不对未登录用户开放「全站按评分排序」浏览页，电影部分采用其官方账号维护的 Top 500；该平台不提供剧集榜单。</li>
<li>Metacritic 榜单页标注北美上映 / 首播日期，部分老片与首映年份不同。MyDramaList 榜单页未公开评分人数，该列留空。</li>
<li>所有榜单均为「全时段总榜」类（按评分 / 影评排序），不收录年度榜、周榜等时效性榜单。</li>
{_T3}
<li>朝鲜等国家 / 地区不存在公开评分数据（无民用互联网评分平台），因此无法收录，也不会编造。</li>
</ul>
"""

tpl = open(os.path.join(BASE, 'template.html'), encoding='utf-8').read()
sub = (f'抓取 / 查询时间 {FETCH_TIME}　·　共 {TOTAL} 条（电影 {N_MOVIE} + 剧集 {N_TV}）'
       f'　·　排名·评分·评分人数为平台榜单原文，中文译名与地区为人工整理')
html = (tpl.replace('__DATA__', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
           .replace('__PLAT__', json.dumps(plat, ensure_ascii=False, separators=(',', ':')))
           .replace('__STAT__', json.dumps(STAT_HTML, ensure_ascii=False))
           .replace('__NOTES__', NOTES)
           .replace('__SUB__', sub)
           .replace('__TOTAL__', str(TOTAL)))

path = os.path.join(OUT, 'index.html')
open(path, 'w', encoding='utf-8').write(html)
print('HTML ->', path)
if os.path.isdir(DESKTOP):
    dpath = os.path.join(DESKTOP, '全球影视评分平台榜单汇总.html')
    open(dpath, 'w', encoding='utf-8').write(html)
    print('COPY ->', dpath)
print('rows:', TOTAL, '| movie:', N_MOVIE, '| tv:', N_TV, '| posters:', N_IMG)
