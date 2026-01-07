document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const searchDropdown = document.getElementById('searchDropdown');
    const searchResults = document.getElementById('searchResults');
    const searchForm = document.getElementById('searchForm');

    let searchTimeout;
    let toastTimeout;

    createToastContainer();

    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
    });

    searchInput.addEventListener('input', function() {
        const query = this.value.trim();

        clearTimeout(searchTimeout);

        if (query.length === 0) {
            hideDropdown();
            return;
        }

        if (query.length < 2) {
            hideDropdown();
            showToast('حداقل 2 کاراکتر وارد کنید', 'info');
            return;
        }

        searchTimeout = setTimeout(() => {
            performSearch(query);
        }, 500);
    });

    function performSearch(query) {
        fetch(`/api/api/search/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                if (data.results.length === 0) {
                    hideDropdown();
                    showToast('محصولی یافت نشد', 'info');
                } else {
                    displayResults(data.results);
                }
            })
            .catch(error => {
                console.error('خطا در جستجو:', error);
                hideDropdown();
                showToast('خطا در جستجو. دوباره تلاش کنید', 'error');
            });
    }

    function displayResults(products) {
        let html = '';
        products.forEach(product => {
            const priceHtml = product.discount_price ?
                `<span class="original-price">${formatPrice(product.price)}</span>
                 <span class="final-price">${formatPrice(product.final_price)}</span>` :
                `<span class="final-price">${formatPrice(product.price)}</span>`;

            const availabilityClass = product.is_available ? 'available' : 'unavailable';
            const availabilityText = product.is_available ? 'موجود' : 'ناموجود';

            html += `
                <a href="${product.detail_url}" class="search-item">
                    <div class="search-item-img">
                        <img src="${product.image}" alt="${product.title}">
                    </div>
                    <div class="search-item-info">
                        <h6 class="search-item-title">${product.title}</h6>
                        <div class="search-item-meta">
                            <div class="search-item-price">
                                ${priceHtml}
                            </div>
                            <span class="search-item-stock ${availabilityClass}">
                                ${availabilityText}
                            </span>
                        </div>
                    </div>
                </a>
            `;
        });

        searchResults.innerHTML = html;
        showDropdown();
    }

    function showDropdown() {
        searchDropdown.classList.add('show');
    }

    function hideDropdown() {
        searchDropdown.classList.remove('show');
        searchResults.innerHTML = '';
    }

    function formatPrice(price) {
        return new Intl.NumberFormat('fa-IR').format(price) + ' ریال';
    }

    function createToastContainer() {
        if (!document.getElementById('searchToast')) {
            const toast = document.createElement('div');
            toast.id = 'searchToast';
            toast.className = 'search-toast';
            document.body.appendChild(toast);
        }
    }

    function showToast(message, type = 'info') {
        const toast = document.getElementById('searchToast');
        const icon = type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle';

        toast.className = `search-toast ${type}`;
        toast.innerHTML = `
            <i class="fas ${icon}"></i>
            <p>${message}</p>
        `;

        toast.classList.add('show');

        clearTimeout(toastTimeout);
        toastTimeout = setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }

    document.addEventListener('click', function(e) {
        if (!e.target.closest('.search-wrapper')) {
            hideDropdown();
        }
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            hideDropdown();
        }
    });
});
