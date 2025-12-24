class CheckoutManager {
    constructor() {
        this.selectedAddress = null;
        this.couponCode = null;
        this.init();
    }

    init() {
        this.loadAddresses();
        this.loadCartSummary();
        this.setupEventListeners();
    }

    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    setupEventListeners() {
        document.getElementById('apply-coupon')?.addEventListener('click', () => {
            this.applyCoupon();
        });

        document.getElementById('checkout-btn')?.addEventListener('click', () => {
            this.checkout();
        });
    }

    async loadAddresses() {
        try {
            const response = await fetch('/api/account/addresses/');
            const addresses = await response.json();

            if (addresses && addresses.length > 0) {
                this.renderAddresses(addresses);
                this.selectedAddress = addresses.find(a => a.is_default) || addresses[0];
            } else {
                document.getElementById('addresses-list').innerHTML =
                    '<p>آدرسی ثبت نشده است. <a href="/accounts/profile/#addresses">اضافه کردن آدرس</a></p>';
            }
        } catch (error) {
            console.error('خطا در دریافت آدرس‌ها:', error);
            alert('خطا در دریافت آدرس‌ها');
        }
    }

    renderAddresses(addresses) {
        const container = document.getElementById('addresses-list');
        container.innerHTML = addresses.map(addr => `
            <div class="address-item ${addr.is_default ? 'default' : ''}" 
                 data-address-id="${addr.id}">
                <h6>${addr.title}</h6>
                <p>${addr.full_address}</p>
                ${addr.is_default ? '<span class="badge bg-primary">پیش‌فرض</span>' : ''}
            </div>
        `).join('');

        container.querySelectorAll('.address-item').forEach(item => {
            item.addEventListener('click', (e) => {
                container.querySelectorAll('.address-item').forEach(el =>
                    el.classList.remove('selected'));
                e.currentTarget.classList.add('selected');
                this.selectedAddress = addresses.find(
                    a => a.id == e.currentTarget.dataset.addressId
                );
            });
        });
    }

    async loadCartSummary() {
        try {
            const response = await fetch('/api/cart/');
            const data = await response.json();

            document.getElementById('subtotal').textContent =
                `${data.total_price.toLocaleString()} تومان`;
            document.getElementById('total').textContent =
                `${data.total_price.toLocaleString()} تومان`;
        } catch (error) {
            console.error('خطا در دریافت سبد:', error);
        }
    }

    async applyCoupon() {
        const couponInput = document.getElementById('coupon-code');
        const code = couponInput.value.trim();

        if (!code) {
            alert('لطفاً کد تخفیف را وارد کنید');
            return;
        }

        try {
            const response = await fetch('/orders/validate-coupon/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({ code })
            });

            const result = await response.json();

            if (result.valid) {
                this.couponCode = code;
                document.getElementById('discount').textContent =
                    `-${result.discount_amount.toLocaleString()} تومان`;
                document.getElementById('total').textContent =
                    `${result.final_total.toLocaleString()} تومان`;
                alert(result.message);
            } else {
                alert(result.message);
            }
        } catch (error) {
            console.error('خطا در اعتبارسنجی کوپن:', error);
            alert('خطا در بررسی کد تخفیف');
        }
    }

    async checkout() {
        if (!this.selectedAddress) {
            alert('لطفاً یک آدرس انتخاب کنید');
            return;
        }

        const notes = document.getElementById('order-notes')?.value || '';

        const checkoutData = {
            address_id: this.selectedAddress.id,
            coupon_code: this.couponCode || '',
            notes: notes
        };

        try {
            const response = await fetch('/orders/checkout/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(checkoutData)
            });

            const result = await response.json();

            if (response.ok && result.success) {
                alert(result.message || 'سفارش با موفقیت ثبت شد');
                window.location.href = `/orders/${result.order.id}/`;
            } else {
                const errorMsg = result.message || result.errors || 'خطا در ثبت سفارش';
                alert(errorMsg);
            }

        } catch (error) {
            console.error('خطا در ثبت سفارش:', error);
            alert('خطا در ارتباط با سرور');
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new CheckoutManager();
});
