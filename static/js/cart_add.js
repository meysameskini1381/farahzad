console.log("SHOP-CART JS LOADED ✅");

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        for (let cookie of document.cookie.split(";")) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie("csrftoken");

function addToCart(productId, btn) {
    fetch("/cart/api/cart/add/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
        },
        credentials: "same-origin",    // 🔴 اضافه شد برای ارسال session cookie
        body: JSON.stringify({ product_id: productId, quantity: 1 }),
    })
    .then(res => {
        if (!res.ok) throw new Error(`ADD FAILED → Status ${res.status}`);
        return res.json();
    })
    .then(() => {
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = "افزوده شد ✅";
        }
        // اگر بخواهیم بلافاصله سبد خرید آپدیت شود
        loadCart && loadCart();
    })
    .catch(err => console.error(err));
}


document.addEventListener("mousedown", function (e) {
    const btn = e.target.closest(".product-add");
    if (!btn) return;

    e.preventDefault();
    e.stopPropagation();
    e.stopImmediatePropagation();

    if (btn.disabled) return;

    // اولویت: روی خود دکمه، بعد کارت
    const productId = btn.dataset.productId ||
                      (btn.closest(".product-card") && btn.closest(".product-card").dataset.productId);

    if (!productId) {
        console.warn("Product ID not found on DOM. Add data-product-id.");
        return;
    }

    addToCart(productId, btn);
}, true);
