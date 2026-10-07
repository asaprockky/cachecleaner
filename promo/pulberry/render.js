// Usage: node render.js --lang uz --out frames_uz            (full frame sequence)
//        node render.js --lang uz --stills 0.5,2.5,5 --out stills   (key frames only)
const { chromium } = require('/opt/node-tools/node_modules/playwright');
const path = require('path'); const fs = require('fs');
const args = Object.fromEntries(process.argv.slice(2).join(' ').split('--').filter(Boolean).map(s => { const [k, ...v] = s.trim().split(' '); return [k, v.join(' ')]; }));
const lang = args.lang || 'uz'; const fps = +(args.fps || 30); const out = path.resolve(__dirname, args.out || ('frames_' + lang));
fs.mkdirSync(out, { recursive: true });
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium', args: ['--no-sandbox', '--font-render-hinting=none'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await p.goto('file://' + path.join(__dirname, 'index.html') + '?lang=' + lang);
  await p.waitForFunction(() => window.READY === true);
  await p.waitForTimeout(300);
  const dur = await p.evaluate(() => window.DURATION);
  const times = args.stills ? args.stills.split(',').map(Number) : Array.from({ length: Math.round(dur * fps) }, (_, i) => i / fps);
  const t0 = Date.now();
  for (let i = 0; i < times.length; i++) {
    await p.evaluate(t => window.seek(t), times[i]);
    const name = args.stills ? `still_${times[i].toFixed(2)}.png` : `f${String(i).padStart(5, '0')}.png`;
    await p.screenshot({ path: path.join(out, name), type: 'png' });
    if (i % 100 === 0) console.log(`${i}/${times.length} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  await b.close(); console.log('done', times.length, 'frames ->', out);
})().catch(e => { console.error(e); process.exit(1); });
