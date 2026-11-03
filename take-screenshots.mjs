/**
 * Take screenshots of every AFAS Studio page using Puppeteer.
 * Run: node take-screenshots.mjs
 */
import puppeteer from 'puppeteer';
import { execSync } from 'child_process';
import { mkdirSync, existsSync } from 'fs';
import { setTimeout as sleep } from 'timers/promises';

const SCREENSHOT_DIR = './screenshots-app';
if (!existsSync(SCREENSHOT_DIR)) mkdirSync(SCREENSHOT_DIR, { recursive: true });

const PAGES = [
  { name: '01-simulator', path: '/', actions: async (page) => {
    // Click "Run Simulation"
    await sleep(500);
    const btn = await page.$('button:has(svg)');
    const buttons = await page.$$('button');
    for (const b of buttons) {
      const text = await b.evaluate(el => el.textContent);
      if (text && text.includes('Run Simulation')) {
        await b.click();
        break;
      }
    }
    await sleep(800);
  }},
  { name: '02-simulator-gantt', path: '/', actions: async (page) => {
    // Load a preset and run
    const buttons = await page.$$('button');
    for (const b of buttons) {
      const text = await b.evaluate(el => el.textContent);
      if (text && text.includes('W2')) { await b.click(); break; }
    }
    await sleep(300);
    // Select all policies
    const policyBtns = await page.$$('button');
    for (const b of policyBtns) {
      const text = await b.evaluate(el => el.textContent);
      if (text && ['SJF', 'SRTF', 'RR', 'Priority'].some(p => text.includes(p))) {
        await b.click();
        await sleep(100);
      }
    }
    // Run
    for (const b of await page.$$('button')) {
      const text = await b.evaluate(el => el.textContent);
      if (text && text.includes('Run Simulation')) { await b.click(); break; }
    }
    await sleep(800);
  }},
  { name: '03-audit-log', path: '/#/audit', actions: async (page) => {
    await sleep(500);
  }},
  { name: '04-metrics', path: '/#/metrics', actions: async (page) => {
    await sleep(500);
  }},
  { name: '05-experiments', path: '/#/experiments', actions: async (page) => {
    await sleep(300);
  }},
  { name: '06-docs', path: '/#/docs', actions: async (page) => {
    await sleep(500);
  }},
];

async function main() {
  // First, run a simulation to have data for all pages
  const browser = await puppeteer.launch({
    headless: 'new',
    defaultViewport: { width: 1440, height: 900 },
    args: ['--no-sandbox'],
  });

  const page = await browser.newPage();
  
  // Go to simulator, load preset, select all policies, and run
  await page.goto('http://localhost:5173/', { waitUntil: 'networkidle0', timeout: 15000 });
  await sleep(1000);
  
  // Click W2 preset
  let buttons = await page.$$('button');
  for (const b of buttons) {
    const text = await b.evaluate(el => el.textContent);
    if (text && text.trim() === 'W2') { await b.click(); break; }
  }
  await sleep(300);
  
  // Enable all policies
  buttons = await page.$$('button');
  for (const b of buttons) {
    const text = await b.evaluate(el => el.textContent);
    if (!text) continue;
    const t = text.trim();
    if (['SJF', 'SRTF', 'RR', 'Priority'].some(p => t.startsWith(p) && t.length < 30)) {
      await b.click();
      await sleep(100);
    }
  }
  await sleep(200);
  
  // Run simulation
  buttons = await page.$$('button');
  for (const b of buttons) {
    const text = await b.evaluate(el => el.textContent);
    if (text && text.includes('Run Simulation')) { await b.click(); break; }
  }
  await sleep(1500);
  
  // Screenshot 1: Simulator page with results
  await page.screenshot({ path: `${SCREENSHOT_DIR}/01-simulator.png`, fullPage: false });
  console.log('✓ 01-simulator.png');
  
  // Scroll down to see Gantt chart
  await page.evaluate(() => window.scrollBy(0, 400));
  await sleep(500);
  await page.screenshot({ path: `${SCREENSHOT_DIR}/02-gantt-chart.png`, fullPage: false });
  console.log('✓ 02-gantt-chart.png');
  
  // Screenshot 3: Audit log
  await page.goto('http://localhost:5173/#/audit', { waitUntil: 'networkidle0', timeout: 10000 });
  await sleep(1000);
  await page.screenshot({ path: `${SCREENSHOT_DIR}/03-audit-log.png`, fullPage: false });
  console.log('✓ 03-audit-log.png');
  
  // Screenshot 4: Metrics
  await page.goto('http://localhost:5173/#/metrics', { waitUntil: 'networkidle0', timeout: 10000 });
  await sleep(1000);
  await page.screenshot({ path: `${SCREENSHOT_DIR}/04-metrics.png`, fullPage: false });
  console.log('✓ 04-metrics.png');
  
  // Scroll down to see charts
  await page.evaluate(() => window.scrollBy(0, 500));
  await sleep(500);
  await page.screenshot({ path: `${SCREENSHOT_DIR}/05-metrics-charts.png`, fullPage: false });
  console.log('✓ 05-metrics-charts.png');
  
  // Screenshot 6: Experiments
  await page.goto('http://localhost:5173/#/experiments', { waitUntil: 'networkidle0', timeout: 10000 });
  await sleep(800);
  await page.screenshot({ path: `${SCREENSHOT_DIR}/06-experiments.png`, fullPage: false });
  console.log('✓ 06-experiments.png');
  
  // Screenshot 7: Docs
  await page.goto('http://localhost:5173/#/docs', { waitUntil: 'networkidle0', timeout: 10000 });
  await sleep(1000);
  await page.screenshot({ path: `${SCREENSHOT_DIR}/07-docs.png`, fullPage: false });
  console.log('✓ 07-docs.png');
  
  await browser.close();
  console.log('\nAll screenshots saved to', SCREENSHOT_DIR);
}

main().catch(console.error);
