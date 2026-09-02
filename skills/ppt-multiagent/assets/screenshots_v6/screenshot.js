
const { chromium } = require('playwright');
(async () => {
    const browser = await chromium.launch();
    const page = await browser.newPage({ viewport: { width: 1280, height: 960 } });
    for (let i = 1; i <= 3; i++) {
        await page.goto('file:///C:/Users/25124/.workbuddy/skills/ppt-multiagent/assets/screenshots_v6/slide_' + i + '.html');
        await page.waitForTimeout(500);
        await page.screenshot({ path: 'C:/Users/25124/.workbuddy/skills/ppt-multiagent/assets/screenshots_v6/slide_' + i + '.png', fullPage: false });
        console.log('Screenshot: slide_' + i + '.png');
    }
    await browser.close();
})();
