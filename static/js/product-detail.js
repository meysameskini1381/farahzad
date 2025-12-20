document.addEventListener("DOMContentLoaded", () => {

    const root = document.getElementById("product-detail-root");
    if (!root) return;

    const slug = root.dataset.slug || root.dataset.productSlug;
    if (!slug) {
        console.error("slug not found on root element");
        return;
    }

    // ===============================
    // LOAD PRODUCT DETAIL
    // ===============================
    fetch(`/api/product-detail/${slug}/`)
        .then(res => {
            if (!res.ok) throw new Error("product api error");
            return res.json();
        })
        .then(product => {
            renderMainDetail(product);
            renderGallery(product);
            renderTabs(product);
        })
        .catch(err => console.error(err));

    // ===============================
    // PREV / NEXT
    // ===============================
    fetch("/product/api/products/")
        .then(res => res.json())
        .then(products => renderPrevNext(products, slug))
        .catch(err => console.error(err));
});


// ==================================================
// MAIN DETAIL
// ==================================================
function renderMainDetail(product) {

    document.querySelector(".details-name a") &&
        (document.querySelector(".details-name a").textContent = product.title);

    document.querySelector(".details-meta span") &&
        (document.querySelector(".details-meta span").textContent = product.id);

    const priceEl = document.querySelector(".details-price");
    if (!priceEl) return;

    const price = Number(product.price);
    const discount = Number(product.discount_price || 0);

    priceEl.innerHTML = discount
        ? `
            <del>${price.toLocaleString()} ريال</del>
            <span>${discount.toLocaleString()} ريال<small>/هر کیلو</small></span>
          `
        : `
            <span>${price.toLocaleString()} ريال<small>/هر کیلو</small></span>
          `;

    const descEl = document.querySelector(".details-desc");
    if (descEl) descEl.innerHTML = product.description || "";
}


// ==================================================
// GALLERY
// ==================================================
function renderGallery(product) {

    const grid = document.querySelector(".product-grid");
    if (!grid) return;

    grid.innerHTML = "";

    if (!product.gallery || product.gallery.length === 0) {
        grid.innerHTML = `<img src="/static/images/product/01.jpg">`;
        return;
    }

    product.gallery
        .sort((a, b) => b.is_main - a.is_main)
        .forEach(item => {
            const img = document.createElement("img");
            img.src = item.image;
            img.alt = product.title;
            grid.appendChild(img);
        });
}


// ==================================================
// TABS (ONLY DESC + SPEC)
// ==================================================
function renderTabs(product) {

    // ---------- description ----------
    const tabDesc = document.querySelector("#tab-desc .tab-descrip");
    if (tabDesc) {
        tabDesc.innerHTML = product.description || "<p>توضیحی وجود ندارد</p>";
    }

    // ---------- specs ----------
    const specBody = document.querySelector("#tab-spec table tbody");
    if (!specBody) return;

    specBody.innerHTML = "";

    if (product.features && product.features.length > 0) {
        product.features.forEach(f => {
            specBody.insertAdjacentHTML("beforeend", `
                <tr>
                    <th>${f.title}</th>
                    <td>${f.value}</td>
                </tr>
            `);
        });
    } else {
        specBody.innerHTML =
            `<tr><td colspan="2">مشخصاتی ثبت نشده</td></tr>`;
    }
}


// ==================================================
// PREV / NEXT
// ==================================================
function renderPrevNext(products, currentSlug) {

    const index = products.findIndex(p => p.slug === currentSlug);
    if (index === -1) return;

    const prev = products[index - 1];
    const next = products[index + 1];

    updateNav(".product-nav-prev", prev);
    updateNav(".product-nav-next", next);
}

function updateNav(selector, product) {

    const el = document.querySelector(selector);
    if (!el) return;

    if (!product) {
        el.style.display = "none";
        return;
    }

    el.querySelector("a").href =
        `/product/product-detail/${product.slug}/`;
    el.querySelector("img").src = product.image;
    el.querySelector("small").textContent = product.title;
}
