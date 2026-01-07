document.addEventListener("DOMContentLoaded", () => {

    const root = document.getElementById("product-detail-root");
    if (!root) return;

    const slug = root.dataset.slug || root.dataset.productSlug;
    if (!slug) {
        console.error("slug not found on root element");
        return;
    }

    // ===== Product Detail =====
    fetch(`/api/product-detail/${slug}/`)
        .then(res => {
            if (!res.ok) throw new Error("product api error");
            return res.json();
        })
        .then(product => {
            renderMainDetail(product);
            renderGallery(product);
            renderTabs(product);
            bindAddToCart();
        })
        .catch(err => console.error(err));

    // ===== Prev / Next =====
    fetch("/product/api/products/")
        .then(res => res.json())
        .then(products => renderPrevNext(products, slug))
        .catch(err => console.error(err));
});

/* ================= Notification ================= */

function showSuccessNotification(message) {
    const old = document.querySelector(".cart-notification");
    if (old) old.remove();

    const div = document.createElement("div");
    div.className = "cart-notification";
    div.innerText = message;

    div.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: #28a745;
        color: #fff;
        padding: 14px 22px;
        border-radius: 8px;
        font-size: 14px;
        z-index: 9999;
        box-shadow: 0 8px 20px rgba(0,0,0,.15);
    `;

    document.body.appendChild(div);
    setTimeout(() => div.remove(), 3000);
}

/* ================= Main Detail ================= */

function renderMainDetail(product) {

    const nameEl = document.querySelector(".details-name a");
    if (nameEl) nameEl.textContent = product.title;

    const idEl = document.querySelector(".details-meta p:first-child span");
    if (idEl) idEl.textContent = product.id;

    const weightEl = document.querySelector(".product-weight span");
    if (weightEl) {
        weightEl.textContent = product.weight
            ? `${product.weight} گرم`
            : "ثبت نشده";
    }

    const addBtn = document.querySelector(".product-add");
    if (addBtn) {
        addBtn.dataset.productId = product.id;
    }

    const priceEl = document.querySelector(".details-price");
    if (priceEl) {
        const price = Number(product.price);
        const discount = Number(product.discount_price || 0);

        priceEl.innerHTML = discount
            ? `<del>${price.toLocaleString()} ریال</del>
               <span>${discount.toLocaleString()} ریال</span>`
            : `<span>${price.toLocaleString()} ریال</span>`;
    }

    const descEl = document.querySelector(".details-desc");
    if (descEl) descEl.innerHTML = product.description || "";
}

/* ================= Add To Cart ================= */

function bindAddToCart() {
    const addBtn = document.querySelector(".product-add");
    if (!addBtn) return;

    addBtn.onclick = () => {
        if (addBtn.disabled) return;

        const productId = addBtn.dataset.productId;
        const qtyInput = document.querySelector("#quantity");
        const quantity = qtyInput ? parseInt(qtyInput.value, 10) || 1 : 1;

        const originalText = addBtn.innerHTML;

        fetch("/cart/api/cart/add/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({
                product_id: productId,
                quantity: quantity
            })
        })
        .then(res => {
            if (!res.ok) throw new Error();
            return res.json();
        })
        .then(() => {
            showSuccessNotification("با موفقیت به سبد خرید اضافه شد");

            addBtn.disabled = true;
            addBtn.innerHTML = "به سبد خرید اضافه شد ✅";

            document.dispatchEvent(new CustomEvent("cart:updated"));

            setTimeout(() => {
                addBtn.disabled = false;
                addBtn.innerHTML = originalText;
            }, 3000);
        });
    };
}

/* ================= Gallery ================= */

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

/* ================= Tabs (Description + Features) ================= */

function renderTabs(product) {

    // --- Description ---
    const tabDesc = document.querySelector("#tab-desc .tab-descrip");
    if (tabDesc) {
        tabDesc.innerHTML = product.description || "<p>توضیحی وجود ندارد</p>";
    }

    // --- Features / Specs ---
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
        specBody.innerHTML = `
            <tr>
                <td colspan="2">ویژگی‌ای ثبت نشده</td>
            </tr>
        `;
    }
}

/* ================= Prev / Next ================= */

function renderPrevNext(products, currentSlug) {
    const index = products.findIndex(p => p.slug === currentSlug);
    if (index === -1) return;

    updateNav(".product-nav-prev", products[index - 1]);
    updateNav(".product-nav-next", products[index + 1]);
}

function updateNav(selector, product) {
    const el = document.querySelector(selector);
    if (!el || !product) {
        el && (el.style.display = "none");
        return;
    }

    el.style.display = "";
    el.querySelector("a").href = `/product/product-detail/${product.slug}/`;
    el.querySelector("img").src = product.image;
    el.querySelector("small").textContent = product.title;
}
