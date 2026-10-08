// 端到端验收：启动页新交互 + 真实打一局闯关 + 学习仪表盘截图
const path = require('path');
const { chromium } = require('playwright-core');

const OUT = path.join(__dirname, 'screenshots');
const BASE = 'http://[::1]:5181';

(async () => {
  const browser = await chromium.launch({
    executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    headless: true,
    args: ['--no-sandbox', '--disable-gpu'],
  });
  const page = await browser.newPage({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 2 });

  // 1. 启动页：等「轻触进入」按钮出现后截图
  await page.goto(BASE + '/', { waitUntil: 'domcontentloaded', timeout: 60000 });
  await page.waitForSelector('.enter-btn', { timeout: 10000 });
  await page.waitForTimeout(600);
  await page.screenshot({ path: path.join(OUT, 'splash.png') });
  console.log('splash.png done');

  // 2. 点击进入 → 首页
  await page.locator('.enter-btn').click();
  await page.waitForTimeout(4000);
  await page.screenshot({ path: path.join(OUT, 'home_after.png') });
  console.log('home_after.png done');

  // 3. 真实打一局闯关（故意答错一半，制造错题）
  await page.goto(BASE + '/challenge', { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(2500);
  await page.locator('text=唐').first().click();
  await page.waitForTimeout(500);
  await page.locator('button:has-text("开始闯关")').click();
  await page.waitForTimeout(3000);

  for (let i = 0; i < 10; i++) {
    // 第 i<5 题点第一个选项（多半错），后面随机选
    const opts = page.locator('.q-opt');
    await opts.nth(i < 5 ? 1 : 0).click();
    await page.waitForTimeout(300);
    await page.locator('button:has-text("确认作答")').click();
    await page.waitForTimeout(500);
    const next = page.locator('button:has-text("下一题")');
    const done = page.locator('button:has-text("查看成绩")');
    if (await done.count()) { await done.click(); break; }
    await next.click();
    await page.waitForTimeout(500);
  }
  await page.waitForTimeout(2500);
  await page.screenshot({ path: path.join(OUT, 'result.png') });
  console.log('result.png done');

  // 4. 进入学习仪表盘
  await page.locator('button:has-text("学习仪表盘")').click();
  await page.waitForTimeout(3500);
  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(600);
  await page.screenshot({ path: path.join(OUT, 'dashboard.png'), fullPage: false });
  console.log('dashboard.png done');

  await browser.close();
  console.log('ALL DONE');
})();
