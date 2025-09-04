from urllib.parse import urlparse

product_selector = "li.searchGoods-item___3gN71"

async def search_kikuu(page, product, start_page=1, batch_size=4):
    results = []
    seen_urls = set()  # éviter les doublons
    last_page = start_page

    for page_number in range(start_page, start_page + batch_size):
        url = f"https://www.kikuu.com/search/result?kw={product}&_pgn={page_number}"
        print(f"Recherche page {page_number} pour '{product}' : {url}")
        await page.goto(url, timeout=60000)

        items = await page.query_selector_all(product_selector)

        if not items:
            print(f"Aucun produit trouvé sur la page {page_number}. Arrêt du scraping Kikuu.")
            return results, last_page  # stop net au lieu de continuer

        for item in items:
            # 🔹 Titre
            title_el = await item.query_selector("p.searchGoods-name___2Sm89")
            title = (await title_el.inner_text()).strip() if title_el else ""
            if not title or "Shop on kikuu" in title:
                continue

            # 🔹 URL
            link_el = await item.query_selector("a.searchGoods-link___3-nXo.clearfix___1FncU")
            url_item = (await link_el.get_attribute("href")).strip() if link_el else ""
            if url_item:
                base_url = "https://www.kikuu.com"
                parsed = urlparse(url_item)
                if not parsed.netloc:  # lien relatif
                    url_item = base_url + url_item
                else:
                    url_item = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

                if url_item in seen_urls:
                    continue
                seen_urls.add(url_item)

            # 🔹 Prix
            price_el = await item.query_selector("p.searchGoods-price___2nc3K")
            price_text = (await price_el.inner_text()).strip() if price_el else ""
            price = None
            try:
                price = float(price_text.replace("$", "").replace(",", "").split()[0])
            except:
                continue

            # 🔹 Image
            img_el = await item.query_selector("img.searchGoods-image-pic___2qjgd")
            img = (await img_el.get_attribute("src")).strip() if img_el else ""

            # 🔹 Ajouter au résultat
            results.append({
                "title": title,
                "url": url_item,
                "price": price,
                "img": img
            })

        last_page = page_number

    return results, last_page
