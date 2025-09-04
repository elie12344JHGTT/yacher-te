import asyncio
from playwright.async_api import async_playwright
from scraper.ebay_scraper import search_ebay

async def main():
    product = input("Entrez le produit à rechercher sur eBay : ").strip()
    current_page = 1
    batch_size = 4

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # navigateur invisible
        page = await browser.new_page()

        while True:
            print(f"\n🔎 Parcours des pages {current_page} à {current_page + batch_size - 1} ...\n")

            results, last_page = await search_ebay(page, product, start_page=current_page, batch_size=batch_size)

            if not results:
                print("⚠️ Aucun produit trouvé dans ce lot de pages. Fin du scraping.")
                break

            print(f"Produits trouvés entre la page {current_page} et {last_page} :\n")
            for i, r in enumerate(results, 1):
                print(f"{i}. {r['title']}")
                print(f"   Prix : ${r['price']}")
                print(f"   URL  : {r['url']}")
                print(f"   Image: {r['img']}\n")

            action = input("➡️ Taper 'next' pour continuer avec les pages suivantes ou 'exit' pour quitter : ").strip().lower()
            if action != "next":
                break

            current_page += batch_size

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
