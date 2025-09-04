import asyncio
from playwright.async_api import async_playwright

from scraper.ebay_scraper import search_ebay
from scraper.kikuu_scraper import search_kikuu as search_kikuu
from scraper.search_banggood import search_alibaba


async def run_scraper_auto(context, scraper_func, site_name, product, start_page=1, batch_size=4, max_pages=50):
    page = await context.new_page()
    current_page = start_page

    while current_page <= max_pages:
        print(f"\n🔎 [{site_name}] Parcours des pages {current_page} à {current_page + batch_size - 1}...\n")

        results, last_page = await scraper_func(page, product, start_page=current_page, batch_size=batch_size)

        if not results:
            print(f"⚠️ [{site_name}] Aucun produit trouvé. Fin du scraping.")
            break

        print(f"📦 [{site_name}] Produits trouvés entre la page {current_page} et {last_page} :\n")
        for i, r in enumerate(results, 1):
            print(f"{i}. {r['title']}")
            print(f"   Prix : {r['price']}")
            print(f"   URL  : {r['url']}")
            print(f"   Image: {r['img']}\n")

        current_page += batch_size

    print(f"✅ [{site_name}] Scraping terminé (limite {max_pages} pages atteinte ou plus de résultats).")
    await page.close()


async def main():
    product = input("Entrez le produit à rechercher : ").strip()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()

        await asyncio.gather(
            run_scraper_auto(context, search_ebay, "eBay", product, max_pages=50),
            run_scraper_auto(context, search_kikuu, "Kikuu", product, max_pages=50),
            run_scraper_auto(context, search_alibaba, "Alibaba", product, max_pages=50),
        )

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
