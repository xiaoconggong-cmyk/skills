const { chromium } = require('playwright');
const pptxParser = require('pptx-parser');
const fs = require('fs');
const path = require('path');

async function capturePPTX() {
    const pptxPath = process.argv[2] || 'C:\\Users\\25124\\.workbuddy\\skills\\ppt-multiagent\\assets\\demo_v6.pptx';
    const outputDir = process.argv[3] || 'C:\\Users\\25124\\.workbuddy\\skills\\ppt-multiagent\\assets\\screenshots_v6';

    // Ensure output directory exists
    if (!fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }

    const browser = await chromium.launch();
    const context = await browser.newContext({
        viewport: { width: 1280, height: 960 }
    });

    try {
        // Parse PPTX to get slide dimensions and content
        const parser = new pptxParser.PresentationParser();
        const result = await parser.parse(pptxPath);

        for (let i = 0; i < result.slides.length; i++) {
            const page = await context.newPage();

            // Create HTML representation of the slide
            const slide = result.slides[i];
            const slideW = result.width || 10;  // inches
            const slideH = result.height || 7.5;
            const pxPerInch = 96;

            let html = `
<!DOCTYPE html>
<html>
<head>
<style>
body { margin: 0; padding: 0; background: #f0f0f0; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
.slide-container { width: ${slideW * pxPerInch}px; height: ${slideH * pxPerInch}px; background: white; position: relative; box-shadow: 0 4px 20px rgba(0,0,0,0.15); }
.shape { position: absolute; }
.textbox { position: absolute; font-family: "Microsoft YaHei", "SimSun", sans-serif; }
.dashed-box { position: absolute; border: 1px dashed #9CA3AF; box-sizing: border-box; }
</style>
</head>
<body>
<div class="slide-container">
`;
            // Add shapes
            for (const shape of slide.shapes || []) {
                if (shape.type === 'text') {
                    const x = (shape.x || 0) * pxPerInch;
                    const y = (shape.y || 0) * pxPerInch;
                    const w = (shape.width || 1) * pxPerInch;
                    const h = (shape.height || 0.5) * pxPerInch;
                    const fontSize = shape.fontSize || 16;
                    const color = shape.fontColor || '#000000';
                    const bold = shape.bold ? 'font-weight: bold;' : '';
                    const align = shape.align || 'left';

                    html += `<div class="textbox" style="left: ${x}px; top: ${y}px; width: ${w}px; height: ${h}px; font-size: ${fontSize}px; color: ${color}; ${bold} text-align: ${align};">${shape.text || ''}</div>\n`;
                } else if (shape.type === 'line' && shape.dashed) {
                    const x = (shape.x || 0) * pxPerInch;
                    const y = (shape.y || 0) * pxPerInch;
                    const w = (shape.width || 1) * pxPerInch;
                    const h = (shape.height || 0.5) * pxPerInch;
                    html += `<div class="dashed-box" style="left: ${x}px; top: ${y}px; width: ${w}px; height: ${h}px;"></div>\n`;
                }
            }

            html += `</div></body></html>`;

            await page.setContent(html);
            await page.waitForTimeout(500);

            const screenshotPath = path.join(outputDir, `slide_${i + 1}.png`);
            await page.screenshot({ path: screenshotPath, fullPage: false });
            console.log(`Screenshot saved: ${screenshotPath}`);
            await page.close();
        }

        console.log(`All ${result.slides.length} slides captured.`);
    } catch (e) {
        console.error('Error:', e.message);
    } finally {
        await browser.close();
    }
}

capturePPTX();
