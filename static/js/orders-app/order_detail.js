// دریافت Order ID از URL
const orderId = window.location.pathname.split('/')[2];

document.addEventListener('DOMContentLoaded', function() {
    loadOrderDetail();
});


function renderOrderItems(items) {
    const tbody = document.querySelector('.checkout-items-table tbody');
    if (!tbody) return;

    tbody.innerHTML = items.map((item, index) => `
        <tr>
            <td class="table-serial"><h6>${index + 1}</h6></td>
            <td class="table-image">
                <img src="${item.product_image}" alt="${item.product_name}">
            </td>
            <td class="table-name"><h6>${item.product_name}</h6></td>
            <td class="table-price"><h6>${formatPrice(item.price)} تومان</h6></td>
            <td class="table-quantity"><h6>${item.quantity}</h6></td>
            <td class="table-total"><h6>${formatPrice(item.total_price)} تومان</h6></td>
        </tr>
    `).join('');
}

function formatPrice(price) {
    return new Intl.NumberFormat('fa-IR').format(price);
}
