// 通过 TMDB 官方 API 抓取「各国/地区高分影片榜 + 高分剧集榜」
// 本机直连 api.themoviedb.org 不通，但浏览器网络通道可通 → 在 themoviedb.org 页面内用 fetch（并行批量）
// 密钥从 .tmdb_key.txt 读取（不要把密钥写进命令行）
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const BASE = path.resolve(__dirname, '..');
const KEYFILE = path.join(BASE, '.tmdb_key.txt');
if (!fs.existsSync(KEYFILE)) {
  console.error('缺少 .tmdb_key.txt');
  process.exit(1);
}
const KEY = fs.readFileSync(KEYFILE, 'utf8').trim();

const COUNTRIES = [
  { code: 'RU', cn: '俄罗斯', min: 400, tvmin: 120 },
  { code: 'DE', cn: '德国', min: 400, tvmin: 100 },
  { code: 'ES', cn: '西班牙', min: 300, tvmin: 120 },
  { code: 'IT', cn: '意大利', min: 300, tvmin: 80 },
  { code: 'GB', cn: '英国', min: 800, tvmin: 300 },
  { code: 'FR', cn: '法国', min: 400, tvmin: 120 },
  { code: 'JP', cn: '日本', min: 500, tvmin: 200 },
  { code: 'KR', cn: '韩国', min: 500, tvmin: 250 },
  { code: 'IN', cn: '印度', min: 400, tvmin: 80 },
  { code: 'CN', cn: '中国大陆', min: 300, tvmin: 200 },
  { code: 'HK', cn: '中国香港', min: 200, tvmin: 100 },
  { code: 'TW', cn: '中国台湾', min: 150, tvmin: 80 },
  { code: 'TH', cn: '泰国', min: 150, tvmin: 80 },
  { code: 'SE', cn: '瑞典', min: 150, tvmin: 60 },
  { code: 'DK', cn: '丹麦', min: 150, tvmin: 80 },
  { code: 'IR', cn: '伊朗', min: 120, tvmin: 30 },
  { code: 'PL', cn: '波兰', min: 150, tvmin: 50 },
  { code: 'BR', cn: '巴西', min: 150, tvmin: 80 },
  { code: 'MX', cn: '墨西哥', min: 120, tvmin: 50 },
  { code: 'AU', cn: '澳大利亚', min: 200, tvmin: 80 },
];

const LANG_CN = {
  en: '英语', ja: '日语', ko: '韩语', zh: '汉语', fr: '法语', de: '德语', ru: '俄语',
  es: '西班牙语', it: '意大利语', pt: '葡萄牙语', th: '泰语', sv: '瑞典语', da: '丹麦语',
  fa: '波斯语', pl: '波兰语', hi: '印地语', tr: '土耳其语', nl: '荷兰语', he: '希伯来语',
  ar: '阿拉伯语', cs: '捷克语', hu: '匈牙利语', el: '希腊语', no: '挪威语', fi: '芬兰语',
  is: '冰岛语', id: '印尼语', vi: '越南语', tl: '菲律宾语', uk: '乌克兰语',
};
const WANT = 50;
const hasCN = s => /[\u4e00-\u9fff]/.test(s || '');

const urlOf = (kind, c, page) => {
  const ep = kind === '电影' ? 'movie' : 'tv';
  const min = kind === '电影' ? c.min : c.tvmin;
  return 'https://api.themoviedb.org/3/discover/' + ep + '?api_key=' + KEY +
    '&language=zh-CN&sort_by=vote_average.desc&include_adult=false' +
    '&with_origin_country=' + c.code + '&vote_count.gte=' + min + '&page=' + page;
};

(async () => {
  const b = await chromium.launch({ channel: 'msedge', headless: true });
  const page = await b.newPage();
  await page.goto('https://www.themoviedb.org/', { waitUntil: 'domcontentloaded', timeout: 60000 });

  const jobs = [];
  for (const c of COUNTRIES) {
    for (const kind of ['电影', '剧集']) {
      for (let p = 1; p <= 3; p++) jobs.push({ c, kind, page: p });
    }
  }

  const bucket = {};
  const BATCH = 6;
  for (let i = 0; i < jobs.length; i += BATCH) {
    const slice = jobs.slice(i, i + BATCH);
    const urls = slice.map(j => urlOf(j.kind, j.c, j.page));
    let res = [];
    try {
      res = await page.evaluate(async us => Promise.all(us.map(u =>
        fetch(u).then(r => r.ok ? r.json() : null).catch(() => null))), urls);
    } catch (e) {
      res = [];
    }
    slice.forEach((j, k) => {
      const r = res[k];
      if (!r || !r.results) return;
      const key = j.kind + '|' + j.c.code;
      bucket[key] = (bucket[key] || []).concat(r.results);
    });
    if (((i / BATCH) | 0) % 4 === 0) console.log('进度', Math.min(i + BATCH, jobs.length), '/', jobs.length);
  }
  await b.close();

  const out = [], meta = [];
  for (const c of COUNTRIES) {
    for (const kind of ['电影', '剧集']) {
      const key = kind + '|' + c.code;
      const seen = new Set();
      const list = (bucket[key] || []).filter(m => !seen.has(m.id) && seen.add(m.id));
      list.sort((a, b) => b.vote_average - a.vote_average || b.vote_count - a.vote_count);
      const top = list.slice(0, WANT);
      const isTV = kind === '剧集';
      const min = isTV ? c.tvmin : c.min;
      top.forEach((m, i) => {
        const orig = isTV ? (m.original_name || m.name) : (m.original_title || m.title);
        const zh = hasCN(m.name || m.title) ? (m.name || m.title) : '';
        const y = ((isTV ? m.first_air_date : m.release_date) || '').slice(0, 4);
        out.push({
          k: kind, p: 'TMDB·' + c.cn, ch: c.cn + (isTV ? '剧集高分榜' : '影片高分榜'), r: i + 1,
          t: orig, cn: zh || orig,
          lang: LANG_CN[m.original_language] || (m.original_language || '—').toUpperCase(),
          reg: c.cn, y: y, sc: String(Math.round((m.vote_average || 0) * 10) / 10), v: m.vote_count || 0,
          u: 'https://www.themoviedb.org/' + (isTV ? 'tv/' : 'movie/') + m.id + '?language=zh-CN',
          sca: '10 分制', nat: '官方公开 API 实时查询',
          rm: 'TMDB：制片国家含' + c.cn + '，按用户平均分降序、评分人数≥' + min + (zh ? '' : '；TMDB 暂无中文译名，沿用原名'),
          img: m.poster_path ? 'https://image.tmdb.org/t/p/w342' + m.poster_path : '',
          id: kind + '|TMDB·' + c.cn + '|' + orig + '|' + y,
        });
      });
      meta.push({ code: c.code, cn: c.cn, kind: kind, min: min, n: top.length });
      console.log(c.cn.padEnd(6), kind, '->', String(top.length).padStart(2), '条  最高', top.length ? top[0].vote_average : '-');
    }
  }

  const outFile = path.join(BASE, 'data', 'tmdb_rows.json');
  fs.mkdirSync(path.dirname(outFile), { recursive: true });
  fs.writeFileSync(outFile, JSON.stringify({ meta, rows: out }, null, 0), 'utf8');
  console.log('DONE 总条数', out.length, '->', outFile);
})();
