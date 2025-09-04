from urllib.parse import urljoin
from asyncio import sleep

product_selector = "ul.goodlist.cf li"

async def search_banggood(page, product, start_page=1, batch_size=2):
    results = []
    seen_urls = set()
    base_url = "https://www.banggood.com"

    for page_number in range(start_page, start_page + batch_size):
        url = f"{base_url}/search/{product}.html?page={page_number}"
        print(f"Recherche page {page_number} pour '{product}' : {url}")
        try:
            await page.goto(url, timeout=60000, wait_until="domcontentloaded")
            # --- Attendre quelques secondes que les prix chargent via JS ---
            await sleep(3)
        except Exception as e:
            print(f"Erreur lors du chargement de la page {page_number}: {e}")
            continue

        items = await page.query_selector_all(product_selector)
        if not items:
            print(f"Aucun produit trouvé sur la page {page_number}.")
            continue

        for item in items:
            # Titre
            title_el = await item.query_selector("a.title")
            title = (await title_el.inner_text()).strip() if title_el else ""
            if not title:
                continue

            # Lien
            url_item = (await title_el.get_attribute("href")).strip() if title_el else ""
            url_item = urljoin(base_url, url_item)
            if url_item in seen_urls:
                continue
            seen_urls.add(url_item)

            # Image
            img = ""
            img_el = await item.query_selector("img.lazy")
            if img_el:
                img_url = await img_el.get_attribute("data-src")
                if img_url and img_url.endswith(".webp"):
                    img = img_url

            # Prix
            price = ""
            # Sélecteur ajusté pour Banggood
            price_el = await item.query_selector("span.price-current, span.price")
            if price_el:
                price = (await price_el.inner_text()).strip()

            results.append({
                "title": title,
                "url": url_item,
                "img": img,
                "price": price
            })

    return results, start_page + batch_size - 1
