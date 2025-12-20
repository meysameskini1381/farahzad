// =========================================
// HOME + SHOP – ADD TO CART (ULTRA SAFE)
// =========================================
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
        body: JSON.stringify({
            product_id: productId,
            quantity: 1,
        }),
    })
        .then(res => {
            if (!res.ok) throw new Error("FAILED");
            return res.json();
        })
        .then(() => {
            btn.disabled = true;
            btn.innerHTML = "افزوده شد ✅";
        })
        .catch(err => {
            console.error(err);
        });
}

/**
 * ⛔️ بسیار مهم:
 * mousedown → قبل از hover / link / slider
 */
document.addEventListener(
    "mousedown",
    function (e) {

        const btn = e.target.closest(".product-add");
        if (!btn) return;

        // قطع کامل DOM / theme
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();

        if (btn.disabled) return;

        const card = btn.closest(".product-card");
        if (!card) return;

        const productId = card.dataset.productId;
        if (!productId) return;

        addToCart(productId, btn);
    },
    true


);
