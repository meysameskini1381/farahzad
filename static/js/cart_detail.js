/* ================= CSRF ================= */
function getCSRFToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    if (meta) return meta.content;

    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : "";
}

const CSRF_TOKEN = getCSRFToken();

/* ================= API ================= */
const API_BASE = "/cart/api/cart/";

async function apiRequest(url, method = "GET", data = null) {
    const options = {
        method: method,
        credentials: "same-origin",
        headers: {
            "X-CSRFToken": CSRF_TOKEN,
        }
    };

    if (data) {
        options.headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(data);
    }

    const res = await fetch(API_BASE + url, options);
    if (!res.ok) {
        console.error("API ERROR:", res.status, url);
        return null;
    }
    return await res.json();
}

/* ================= PRICE ================= */
function formatPrice(num) {
    return new Intl.NumberFormat("fa-IR").format(num) + " ریال";
}

/* ================= LOAD CART ================= */
async function loadCart() {
    const cart = await apiRequest("get/");
    if (cart) renderCart(cart);
}

/* ================= RENDER ================= */
function renderCart(cart) {
    const list = document.querySelector(".cart-list");
    const totalCount = document.querySelector(".cart-total span");
    const totalPrice = document.querySelector(".checkout-price");

    list.innerHTML = "";

    if (!cart.items.length) {
        list.innerHTML = "<li class='cart-item'>سبد خرید خالی است</li>";
        totalCount.textContent = "کل مورد (0)";
        totalPrice.textContent = "0 ریال";
        return;
    }

    cart.items.forEach(item => {
        const img = item.product_image ||
            "https://images.unsplash.com/photo-1579113800032-c38bd7635818?w=100";

        list.insertAdjacentHTML("beforeend", `
<li class="cart-item" data-id="${item.id}">
    <div class="cart-media">
        <a href="#"><img src="${img}" alt="${item.product_title}"></a>
        <button class="cart-delete" onclick="deleteItem(${item.id})">
            <i class="far fa-trash-alt"></i>
        </button>
    </div>

    <div class="cart-info-group">
        <div class="cart-info">
            <h6>${item.product_title}</h6>
            <p>قیمت واحد - ${formatPrice(item.price)}</p>
        </div>

        <div class="cart-action-group">
            <div class="product-action">
                <button class="action-minus" onclick="changeQty(${item.id}, ${item.quantity - 1})">
                    <i class="icofont-minus"></i>
                </button>

                <input class="action-input"
                       type="text"
                       value="${item.quantity}"
                       onchange="changeQty(${item.id}, this.value)">

                <button class="action-plus" onclick="changeQty(${item.id}, ${item.quantity + 1})">
                    <i class="icofont-plus"></i>
                </button>
            </div>
            <h6>${formatPrice(item.total_price)}</h6>
        </div>
    </div>
</li>
        `);
    });

    totalCount.textContent = `کل مورد (${cart.items.length})`;
    totalPrice.textContent = formatPrice(cart.total_price);
}

/* ================= UPDATE ================= */
async function changeQty(itemId, qty) {
    qty = parseInt(qty);
    if (qty <= 0) {
        deleteItem(itemId);
        return;
    }

    const res = await apiRequest(`update/${itemId}/`, "PATCH", {
        quantity: qty
    });

    if (res) loadCart();
}

/* ================= DELETE ================= */
async function deleteItem(itemId) {
    const res = await apiRequest(`delete/${itemId}/`, "DELETE");
    if (res) loadCart();
}

/* ================= ADD ================= */
async function addToCart(productId, qty = 1) {
    const res = await apiRequest("add/", "POST", {
        product_id: productId,
        quantity: qty
    });
    if (res) loadCart();
}

/* ================= INIT ================= */
document.addEventListener("DOMContentLoaded", () => {
    if (document.querySelector(".cart-sidebar")) {
        loadCart();
    }
});

/* ================= GLOBAL ================= */
window.addToCart = addToCart;
window.changeQty = changeQty;
window.deleteItem = deleteItem;
