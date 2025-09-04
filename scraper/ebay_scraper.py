from urllib.parse import urlparse

product_selector = "li.s-card--horizontal"

async def search_ebay(page, product, start_page=1, batch_size=4):
    results = []
    last_page = start_page

    for page_number in range(start_page, start_page + batch_size):
        url = f"https://www.ebay.com/sch/i.html?_nkw={product}&_pgn={page_number}"
        print(f"Recherche page {page_number} pour '{product}' : {url}")
        await page.goto(url, timeout=60000)

        items = await page.query_selector_all(product_selector)

        if not items:
            print(f"⚠️ Aucun produit trouvé sur la page {page_number}. Arrêt du scraping Ebay")
            continue  # on essaie quand même les autres pages du batch

        for item in items:
            title_el = await item.query_selector("div.s-card__title")
            title = (await title_el.inner_text()).strip() if title_el else ""
            if not title or "Shop on eBay" in title:
                continue

            link_el = await item.query_selector("a.image-treatment")
            url_item = (await link_el.get_attribute("href")).strip() if link_el else ""
            if url_item:
                parsed = urlparse(url_item)
                url_item = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

            price_el = await item.query_selector("span.su-styled-text.primary.bold.large-1.s-card__price")
            price_text = (await price_el.inner_text()).strip() if price_el else ""
            price = None
            try:
                price = float(price_text.replace("$","").replace(",","").split()[0])
            except:
                continue

            img_el = await item.query_selector(".s-card__image")
            img = (await img_el.get_attribute("src")).strip() if img_el else ""

            results.append({
                "title": title,
                "url": url_item,
                "price": price,
                "img": img
            })

        last_page = page_number

    return results, last_page
