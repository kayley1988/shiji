// 为 README 生成演示截图（无头 Edge）
const path = require('path');
const fs = require('fs');
const { chromium } = require('playwright-core');

const OUT = path.join(__dirname, '..', 'docs', 'screenshots');
const BASE = 'http://[::1]:5181';

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch({
    executablePath: 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
    headless: true,
    args: ['--no-sandbox', '--disable-gpu'],
  });
  const page = await browser.newPage({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 2 });

  // 1. 首页（等待每日一诗等数据渲染完成）
  await page.goto(BASE + '/', { waitUntil: 'networkidle', timeout: 60000 }).catch(() => {});
  await page.waitForTimeout(7000);
  await page.screenshot({ path: path.join(OUT, 'home.png') });
  console.log('home.png done');

  // 2. 诗云星图（朝代泳道时间轴）
  await page.goto(BASE + '/galaxy', { waitUntil: 'networkidle', timeout: 60000 }).catch(() => {});
  await page.waitForTimeout(6000);
  await page.mouse.move(800, 450);
  await page.screenshot({ path: path.join(OUT, 'galaxy.png') });
  console.log('galaxy.png done');

  // 3. 闯关答题中：选唐 -> 开始闯关
  await page.goto(BASE + '/challenge', { waitUntil: 'networkidle', timeout: 60000 }).catch(() => {});
  await page.waitForTimeout(3000);
  await page.locator('text=唐').first().click({ timeout: 8000 });
  await page.waitForTimeout(600);
  await page.locator('button:has-text("开始闯关")').click({ timeout: 8000 });
  await page.waitForTimeout(4000);
  await page.screenshot({ path: path.join(OUT, 'challenge.png') });
  console.log('challenge.png done');

  // 4. 无尽连刷中：回配置页选无尽模式
  await page.goto(BASE + '/challenge', { waitUntil: 'networkidle', timeout: 60000 }).catch(() => {});
  await page.waitForTimeout(3000);
  await page.locator('text=唐').first().click({ timeout: 8000 });
  await page.waitForTimeout(400);
  await page.locator('text=无尽刷题').first().click({ timeout: 8000 });
  await page.waitForTimeout(400);
  await page.locator('button:has-text("开始连刷")').click({ timeout: 8000 });
  await page.waitForTimeout(4000);
  await page.screenshot({ path: path.join(OUT, 'endless.png') });
  console.log('endless.png done');

  await browser.close();
  console.log('ALL DONE');
})();
