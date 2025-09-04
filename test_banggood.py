import asyncio
from playwright.async_api import async_playwright
from scraper.search_banggood import search_banggood

async def main():
    product = input("Entrez le produit à rechercher sur Banggood : ")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        print(f"\n🔎 Recherche Banggood pour '{product}'...\n")

        results, last_page = await search_banggood(page, product, start_page=1, batch_size=2)

        if not results:
            print("⚠️ Aucun produit trouvé.")
        else:
            for i, r in enumerate(results, 1):
                print(f"{i}. {r['title']}")
                print(f"   Lien : {r['url']}")
                print(f"   Prix : {r['price']}")
                print(f"   Image (.webp uniquement) : {r['img']}\n")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
