import json
import subprocess
from pathlib import Path

print(">>> RUNNING NEW SHOPWISE SCRIPT <<<")

DATA_FILE = "shopwise_data.json"
OUTPUT_FILE = "shopwise.html"


def load_products():
    data_path = Path(DATA_FILE)
    print("Loading JSON from:", Path(DATA_FILE).resolve())
    if not data_path.exists():
        raise FileNotFoundError(f"{DATA_FILE} not found in {Path.cwd()}")
    with data_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_html(products):
    products_json = json.dumps(products).replace("\\/", "/")

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Shopwise</title>
<style>

    body {{
        font-family: Arial, sans-serif;
        background: #ffe6f2;
        margin: 0;
        padding: 20px;
    }}

    /* HEADER */
    .header {{
        text-align: center;
        padding: 25px 0;
        margin-bottom: 25px;

        background: linear-gradient(135deg, #ff4fa3, #ff7ac4, #ffa8d8);
        border-radius: 16px;

        box-shadow: 0 4px 12px rgba(255, 79, 163, 0.35);

        animation: fadeIn 0.8s ease-out;
    }}

    .header-title {{
        font-size: 38px;
        font-weight: 800;
        letter-spacing: 2px;
        color: white;
        margin: 0;
    }}

    .tagline {{
        margin-top: 6px;
        font-size: 16px;
        color: #ffe6f7;
        font-weight: 500;
    }}

    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(-10px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}

    /* SEARCH CONTROLS */
    .search-controls {{
        display: flex;
        justify-content: center;
        gap: 10px;
        margin-bottom: 20px;
    }}

    select, input {{
        padding: 10px;
        border: 2px solid #ff4fa3;
        border-radius: 6px;
        font-size: 16px;
        outline: none;
    }}

    button {{
        padding: 10px 16px;
        background: #ff4fa3;
        color: white;
        border: none;
        border-radius: 6px;
        font-size: 16px;
        cursor: pointer;
    }}

    button:hover {{
        background: #ff2f8f;
    }}

    /* PRODUCT GRID */
    .results-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
        gap: 12px;
    }}

    .card {{
        background: white;
        border-radius: 6px;
        padding: 12px;
        box-shadow: 0 1px 3px rgba(255, 79, 163, 0.25);
        display: flex;
        flex-direction: column;
        gap: 4px;
        transition: transform 0.1s ease-in-out;
    }}

    .card:hover {{
        transform: scale(1.02);
    }}

    .card-title {{
        font-weight: bold;
        color: #333;
        font-size: 16px;
    }}

    .card-store {{
        color: #ff4fa3;
        font-size: 14px;
        font-weight: bold;
    }}

    .card-category {{
        font-size: 13px;
        color: #777;
    }}

    .card-price {{
        font-size: 18px;
        font-weight: bold;
        margin-top: 4px;
        color: #222;
    }}

    .card a {{
        margin-top: 6px;
        text-decoration: none;
        color: white;
        background: #ff4fa3;
        padding: 8px;
        text-align: center;
        border-radius: 4px;
        font-size: 14px;
    }}

    /* POPUP */
    .popup-bg {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.5);
        display: none;
        justify-content: center;
        align-items: center;
    }}

    .popup {{
        background: white;
        padding: 20px;
        width: 350px;
        border-radius: 8px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    }}

    .popup h2 {{
        margin-top: 0;
        color: #ff4fa3;
        font-size: 22px;
    }}

    .close-btn {{
        background: #ff4fa3;
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        cursor: pointer;
        margin-top: 10px;
        display: inline-block;
    }}

    /* --- Cheapest Store Card Styles --- */
    .best-price-card {{
        background: #e8f9ee;
        border: 2px solid #28a745;
        padding: 12px;
        border-radius: 10px;
        margin-bottom: 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
    }}

    .best-price-title {{
        font-weight: 700;
        font-size: 1rem;
        color: #28a745;
        margin-bottom: 6px;
    }}

    .store-card {{
        background: #f7f7f7;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 8px;
        border: 1px solid #ddd;
    }}

    .store-name {{
        font-weight: 600;
    }}

    .store-price {{
        float: right;
        font-weight: 600;
    }}

    /* ⭐ Soft pastel pill tag ⭐ */
    .price-diff-pill {{
        display: inline-block;
        padding: 5px 14px;
        border-radius: 999px;
        background: linear-gradient(135deg, #ffe6f2, #ffd9ec);
        color: #ff2f8f;
        font-size: 13px;
        font-weight: 600;
        box-shadow: 0 2px 4px rgba(255, 79, 163, 0.15);
        margin-top: 8px;
    }}

</style>
</head>
<body>

<div class="header">
    <h1 class="header-title">SHOPWISE</h1>
    <p class="tagline">Compare prices instantly. Shop smarter, not harder.</p>
</div>

<div class="search-controls">
    <select id="category">
        <option value="">All Categories</option>
        <option value="Home Essentials">Home Essentials</option>
        <option value="Stationery">Stationery</option>
        <option value="Beauty">Beauty</option>
        <option value="Books">Books</option>
        <option value="Electronics">Electronics</option>
    </select>

    <input type="text" id="search" placeholder="Search products...">

    <button id="searchBtn">Search</button>
</div>

<div id="results" class="results-grid"></div>

<!-- POPUP -->
<div id="popup-bg" class="popup-bg">
    <div class="popup">
        <h2 id="popup-title"></h2>
        <div id="popup-content"></div>
        <div class="close-btn" onclick="closePopup()">Close</div>
    </div>
</div>

<script>
    const products = {products_json};

    function formatPrice(price) {{
        return "£" + price.toFixed(2);
    }}

    /* ⭐ FINAL POPUP WITH SOFT PASTEL PILL TAGS ⭐ */
    function openPopup(productName) {{
        const popupBg = document.getElementById("popup-bg");
        const popupTitle = document.getElementById("popup-title");
        const popupContent = document.getElementById("popup-content");

        const matches = products
            .filter(p => p.name === productName)
            .sort((a, b) => a.price - b.price);

        popupTitle.textContent = "Compare Prices: " + productName;

        const cheapest = matches[0];

        let html = ""
            + "<div class='best-price-card'>"
            +     "<div class='best-price-title'>Best Price</div>"
            +     "<div class='store-name'>" + cheapest.store + "</div>"
            +     "<div class='store-price'>£" + cheapest.price.toFixed(2) + "</div>"
            +     "<div style='clear: both;'></div>"
            +     "<a href='" + cheapest.link + "' target='_blank' style='"
            +         "display:block;"
            +         "margin-top:10px;"
            +         "background:#28a745;"
            +         "color:white;"
            +         "padding:8px;"
            +         "border-radius:6px;"
            +         "text-align:center;"
            +         "text-decoration:none;"
            +     "'>Visit Store</a>"
            + "</div>";

        for (let i = 1; i < matches.length; i++) {{
            const s = matches[i];
            const diff = s.price - cheapest.price;
            const diffLabel = "+£" + diff.toFixed(2) + " more";

            html += ""
                + "<div class='store-card'>"
                +     "<span class='store-name'>" + s.store + "</span>"
                +     "<span class='store-price'>£" + s.price.toFixed(2) + "</span>"
                +     "<div style='clear: both;'></div>"

                // ⭐ Soft pastel pill
                +     "<div class='price-diff-pill'>" + diffLabel + "</div>"

                +     "<a href='" + s.link + "' target='_blank' style='"
                +         "display:block;"
                +         "margin-top:10px;"
                +         "background:#ff4fa3;"
                +         "color:white;"
                +         "padding:6px;"
                +         "border-radius:6px;"
                +         "text-align:center;"
                +         "text-decoration:none;"
                +     "'>Visit Store</a>"
                + "</div>";
        }}

        popupContent.innerHTML = html;
        popupBg.style.display = "flex";
    }}

    function closePopup() {{
        document.getElementById("popup-bg").style.display = "none";
    }}

    function renderProducts(list) {{
        const grid = document.getElementById("results");
        grid.innerHTML = "";

        list.forEach(item => {{
            const card = document.createElement("div");
            card.className = "card";

            const title = document.createElement("div");
            title.className = "card-title";
            title.textContent = item.name;
            card.appendChild(title);

            const store = document.createElement("div");
            store.className = "card-store";
            store.textContent = item.store;
            card.appendChild(store);

            const cat = document.createElement("div");
            cat.className = "card-category";
            cat.textContent = item.category;
            card.appendChild(cat);

            const price = document.createElement("div");
            price.className = "card-price";
            price.textContent = formatPrice(item.price);
            card.appendChild(price);

            const link = document.createElement("a");
            link.href = item.link;
            link.target = "_blank";
            link.textContent = "View product";
            card.appendChild(link);

            const compareBtn = document.createElement("button");
            compareBtn.textContent = "Compare prices";
            compareBtn.style.marginTop = "6px";
            compareBtn.onclick = () => openPopup(item.name);
            card.appendChild(compareBtn);

            grid.appendChild(card);
        }});
    }}

    function applyFilters() {{
        const term = document.getElementById("search").value.toLowerCase();
        const category = document.getElementById("category").value;

        const filtered = products.filter(p => {{
            const matchesText =
                p.name.toLowerCase().includes(term) ||
                p.store.toLowerCase().includes(term);

            const matchesCategory =
                category === "" || p.category === category;

            return matchesText && matchesCategory;
        }});

        renderProducts(filtered);
    }}

    document.getElementById("searchBtn").addEventListener("click", applyFilters);
    document.getElementById("search").addEventListener("input", applyFilters);
    document.getElementById("category").addEventListener("change", applyFilters);

    renderProducts(products);
</script>

</body>
</html>
"""
    return html


def main():
    products = load_products()

    html = build_html(products)
    print(products)
    out_path = Path(OUTPUT_FILE)
    out_path.write_text(html, encoding="utf-8")
    print(f"Generated {OUTPUT_FILE} in {Path.cwd()}")

    subprocess.run(["open", "-a", "Google Chrome", str(out_path)])


if __name__ == "__main__":
    main()

















