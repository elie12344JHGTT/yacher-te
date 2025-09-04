document.addEventListener("DOMContentLoaded", function () {
    const resultsContainer = document.getElementById("results-list");
    const loader = document.getElementById("loader");
    const paginationContainer = document.getElementById("pagination");

    if (!resultsContainer || !query) return;

    function formatPrice(price, currency) {
        if (!price) return "Prix non indiqué";
        let strPrice = price.toString().trim();
        if (/[$€CDF]/i.test(strPrice)) return strPrice;
        let numeric = strPrice.replace(/[^0-9.,]/g, "").replace(",", ".");
        let num = parseFloat(numeric);
        if (isNaN(num)) return strPrice;
        let formatted = num.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2});
        return currency ? `${formatted} ${currency}` : `${formatted} $`;
    }

    async function loadResults(page = 1) {
        loader.style.display = "block";
        paginationContainer.innerHTML = "";

        // Garde les placeholders
        const placeholders = Array.from(resultsContainer.querySelectorAll(".placeholder"));
        placeholders.forEach(ph => ph.classList.remove("show"));

        try {
            const response = await fetch(`/api/resultats?query=${encodeURIComponent(query)}&page=${page}`);
            const data = await response.json();
            loader.style.display = "none";

            if (!data.results || data.results.length === 0) {
                resultsContainer.innerHTML = "<p>Aucun résultat trouvé.</p>";
                return;
            }

            // Remplacer les placeholders par les vrais produits
            data.results.forEach((product, index) => {
                let card;
                if (placeholders[index]) {
                    card = placeholders[index];
                    card.classList.add("product-card");
                    card.classList.remove("placeholder");
                    card.innerHTML = `
                        <img src="${product.img || '/static/img/default.jpg'}" alt="${product.title}">
                        <h3>${product.title}</h3>
                        <p class="merchant">Chez ${product.merchant || "Marchand inconnu"}</p>
                        <p class="price">${formatPrice(product.price, product.currency)}</p>
                        <a class="boutton" href="${product.url}" target="_blank"><button>Voir l’offre</button></a>
                    `;
                } else {
                    card = document.createElement("div");
                    card.className = "product-card";
                    card.innerHTML = `
                        <img src="${product.img || '/static/img/default.jpg'}" alt="${product.title}">
                        <h3>${product.title}</h3>
                        <p class="merchant">Chez ${product.merchant || "Marchand inconnu"}</p>
                        <p class="price">${formatPrice(product.price, product.currency)}</p>
                        <a class="boutton" href="${product.url}" target="_blank"><button>Voir l’offre</button></a>
                    `;
                    resultsContainer.appendChild(card);
                }
                requestAnimationFrame(() => card.classList.add("show"));
            });

            buildPagination(data.page, data.total_pages);

        } catch (err) {
            console.error("Erreur lors du chargement :", err);
            loader.innerHTML = "<p>Une erreur est survenue lors du chargement.</p>";
        }
    }

    function buildPagination(currentPage, totalPages) {
        if (totalPages <= 1) return;
        if (currentPage > 1) {
            const prevBtn = document.createElement("button");
            prevBtn.textContent = "Précédent";
            prevBtn.addEventListener("click", () => loadResults(currentPage - 1));
            paginationContainer.appendChild(prevBtn);
        }
        for (let i = 1; i <= totalPages; i++) {
            const pageBtn = document.createElement("button");
            pageBtn.textContent = i;
            if (i === currentPage) pageBtn.classList.add("active");
            pageBtn.addEventListener("click", () => loadResults(i));
            paginationContainer.appendChild(pageBtn);
        }
        if (currentPage < totalPages) {
            const nextBtn = document.createElement("button");
            nextBtn.textContent = "Suivant";
            nextBtn.addEventListener("click", () => loadResults(currentPage + 1));
            paginationContainer.appendChild(nextBtn);
        }
    }

    loadResults(initialPage || 1);

    document.querySelectorAll(".dropdown-content a").forEach(link => {
        link.addEventListener("click", function (e) {
            e.preventDefault();
            const category = this.textContent.trim();
            window.location.href = `/resultat?query=${encodeURIComponent(category)}`;
        });
    });
});
