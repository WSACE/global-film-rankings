// 补抓：条数不足 50 的国家/地区榜，降低评分人数门槛再取一轮
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const BASE = path.resolve(__dirname, '..');
const KEY = fs.readFileSync(path.join(BASE, '.tmdb_key.txt'), 'utf8').trim();
const FILE = path.join(BASE, 'data', 'tmdb_rows.json');
const RAW = JSON.parse(fs.readFileSync(FILE, 'utf8'));

const LANG_CN = {
  en: '英语', ja: '日语', ko: '韩语', zh: '汉语', fr: '法语', de: '德语', ru: '俄语',
  es: '西班牙语', it: '意大利语', pt: '葡萄牙语', th: '泰语', sv: '瑞典语', da: '丹麦语',
  fa: '波斯语', pl: '波兰语', hi: '印地语', tr: '土耳其语', nl: '荷兰语', he: '希伯来语',
  ar: '阿拉伯语', cs: '捷克语', hu: '匈牙利语', el: '希腊语', no: '挪威语', fi: '芬兰语',
  is: '冰岛语', id: '印尼语', vi: '越南语', tl: '菲律宾语', uk: '乌克兰语',
};
const WANT = 50;
const hasCN = s => /[\u4e00-\u9fff]/.test(s || '');

(async () => {
  const sparse = RAW.meta.filter(m => m.n < WANT);
  console.log('待补充:', sparse.map(m => m.cn + m.kind + '(' + m.n + ')').join(' '));
  const b = await chromium.launch({ channel: 'msedge', headless: true });
  const page = await b.newPage();
  await page.goto('https://www.themoviedb.org/', { waitUntil: 'domcontentloaded', timeout: 60000 });

  const jobs = [];
  for (const m of sparse) {
    const min2 = Math.max(8, Math.round(m.min / 5));
    m._min2 = min2;
    for (let p = 1; p <= 3; p++) jobs.push({ m, min: min2, page: p });
  }
  const bucket = {};
  for (let i = 0; i < jobs.length; i += 6) {
    const slice = jobs.slice(i, i + 6);
    const urls = slice.map(j => 'https://api.themoviedb.org/3/discover/' + (j.m.kind === '电影' ? 'movie' : 'tv') +
      '?api_key=' + KEY + '&language=zh-CN&sort_by=vote_average.desc&include_adult=false' +
      '&with_origin_country=' + j.m.code + '&vote_count.gte=' + j.min + '&page=' + j.page);
    let res = [];
    try {
      res = await page.evaluate(async us => Promise.all(us.map(u =>
        fetch(u).then(r => r.ok ? r.json() : null).catch(() => null))), urls);
    } catch (e) { res = []; }
    slice.forEach((j, k) => {
      const r = res[k];
      if (!r || !r.results) return;
      const key = j.m.kind + '|' + j.m.code;
      bucket[key] = (bucket[key] || []).concat(r.results);
    });
  }
  await b.close();

  // 重建数据
  const byKey = {};
  for (const r of RAW.rows) byKey[r.k + '|' + r.reg] = byKey[r.k + '|' + r.reg] || [];
  const out = [], meta = [];
  for (const m of RAW.meta) {
    const key = m.kind + '|' + m.code;
    const extra = bucket[key] || [];
    const existing = RAW.rows.filter(r => r.k === m.kind && r.p === 'TMDB·' + m.cn);
    const seen = new Set(existing.map(r => r.id));
    const merged = existing.slice();
    for (const it of extra) {
      const isTV = m.kind === '剧集';
      const orig = isTV ? (it.original_name || it.name) : (it.original_title || it.title);
      const y = ((isTV ? it.first_air_date : it.release_date) || '').slice(0, 4);
      const id = m.kind + '|TMDB·' + m.cn + '|' + orig + '|' + y;
      if (seen.has(id)) continue;
      seen.add(id);
      const zh = hasCN(it.name || it.title) ? (it.name || it.title) : '';
      merged.push({
        k: m.kind, p: 'TMDB·' + m.cn, ch: m.cn + (isTV ? '剧集高分榜' : '影片高分榜'), r: 0,
        t: orig, cn: zh || orig,
        lang: LANG_CN[it.original_language] || (it.original_language || '—').toUpperCase(),
        reg: m.cn, y: y, sc: String(Math.round((it.vote_average || 0) * 10) / 10), v: it.vote_count || 0,
        u: 'https://www.themoviedb.org/' + (isTV ? 'tv/' : 'movie/') + it.id + '?language=zh-CN',
        sca: '10 分制', nat: '官方公开 API 实时查询',
        rm: 'TMDB：制片国家含' + m.cn + '，按用户平均分降序、评分人数≥' + Math.min(m.min, m._min2 || m.min) +
            (zh ? '' : '；TMDB 暂无中文译名，沿用原名'),
        img: it.poster_path ? 'https://image.tmdb.org/t/p/w342' + it.poster_path : '',
        id: id,
      });
    }
    merged.sort((a, c) => parseFloat(c.sc) - parseFloat(a.sc) || c.v - a.v);
    const top = merged.slice(0, WANT);
    top.forEach((r, i) => { r.r = i + 1; out.push(r); });
    meta.push({ code: m.code, cn: m.cn, kind: m.kind, min: Math.min(m.min, m._min2 || m.min), n: top.length });
    console.log(m.cn.padEnd(6), m.kind, m.n, '->', top.length);
  }
  fs.writeFileSync(FILE, JSON.stringify({ meta, rows: out }, null, 0), 'utf8');
  console.log('DONE 总条数', out.length);
})();
