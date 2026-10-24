# -*- coding: utf-8 -*-
"""纯 HTTP 抓取封面图（IMDb 官方 suggestion 接口），无需浏览器。
输出 poster_cache.json：{ "id": {"img": url, "t": imdb标题, "y": 年份} }
"""
import json, os, re, ssl, time, gzip, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
UA = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36',
      'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'}

CACHE_FILE = 'poster_cache.json'
cache = {}
if os.path.exists(CACHE_FILE):
    try:
        cache = json.load(open(CACHE_FILE, encoding='utf-8'))
    except Exception:
        cache = {}


def norm(s):
    s = (s or '').lower()
    s = re.sub(r'[\s\u3000]+', '', s)
    s = re.sub(r'[^\w\u4e00-\u9fff\u3040-\u30ff]', '', s)
    return s


def clean_title(t):
    t = re.sub(r'\s*[（(\[].*?[)）\]]\s*', ' ', str(t or ''))   # 去括号内容
    t = re.sub(r'\s*[:：]\s*.*$', '', t) if len(t) > 40 else t
    return t.strip()


def http_json(url, retry=2):
    for i in range(retry + 1):
        try:
            req = urllib.request.Request(url, headers=UA)
            r = urllib.request.urlopen(req, timeout=25, context=ctx)
            d = r.read()
            if r.headers.get('Content-Encoding') == 'gzip':
                d = gzip.decompress(d)
            return json.loads(d.decode('utf-8', 'ignore'))
        except Exception:
            if i == retry:
                return None
            time.sleep(1.2 * (i + 1))


def suggest(q):
    return http_json('https://v3.sg.media-imdb.com/suggestion/x/' + urllib.parse.quote(q) + '.json') or {}


STOP = {'season', 'series', 'part', 'volume', 'movie', 'final', 'story', 'episode', 'chapter'}


def toks(s):
    return {t for t in re.findall(r'[a-z0-9]+', (s or '').lower()) if len(t) >= 5 and t not in STOP}


CJK = re.compile(r'[\u4e00-\u9fff\u3040-\u30ff]')


def pick(items, qraw, year, kind):
    """返回最佳匹配条目；宁可留空也不误配。
       核心规则：标题必须有实质重合（完全相同 / 互相包含 / 共享长度≥5 的实词）；
       纯中文查询放宽为「年份吻合 ±1 且取最高分」。"""
    qnorm = norm(qraw)
    yt = int(year) if str(year).isdigit() else None
    cjk_q = bool(CJK.search(qraw or '')) and not re.search(r'[a-z0-9]{3,}', (qraw or '').lower())
    cands = []
    for it in items or []:
        if not (it.get('id') or '').startswith('tt'):
            continue
        img = (it.get('i') or {}).get('imageUrl')
        if not img:
            continue
        raw = it.get('l') or ''
        ln = norm(raw)
        core = (ln == qnorm) or (qnorm and (qnorm in ln or ln in qnorm)) or bool(toks(raw) & toks(qraw))
        y = it.get('y')
        yd = abs(int(y) - yt) if (yt and y) else None
        if cjk_q:
            if yd is None or yd > 1:
                continue
        else:
            if not core:
                continue
            if yd is not None and yd > (1 if kind == '剧集' else 2):
                continue
        s = 0
        if ln == qnorm:
            s += 100
        elif qnorm and (qnorm in ln or ln in qnorm):
            s += 50
        else:
            s += 8 * len(set(re.findall(r'\w+', ln)) & set(re.findall(r'\w+', qnorm)))
        if yd is not None:
            s += max(0, 20 - yd * 5)
        q = (it.get('q') or '').lower()
        if kind == '剧集':
            s += 30 if 'tv' in q else (-25 if q in ('feature', 'movie') else 0)
        else:
            s += 30 if ('feature' in q or 'movie' in q) else (-25 if 'tv' in q else 0)
        s += min(it.get('rank') or 0, 10) * 0.1
        cands.append((s, it))
    if not cands:
        return None
    cands.sort(key=lambda x: -x[0])
    return cands[0][1]


def thumb(u):
    # IMDb 图片支持后缀缩放，取 ~240px 宽版本，显著减小体积
    b = u.split('._V1_')[0]
    return b + '._V1_QL75_UX240_.jpg'


def extra_titles(r):
    """从备注里挖英文名 / 原名，用于 MAL、AniList 等罗马字片名"""
    out = []
    rm = str(r.get('备注') or '')
    for key in ('英文名', '原名'):
        m = re.search(key + r'：(.+?)(?:｜|$)', rm)
        if m:
            out.append(m.group(1).strip())
    return out


def work(r):
    rid = r['_id']
    if cache.get(rid, {}).get('img'):
        return rid, cache[rid]
    kind = r['内容类型']
    year = str(r.get('上映年份') or '')[:4]
    out = None
    o = str(r.get('片名原文') or '')
    cands = [o, clean_title(o)] + extra_titles(r) + [str(r.get('中文译名') or ''), clean_title(r.get('中文译名') or '')]
    if year:
        cands.append(o + ' ' + year)
    seen_q = set()
    for cand in cands:
        cand = str(cand or '').strip()
        if len(cand) < 2 or cand in seen_q:
            continue
        seen_q.add(cand)
        j = suggest(cand[:80])
        it = pick(j.get('d'), cand, year, kind)
        if it:
            out = {'img': thumb((it.get('i') or {}).get('imageUrl')), 't': it.get('l'), 'y': it.get('y')}
            break
        time.sleep(0.15)
    return rid, (out or {})


def main():
    mv = json.load(open('rows_final.json', encoding='utf-8'))
    tv = json.load(open('rows_tv.json', encoding='utf-8'))
    for r in mv:
        r['内容类型'] = '电影'
    rows = mv + tv
    # 豆瓣剧集周榜不再收录
    rows = [r for r in rows if not (r['内容类型'] == '剧集' and str(r['平台']).startswith('豆瓣'))]
    for r in rows:
        r['_id'] = '|'.join([r['内容类型'], str(r['平台']), str(r['片名原文']), str(r.get('上映年份') or '')])
    need = [r for r in rows if not cache.get(r['_id'], {}).get('img')]
    print('total', len(rows), 'need fetch', len(need))
    done = 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        for rid, val in ex.map(work, need):
            cache[rid] = val
            done += 1
            if done % 50 == 0:
                print('  ...', done, '/', len(need), flush=True)
                json.dump(cache, open(CACHE_FILE, 'w', encoding='utf-8'), ensure_ascii=False)
    json.dump(cache, open(CACHE_FILE, 'w', encoding='utf-8'), ensure_ascii=False)
    ok = sum(1 for v in cache.values() if v.get('img'))
    print('DONE. cache', len(cache), 'with image', ok)


if __name__ == '__main__':
    main()
