import asyncio
import json
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from playwright.async_api import async_playwright

from scraper.ebay_scraper import search_ebay
from scraper.kikuu_scraper import search_kikuu
from scraper.search_banggood import search_banggood

app = Flask(__name__)
app.secret_key = "super_secret_key"


# --- Scraper "classique" avec pagination ---
async def scrape_products(query, start_page=1, batch_size=1):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        scrapers = [
            ("eBay", search_ebay),
            ("Kikuu", search_kikuu),
            ("Banggood", search_banggood),
        ]

        all_results = []
        for site_name, scraper_func in scrapers:
            page = await context.new_page()
            results, _ = await scraper_func(page, query, start_page=start_page, batch_size=batch_size)
            await page.close()

            for item in results:
                all_results.append({
                    "site": site_name,
                    "title": item.get("title"),
                    "price": item.get("price"),
                    "merchant": item.get("merchant"),
                    "url": item.get("url"),
                    "img": item.get("img"),
                })

        await browser.close()
        return all_results


# --- API JSON pour pagination ---
@app.route("/api/resultats")
def api_resultats():
    query = request.args.get("query")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("limit", 60))

    if not query:
        return jsonify({"error": "Paramètre 'query' manquant"}), 400

    # Ici tu appelles ton scraper
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(scrape_products(query, start_page=page, batch_size=1))
    loop.close()

    total_results = len(results)  # tu peux aussi calculer avec une vraie valeur
    total_pages = (total_results + per_page - 1) // per_page

    # Découpe pour pagination (si tes scrapers renvoient trop)
    start = (page - 1) * per_page
    end = start + per_page
    page_results = results[start:end]

    return jsonify({
        "page": page,
        "total": total_results,
        "total_pages": total_pages,
        "results": page_results,
    })


# --- Routes HTML normales ---
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/resultat", methods=["GET", "POST"])
def resultat():
    if request.method == "POST":
        query = request.form.get("query")
        page = 1
    else:
        query = request.args.get("query")
        page = int(request.args.get("page", 1))

    if not query:
        flash("Veuillez saisir un produit à rechercher.")
        return redirect(url_for("home"))

    return render_template("resultat.html", query=query, page=page)


@app.route("/pourquoi")
def pourquoi():
    return render_template("pourquoi.html")


@app.route("/fonctionnement")
def fonctionnement():
    return render_template("fonctionnement.html")


@app.route("/nouveaux_clients")
def nouveaux_clients():
    return render_template("nouveaux_clients.html")


@app.route("/nouveaux_clients", methods=["POST"])
def nouveaux_clients_form():
    email = request.form.get("email")
    subject = request.form.get("subject")
    message = request.form.get("message")

    flash("Votre message a bien été envoyé ! Nous vous répondrons sous 2 jours ouvrés.")
    return redirect(url_for("nouveaux_clients"))


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
