# -*- coding: utf-8 -*-
"""整合剧集榜单：统一字段 + 补中文译名/语言/地区"""
import json, re
from mapping import M as M_FILM
from mapping_tv import M_TV, EXACT_TV

P = json.load(open('parsed_tv.json', encoding='utf-8'))
RT = json.load(open('raw/tv_rt25_withyear.json', encoding='utf-8'))
MDL = json.load(open('raw/tv_mdl_parsed.json', encoding='utf-8'))
ACD = json.load(open('raw/tv_ac_details.json', encoding='utf-8'))
MC = json.load(open('raw/tv_mc.json', encoding='utf-8'))


def norm(s):
    s = (s or '').lower().strip()
    s = s.replace("'", "").replace("\u2019", "").replace(".", "").replace("-", "")
    s = re.sub(r"[^0-9a-z\u4e00-\u9fff\u3040-\u30ff]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


NM_FILM = {norm(k): v for k, v in M_FILM.items()}
NM_TV = {norm(k): v for k, v in M_TV.items()}


def lookup(title):
    if title in EXACT_TV:
        return EXACT_TV[title]
    n = norm(title)
    if n in NM_TV:
        return NM_TV[n]
    if n in NM_FILM:
        return NM_FILM[n]
    for sep in [" - ", ": ", " ("]:
        if sep in title:
            h = norm(title.split(sep)[0])
            if h in NM_TV:
                return NM_TV[h]
            if h in NM_FILM:
                return NM_FILM[h]
    return ("", "", "")


def clean_ac(t):
    t = re.sub(r'\s*-\s*S[ée]rie TV.*$', '', t or '')
    return t.strip()


rows = []


def add(platform, chart, rank, title_orig, title_cn, region, lang, year,
        score, votes, url, source_kind, note, score_scale):
    rows.append(dict(
        内容类型='剧集', 平台=platform, 榜单=chart, 排名=rank, 片名原文=title_orig,
        中文译名=title_cn, 原始语言=lang, 制片地区=region,
        上映年份=('' if year is None else str(year)),
        平台评分=('' if score is None else str(score)), 评分人数=votes,
        作品链接=url, 评分制=score_scale, 数据性质=source_kind, 备注=note))


# ===== 1. 豆瓣：官方剧集口碑榜 =====
for r in P['douban_tv']:
    region = r['region']
    lang = {'韩国': '韩语', '中国大陆': '汉语普通话', '中国香港': '粤语', '中国台湾': '汉语普通话',
            '美国': '英语', '英国': '英语', '日本': '日语', '泰国': '泰语'}.get(region, '')
    add('豆瓣电影 Douban', f"豆瓣{r['chart']}剧集口碑榜（取全部 {r['rank']}/10）", r['rank'],
        r['title_cn'], r['title_cn'], region, lang, r['year'], r['score'], r['votes'],
        r['url'], '官方榜单原文（周榜）',
        f"豆瓣「一周{r['chart']}口碑剧集榜」当期条目；豆瓣未设立剧集 Top 250 一类的固定总榜",
        '10 分制')

# ===== 2. IMDb Top 250 TV =====
for r in P['imdb_tv']:
    cn, lang, reg = lookup(r['title_orig'])
    span = f"，播出至 {r['end_year']}" if r.get('end_year') else ''
    add('IMDb', 'IMDb Top 250 TV Shows（取前 50）', r['rank'], r['title_orig'], cn, reg, lang,
        r['year'], r['score'], r['votes'], r['url'], '官方榜单原文',
        f"IMDb 剧集榜（含剧集/迷你剧/纪录片）{span}", '10 分制')

# ===== 3. Rotten Tomatoes：RT25 编辑部剧集榜 =====
for r in RT:
    cn, lang, reg = lookup(r['title'])
    add('Rotten Tomatoes 烂番茄', "RT25: Critics' Top TV Shows of the Last 25 Years（全部 25 条）",
        r['rank'], r['title'], cn, reg, lang, r['year'], r['critics'], None, r['url'],
        '官方榜单原文（RT 编辑部榜单）',
        f"Tomatometer＝专业影评人好评百分比 {r['critics']}%；另附观众 Popcornmeter {r['audience']}%；"
        f"RT 无全时段纯算法剧集榜，此为编辑部 25 周年榜单，共 25 条", '百分制')

# ===== 4. Metacritic Best TV Shows of All Time =====
for i, r in enumerate(MC[:50], 1):
    t = re.sub(r'^\d+\.\s*', '', r['title'])
    dm = re.search(r'[A-Z]{3} \d{1,2}, (\d{4})', r['txt'])
    date = re.search(r'([A-Z]{3} \d{1,2}, \d{4})', r['txt'])
    cn, lang, reg = lookup(t)
    add('Metacritic', 'Best TV Shows of All Time（Metascore 高→低，取前 50）', i, t, cn, reg, lang,
        dm.group(1) if dm else None, r['metascore'], None, r['href'], '官方榜单原文',
        f"榜单显示名次 {r['rank'].rstrip('.')}；平台标注北美首播日期 {date.group(1) if date else '—'}",
        '百分制')

# ===== 5. MyDramaList =====
for r in MDL:
    ym = re.search(r'(\d{4})', r['meta'])
    cn, lang, reg = lookup(r['title'])
    add('MyDramaList（MDL）', 'Top 100 Best K-Dramas（取前 50）', r['rank'], r['title'], cn,
        reg or '韩国', lang or '韩语', ym.group(1) if ym else None, r['score'], None, r['url'],
        '官方榜单原文', f"{r['meta']}｜榜单页仅公开评分，未公开评分人数", '10 分制')

# ===== 6. MyAnimeList（TV）=====
for r in P['mal_tv']:
    cn, lang, reg = lookup(r['title_orig'])
    add('MyAnimeList（MAL）', 'Top Anime（TV 类，取前 50）', r['rank'], r['title_orig'], cn,
        reg or '日本', lang or '日语', r['year'], r['score'], r['votes'], r['url'],
        '官方榜单原文', f"类型：{r['format']}｜放送：{r['air']}｜评分人数＝收藏该作品的会员数（members）",
        '10 分制')

# ===== 7. AniList（TV）=====
for r in P['anilist_tv']:
    cn, lang, reg = lookup(r['title_orig'])
    add('AniList', 'Anime（TV 格式）按 Average Score 降序（取前 50）', r['rank'], r['title_orig'],
        cn, reg or '日本', lang or '日语', r['year'], r['score'], r['users'], r['url'],
        '官方公开 GraphQL API 实时查询',
        f"英文名：{r['title_en']}｜原名：{r['title_native']}｜集数：{r['episodes']}｜人数＝收藏用户数（popularity）",
        '百分制')

# ===== 8. AlloCiné 最佳剧集 =====
for r in ACD:
    title = clean_ac(r['title'])
    ym = re.search(r'S[ée]rie TV\s+(\d{4})', r.get('title') or '')
    spec = r.get('spec')
    if spec:
        spec = spec.replace(',', '.')
    votes = None
    if r.get('votes'):
        try:
            votes = int(r['votes'])
        except Exception:
            votes = None
    cn, lang, reg = lookup(title)
    add('AlloCiné（法国）', 'Meilleures Séries TV de tous les temps（观众评分，取前 50）',
        r['rank'], title, cn, reg, lang, ym.group(1) if ym else None, spec, votes, r['url'],
        '官方榜单原文',
        f"法语/本地化片名：{title}｜评分＝观众评分（Spectateurs，5 分制），人数＝notes 数", '5 分制')

json.dump(rows, open('rows_tv.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
miss = sorted({r['片名原文'] for r in rows if not r['中文译名']})
noreg = sorted({r['片名原文'] for r in rows if not r['制片地区']})
print('剧集总行数:', len(rows))
print('缺中文译名:', len(miss))
open('tv_missing_cn.txt', 'w', encoding='utf-8').write('\n'.join(miss))
print('缺地区:', len(noreg))
open('tv_missing_region.txt', 'w', encoding='utf-8').write('\n'.join(noreg))
from collections import Counter
print(Counter(r['平台'] for r in rows))
