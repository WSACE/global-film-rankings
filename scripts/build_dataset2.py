# -*- coding: utf-8 -*-
"""最终整合：统一字段 + 补中文译名/语言/地区"""
import json, re, csv, os
from mapping import M

FETCH_TIME = "2026-10-24 19:40 – 20:35（UTC+8）"

S = json.load(open('parsed_static.json', encoding='utf-8'))
E = json.load(open('raw/extracted.json', encoding='utf-8'))
D = json.load(open('raw/details.json', encoding='utf-8'))
AC = json.load(open('raw/ac_details2.json', encoding='utf-8'))
MC = json.load(open('raw/mc2.json', encoding='utf-8'))

# 精确匹配优先（用于标点敏感、归一化后会冲突的片名）
EXACT = {
 "Gintama": ("银魂", "日语", "日本"),
 "La Bataille de Gaulle - partie 1 : L'Âge de Fer": ("高卢之战 第一部：铁器时代", "法语", "法国"),
 "Gintama'": ("银魂'", "日语", "日本"),
 "Gintama'": ("银魂'", "日语", "日本"),
 "Gintama°": ("银魂°", "日语", "日本"),
 "Gintama.": ("银魂.", "日语", "日本"),
 "Gintama': Enchousen": ("银魂' 延长战", "日语", "日本"),
 "Gintama. Shirogane no Tamashii-hen": ("银魂. 银之魂篇", "日语", "日本"),
 "Gintama. Shirogane no Tamashii-hen - Kouhan-sen": ("银魂. 银之魂篇（后半战）", "日语", "日本"),
 "Gintama.: Shirogane no Tamashii-hen - Kouhan-sen": ("银魂. 银之魂篇（后半战）", "日语", "日本"),
 "Gintama: THE FINAL": ("银魂 THE FINAL", "日语", "日本"),
 "Gintama: The Final": ("银魂 THE FINAL", "日语", "日本"),
 "Gintama Movie 2: Kanketsu-hen - Yorozuya yo Eien Nare": ("银魂 完结篇：直到万事屋永远", "日语", "日本"),
 "Gintama: Kanketsu-hen - Yorozuya yo Eien Nare": ("银魂 完结篇：直到万事屋永远", "日语", "日本"),
 "Gintama Movie 3: Yoshiwara Daienjou": ("银魂 剧场版：吉原大炎上", "日语", "日本"),
 "Shin Gintama Movie: Yoshiwara Daienjou": ("银魂 剧场版：吉原大炎上", "日语", "日本"),
}


def norm(s):
    s = (s or '').lower().strip()
    s = s.replace("'", "").replace("\u2019", "").replace(".", "").replace("-", "")
    s = re.sub(r"[^0-9a-z\u4e00-\u9fff\u3040-\u30ff]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


NM = {norm(k): v for k, v in M.items()}


def lookup(title):
    if title in EXACT: return EXACT[title]
    n = norm(title)
    if n in NM: return NM[n]
    # 逐级去掉尾部修饰再试
    for sep in [" - ", ": ", " ("]:
        if sep in title:
            head = title.split(sep)[0]
            nh = norm(head)
            if head in EXACT: return EXACT[head]
            if nh in NM: return NM[nh]
    return ("", "", "")


rows = []


def add(platform, chart, rank, title_orig, title_cn, region, lang, year,
        score, votes, url, source_kind, note, score_scale):
    rows.append(dict(
        平台=platform, 榜单=chart, 排名=rank, 片名原文=title_orig, 中文译名=title_cn,
        原始语言=lang, 制片地区=region, 上映年份=('' if year is None else str(year)),
        平台评分=('' if score is None else str(score)), 评分人数=votes,
        作品链接=url, 评分制=score_scale,
        数据性质=source_kind, 备注=note))


# ===== 1. 豆瓣 =====
for r in S['douban']:
    orig = r['title_orig'].lstrip('/ ').strip() or r['title_cn']
    cn, lang, reg = lookup(orig) if orig != r['title_cn'] else (r['title_cn'], '', '')
    add('豆瓣电影 Douban', '豆瓣电影 Top 250（取前 50）', r['rank'], orig, r['title_cn'],
        r['region'], lang if lang else ('汉语普通话' if r['region'].startswith('中国') else ''),
        r['year'], r['score'], r['votes'], r['url'], '官方榜单原文', '', '10 分制')

# ===== 2. IMDb =====
for r in S['imdb']:
    cn, lang, reg = lookup(r['title_orig'])
    add('IMDb', 'IMDb Top 250（取前 50）', r['rank'], r['title_orig'], cn, reg, lang,
        r['year'], r['score'], r['votes'], r['url'], '官方榜单原文', '', '10 分制')

# ===== 3. Rotten Tomatoes =====
for r in E['rt'][:50]:
    rk = int(re.sub(r'\D', '', r['rank_raw'] or '0') or 0)
    cn, lang, reg = lookup(r['title'])
    add('Rotten Tomatoes 烂番茄', '300 Best Movies of All Time（取前 50）', rk, r['title'], cn,
        reg, lang, r['year'], r['score'].rstrip('%'), None, r['href'],
        '官方榜单原文（RT 编辑部榜单）',
        'Tomatometer＝专业影评人好评百分比；排序另计入 Popcornmeter 观众票、评论数与上映年份，并含编辑人工调整',
        '百分制')

# ===== 4. Metacritic =====
for i, r in enumerate(MC[:50], 1):
    t = re.sub(r'^\d+\.\s*', '', r['title'])
    m = re.match(r'^(.*?)\s*\((\d{4})\)$', t)
    title = m.group(1) if m else t
    year = m.group(2) if m else None
    date = ''
    dm = re.search(r'([A-Z]{3} \d{1,2}, (\d{4}))', r['txt'])
    if dm:
        date = dm.group(1)
        if not year: year = dm.group(2)
    cn, lang, reg = lookup(title)
    note = f"榜单显示名次 {r['rank'].rstrip('.')}；平台标注上映日期 {date}"
    add('Metacritic', 'Best Movies of All Time（Metascore 高→低，取前 50）', i, title, cn,
        reg, lang, year, r['metascore'], None, r['href'], '官方榜单原文', note, '百分制')

# ===== 5. Letterboxd =====
for i, (base, det) in enumerate(zip(E['letterboxd'][:50], D['letterboxd'][:50]), 1):
    m = re.match(r'Poster for (.*) \((\d{4})\)$', base['alt'])
    title = m.group(1) if m else base['alt']
    year = m.group(2) if m else ''
    avg = None
    if det.get('avg'):
        mm = re.search(r'([\d.]+)', det['avg'])
        if mm: avg = mm.group(1)
    cn, lang, reg = lookup(title)
    add('Letterboxd', 'Letterboxd 官方 Top 500 Films（取前 50）', i, title, cn, reg, lang,
        year, avg, None, base['href'], '官方榜单原文',
        '榜单页不显示评分人数；评分为影片页公开平均分（5 分制）', '5 分制')

# ===== 6. MyAnimeList =====
for r in S['mal']:
    cn, lang, reg = lookup(r['title_orig'])
    add('MyAnimeList', 'Top Anime（取前 50）', r['rank'], r['title_orig'], cn or '', reg or '日本',
        lang or '日语', r['year'], r['score'], r['votes'], r['url'], '官方榜单原文',
        f"类型：{r['format']}｜放送：{r['air']}｜评分人数＝收藏该作品的会员数（members）", '10 分制')

# ===== 7. AniList =====
for r in S['anilist']:
    cn, lang, reg = lookup(r['title_orig'])
    add('AniList', 'Anime 按 Average Score 降序（取前 50）', r['rank'], r['title_orig'], cn or '',
        reg or '日本', lang or '日语', r['year'], r['score'], r['users'], r['url'],
        '官方公开 GraphQL API 实时查询',
        f"英文名：{r['title_en']}｜原名：{r['title_native']}｜类型：{r['format']}｜人数＝收藏用户数（popularity）",
        '百分制')

# ===== 8. AlloCine =====
for i, (base, det) in enumerate(zip(E['allocine'][:50], AC[:50]), 1):
    txt = base['text']
    parts = [x.strip() for x in txt.split('|')]
    rank = parts[0]
    fr_title = parts[1] if len(parts) > 1 else ''
    orig = ''
    mm = re.search(r'Titre original\s+(.*?)\s*\|', txt)
    if mm: orig = mm.group(1).strip()
    score = det.get('spec')
    if score: score = score.replace(',', '.')
    votes = None
    if det.get('votes'):
        try: votes = int(det['votes'])
        except Exception: votes = None
    title = orig or fr_title
    cn, lang, reg = lookup(title)
    add('AlloCiné（法国）', 'Les 300 meilleurs films de tous les temps（观众评分，取前 50）',
        int(rank) if rank.isdigit() else i, title, cn, reg, lang, det.get('year') or '',
        score, votes, det.get('url') or '', '官方榜单原文',
        f"法语片名：{fr_title}｜评分＝观众评分（Spectateurs，5 分制），人数＝notes 数", '5 分制')

# -------- 统计与落盘 --------
json.dump(rows, open('rows_final.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
missing = [r for r in rows if not r['中文译名']]
print('总行数:', len(rows))
print('缺中文译名:', len(missing))
missing_titles = sorted({r['片名原文'] for r in missing})
open('missing_cn.txt', 'w', encoding='utf-8').write('\n'.join(missing_titles))
print('缺译名唯一片名:', len(missing_titles))
noreg = sorted({r['片名原文'] for r in rows if not r['制片地区']})
open('missing_region.txt', 'w', encoding='utf-8').write('\n'.join(noreg))
print('缺地区唯一片名:', len(noreg))
