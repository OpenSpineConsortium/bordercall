const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  for (const [w, name] of [[1280, 'desk'], [390, 'phone']]) {
    const p = await b.newPage({ viewport: { width: w, height: 900 } });
    await p.goto('file://' + process.argv[2] + '/index.html');
    await p.waitForTimeout(500);
    await p.screenshot({ path: process.argv[2] + '/shot-' + name + '.png', fullPage: false });
    const sw = await p.evaluate(() => [document.documentElement.scrollWidth, document.documentElement.clientWidth, document.body.scrollHeight]);
    console.log(name, sw);
    await p.evaluate(() => window.scrollTo(0, 5200));
    await p.screenshot({ path: process.argv[2] + '/shot-' + name + '-2.png' });
  }
  await b.close();
})();
