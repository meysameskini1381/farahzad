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

function showNotification(message, type = 'error') {
    // حذف نوتیفیکیشن قبلی اگر وجود داشته باشد
    const existingNotif = document.querySelector('.cart-notification');
    if (existingNotif) existingNotif.remove();

    const notification = document.createElement('div');
    notification.className = `cart-notification cart-notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'error' ? '#dc3545' : '#28a745'};
        color: white;
        padding: 15px 25px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 9999;
        font-family: 'Vazir', sans-serif;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

// استایل انیمیشن
if (!document.querySelector('#cart-notification-styles')) {
    const style = document.createElement('style');
    style.id = 'cart-notification-styles';
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(400px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(400px); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
}

function addToCart(productId, btn) {
    fetch("/cart/api/cart/add/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken,
        },
        credentials: "include",
        body: JSON.stringify({ product_id: productId, quantity: 1 }),
    })
    .then(res => {
        if (res.status === 403) {
            showNotification("لطفاً ابتدا وارد حساب کاربری خود در فرحزاد شوید", 'error');
            setTimeout(() => {
                window.location.href = "/login/";
            }, 2000);
            throw new Error("Not authenticated");
        }
        if (!res.ok) {
            throw new Error(`خطا در افزودن به سبد خرید (Status ${res.status})`);
        }
        return res.json();
    })
    .then(() => {
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = "افزوده شد ✅";
        }
        showNotification("محصول با موفقیت به سبد خرید اضافه شد", 'success');
        loadCart && loadCart();
    })
    .catch(err => {
        console.error(err);
        if (err.message !== "Not authenticated") {
            showNotification(err.message || "خطا در افزودن به سبد خرید", 'error');
        }
    });
}

document.addEventListener("mousedown", function (e) {
    const btn = e.target.closest(".product-add");
    if (!btn) return;

    e.preventDefault();
    e.stopPropagation();
    e.stopImmediatePropagation();

    if (btn.disabled) return;

    const productId = btn.dataset.productId ||
                      (btn.closest(".product-card") && btn.closest(".product-card").dataset.productId);

    if (!productId) {
        console.warn("Product ID not found on DOM. Add data-product-id.");
        showNotification("خطا: شناسه محصول یافت نشد", 'error');
        return;
    }

    addToCart(productId, btn);
}, true);
