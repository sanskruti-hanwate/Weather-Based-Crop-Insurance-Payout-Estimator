import json
import asyncio
from playwright.async_api import async_playwright

async def main():
    crop_map = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Set headless=True if you want hidden
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://pmfby.gov.in")

        # Click "Insurance Premium Calculator"
        await page.click("text=Insurance Premium Calculator")
        await page.wait_for_timeout(3000)

        # ==== CSS Selectors ====
        base = "#app > div > div:nth-child(1) > div > div.newHeader__headerMain___3js6e > div.newHeader__cardsMenu___1Sgs1.container-fluid > div > div:nth-child(1) > div > div.newHeader__modalInnerOverlay___2U5R2 > div > div > div > div > div.newHeader__InnerCalculator___1YK6V.modal-body > form > div > div"
        season_sel = f"{base} > div:nth-child(1) > div > select"
        year_sel   = f"{base} > div:nth-child(2) > div > select"
        scheme_sel = f"{base} > div:nth-child(3) > div > select"
        state_sel  = f"{base} > div:nth-child(4) > div > select"
        dist_sel   = f"{base} > div:nth-child(5) > div > select"
        crop_sel   = f"{base} > div:nth-child(6) > div > select"

        # ==== Select Season, Year, Scheme ====
        await page.select_option(season_sel, value="01///Kharif")
        await page.select_option(year_sel, value="2020")
        await page.select_option(scheme_sel, value="02///Weather Based Crop Insurance Scheme")
        await page.wait_for_timeout(2000)

        # ✅ Select Maharashtra (label is case-sensitive!)
        await page.select_option(state_sel, value="5FB484F4-A27D-46BF-8368-81656DFBB157///Maharashtra")
        await page.wait_for_timeout(1500)

        # ==== Districts Loop ====
        district_select = await page.query_selector(dist_sel)
        district_options = await district_select.query_selector_all("option")

        for option in district_options:
            value = await option.get_attribute("value")
            name = await option.inner_text()
            if not value or name.strip().lower() == "select":
                continue

            print(f"📍 {name}")
            await page.select_option(dist_sel, value=value)
            await page.wait_for_timeout(1500)

            # ==== Crops in this district ====
            crop_select = await page.query_selector(crop_sel)
            crop_options = await crop_select.query_selector_all("option")

            crops = []
            for c in crop_options:
                crop_name = await c.inner_text()
                if crop_name.strip().lower() != "select":
                    crops.append(crop_name)

            crop_map[name] = crops
            print(f"✅ {name}: {len(crops)} crops")

        # ==== Save to file ====
        with open("district_crop_data_css.json", "w", encoding="utf-8") as f:
            json.dump(crop_map, f, indent=2, ensure_ascii=False)

        print("\n🎉 Done! Saved to district_crop_data_css.json")
        await browser.close()

asyncio.run(main())
