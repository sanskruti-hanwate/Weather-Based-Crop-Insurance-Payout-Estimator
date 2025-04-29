import json
import asyncio
from playwright.async_api import async_playwright

async def main():
    crop_map = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://pmfby.gov.in")
        await page.click("text=Insurance Premium Calculator")
        await page.wait_for_timeout(3000)

        # ==== Selectors ====
        base = "#app > div > div:nth-child(1) > div > div.newHeader__headerMain___3js6e > div.newHeader__cardsMenu___1Sgs1.container-fluid > div > div:nth-child(1) > div > div.newHeader__modalInnerOverlay___2U5R2 > div > div > div > div > div.newHeader__InnerCalculator___1YK6V.modal-body > form > div > div"
        season_sel = f"{base} > div:nth-child(1) > div > select"
        year_sel   = f"{base} > div:nth-child(2) > div > select"
        scheme_sel = f"{base} > div:nth-child(3) > div > select"
        state_sel  = f"{base} > div:nth-child(4) > div > select"
        dist_sel   = f"{base} > div:nth-child(5) > div > select"
        crop_sel   = f"{base} > div:nth-child(6) > div > select"
        area_input = f"{base} > div:nth-child(7) > div > input"
        calc_button = "button[type='submit']"

        # ==== Select Static Options ====
        await page.select_option(season_sel, value="02///Rabi")
        await page.wait_for_timeout(2000)
        await page.select_option(year_sel, value="2020")
        await page.select_option(scheme_sel, value="02///Weather Based Crop Insurance Scheme")
        await page.wait_for_timeout(2000)
        await page.select_option(state_sel, value="5FB484F4-A27D-46BF-8368-81656DFBB157///MAHARASHTRA")
        await page.wait_for_timeout(1500)

        # ==== Districts Loop ====
        district_select = await page.query_selector(dist_sel)
        district_options = await district_select.query_selector_all("option")

        for option in district_options:
            district_value = await option.get_attribute("value")
            district_name = await option.inner_text()
            if not district_value or district_name.strip().lower() == "select":
                continue

            print(f"\n📍 District: {district_name}")
            await page.select_option(dist_sel, value=district_value)
            await page.wait_for_timeout(1000)

            crop_map[district_name] = {}
            crop_select = await page.query_selector(crop_sel)
            crop_options = await crop_select.query_selector_all("option")

            for c in crop_options:
                crop_value = await c.get_attribute("value")
                crop_name = await c.inner_text()
                if not crop_value or crop_name.strip().lower() == "select":
                    continue

                print(f" 🌾 Crop: {crop_name}")
                await page.select_option(crop_sel, value=crop_value)
                await page.wait_for_timeout(1000)

                try:
                    await page.wait_for_selector(area_input, timeout=4000)
                    await page.fill(area_input, "1")
                    await page.click(calc_button)
                    await page.wait_for_timeout(2000)

                    # Fetch data
                    sum_insured_selector = "#app > div > div:nth-child(1) > div > div.newHeader__headerMain___3js6e > div.newHeader__cardsMenu___1Sgs1.container-fluid > div > div:nth-child(1) > div > div.newHeader__modalInnerOverlay___2U5R2 > div > div > div > div > div.newHeader__InnerCalculator___1YK6V.modal-body > div:nth-child(2) > div > table > tbody > tr > td:nth-child(2)"
                    farmer_share_selector = "#app > div > div:nth-child(1) > div > div.newHeader__headerMain___3js6e > div.newHeader__cardsMenu___1Sgs1.container-fluid > div > div:nth-child(1) > div > div.newHeader__modalInnerOverlay___2U5R2 > div > div > div > div > div.newHeader__InnerCalculator___1YK6V.modal-body > div:nth-child(2) > div > table > tbody > tr > td:nth-child(3)"
                    actuarial_rate_selector = "#app > div > div:nth-child(1) > div > div.newHeader__headerMain___3js6e > div.newHeader__cardsMenu___1Sgs1.container-fluid > div > div:nth-child(1) > div > div.newHeader__modalInnerOverlay___2U5R2 > div > div > div > div > div.newHeader__InnerCalculator___1YK6V.modal-body > div:nth-child(2) > div > table > tbody > tr > td:nth-child(4)"
                    govt_premium_selector = "#app > div > div:nth-child(1) > div > div.newHeader__headerMain___3js6e > div.newHeader__cardsMenu___1Sgs1.container-fluid > div > div:nth-child(1) > div > div.newHeader__modalInnerOverlay___2U5R2 > div > div > div > div > div.newHeader__InnerCalculator___1YK6V.modal-body > div:nth-child(3) > div > table > tbody > tr > td:nth-child(4)"

                    sum_insured = await page.inner_text(sum_insured_selector)
                    farmer_share = await page.inner_text(farmer_share_selector)
                    actuarial_rate = await page.inner_text(actuarial_rate_selector)
                    govt_premium = await page.inner_text(govt_premium_selector)

                    crop_map[district_name][crop_name] = {
                        "sum_insured_per_hectare": sum_insured.strip(),
                        "farmer_share_percent": farmer_share.strip(),
                        "actuarial_rate_percent": actuarial_rate.strip(),
                        "govt_premium": govt_premium.strip()
                    }

                    print(f"   💰 Sum Insured: {sum_insured.strip()}")
                    print(f"   👨‍🌾 Farmer Share %: {farmer_share.strip()}")
                    print(f"   📊 Actuarial Rate %: {actuarial_rate.strip()}")
                    print(f"   🏛️ Govt Premium: {govt_premium.strip()}")

                except Exception as e:
                    print(f"❌ Skipping {crop_name} due to error: {e}")
                await page.wait_for_timeout(500)

        # ==== Save to JSON ====
        with open("district_crop_insurance_data.json", "w", encoding="utf-8") as f:
            json.dump(crop_map, f, indent=2, ensure_ascii=False)

        print("\n✅ Done! Data saved to district_crop_insurance_data.json")
        await browser.close()

asyncio.run(main())
