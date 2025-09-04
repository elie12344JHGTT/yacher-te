from .ebay_scraper import scrape_ebay
from .search_banggood import scrape_alibaba
from .kikuu_scraper import scrape_kikuu


def scrape_all(query, max_results=10):
    results = {}

    ebay_results = scrape_ebay(query, max_results)
    results["eBay"] = ebay_results

    alibaba_results = scrape_alibaba(query, max_results)
    results["Alibaba"] = alibaba_results

    kikuu_results = scrape_kikuu(query, max_results)
    results["Kikuu"] = kikuu_results

    total = sum(len(lst) for lst in results.values())
    print(f"TOTAL : {total} résultats au total")

    return results
