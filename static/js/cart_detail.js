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
    const checkoutBtn = document.getElementById('checkout-btn');

    list.innerHTML = "";

    if (!cart.items.length) {
        list.innerHTML = "<li class='cart-item'>سبد خرید شما خالی است</li>";
        totalCount.textContent = "کل مورد (0)";
        totalPrice.textContent = "0 ریال";

        if (checkoutBtn) {
            checkoutBtn.style.pointerEvents = 'none';
            checkoutBtn.style.opacity = '0.5';
        }
        return;
    }

    if (checkoutBtn) {
        checkoutBtn.style.pointerEvents = 'auto';
        checkoutBtn.style.opacity = '1';
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

/* ================= QUICK CHECKOUT ================= */
async function quickCheckout() {
    try {
        // چک کردن سبد خرید خالی
        const totalPrice = document.getElementById('checkout-price').textContent;
        if (totalPrice === '0 ریال' || totalPrice === '0') {
            alert('سبد خرید شما خالی است!');
            return;
        }

        // گرفتن آدرس‌ها
        const addressResponse = await fetch('/api/account/addresses/', {
            credentials: 'same-origin',
            headers: {
                'X-CSRFToken': CSRF_TOKEN
            }
        });

        if (!addressResponse.ok) {
            alert('خطا در دریافت آدرس‌ها');
            return;
        }

        const addresses = await addressResponse.json();

        if (!addresses || addresses.length === 0) {
            alert('لطفاً ابتدا یک آدرس اضافه کنید');
            window.location.href = '/api/account/profile-user#addresses';
            return;
        }

        // انتخاب آدرس پیش‌فرض
        const defaultAddress = addresses.find(a => a.is_default) || addresses[0];

        // ارسال درخواست ثبت سفارش
        const checkoutData = {
            address_id: defaultAddress.id,
            coupon_code: '',
            notes: ''
        };

        const response = await fetch('/orders/api/checkout/', {
            method: 'POST',
            credentials: 'same-origin',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': CSRF_TOKEN
            },
            body: JSON.stringify(checkoutData)
        });

        const result = await response.json();

        if (response.ok && result.success) {
            // پیام موفقیت و شروع شمارش معکوس
            let countdown = 5;
            const messageBox = document.createElement("div");
            messageBox.style.position = "fixed";
            messageBox.style.top = "50%";
            messageBox.style.left = "50%";
            messageBox.style.transform = "translate(-50%, -50%)";
            messageBox.style.background = "#fff";
            messageBox.style.padding = "20px 30px";
            messageBox.style.borderRadius = "10px";
            messageBox.style.boxShadow = "0 0 10px rgba(0,0,0,0.3)";
            messageBox.style.zIndex = "9999";
            messageBox.style.textAlign = "center";
            messageBox.style.fontFamily = "IRANSans, sans-serif";
            messageBox.innerHTML = `
                <h3>در حال ساخت سفارش...</h3>
                <p>شما در حال انتقال به صفحه سفارش هستید</p>
                <h2 id="count-num">${countdown}</h2>
            `;
            document.body.appendChild(messageBox);

            const interval = setInterval(() => {
                countdown--;
                document.getElementById('count-num').textContent = countdown;
                if (countdown <= 0) {
                    clearInterval(interval);
                    document.body.removeChild(messageBox);

                    if (result.order && result.order.id) {
                        window.location.href = `/orders/${result.order.id}/`;
                    } else {
                        window.location.href = '/orders/api/';
                    }
                }
            }, 1000);
        } else {
            const errorMsg = result.message || result.errors || 'خطا در ثبت سفارش';
            alert(errorMsg);
        }

    } catch (error) {
        console.error('خطا در ثبت سفارش:', error);
        alert('خطا در ارتباط با سرور');
    }
}

/* ================= CHECKOUT VALIDATION ================= */
function setupCheckoutButton() {
    const checkoutBtn = document.getElementById('checkout-btn');

    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            quickCheckout();
        });
    }
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
        setupCheckoutButton();
    }
});

/* ================= GLOBAL ================= */
window.addToCart = addToCart;
window.changeQty = changeQty;
window.deleteItem = deleteItem;
