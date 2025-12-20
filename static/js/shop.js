document.addEventListener("DOMContentLoaded", function () {

    const productList = document.getElementById("product-list");
    const paginationEl = document.getElementById("pagination");
    const pageInfoEl = document.getElementById("page-info");
    const categorySlug = window.CATEGORY_SLUG;
    const filterSelect = document.getElementById("filterSelect");


    if (!productList || !categorySlug) return;

    const PAGE_SIZE = 15;

    // وضعیت فعلی پارامترها
    let currentParams = new URLSearchParams();
    currentParams.append("category", categorySlug);

    // ---------- لود اولیه ----------
    loadProductsWithParams(1);

    // ---------- فیلتر قیمت ----------
    const priceForm = document.querySelector(".shop-widget form");

    if (priceForm) {
        const inputs = priceForm.querySelectorAll("input");
        const minInput = inputs[0];
        const maxInput = inputs[1];

        priceForm.addEventListener("submit", function (e) {
            e.preventDefault();

            const minPrice = minInput.value.trim();
            const maxPrice = maxInput.value.trim();

            if (minPrice && maxPrice && Number(minPrice) > Number(maxPrice)) {
                alert("حداقل قیمت بیشتر از حداکثر است");
                return;
            }

            currentParams = new URLSearchParams();
            currentParams.append("category", categorySlug);

            if (minPrice) currentParams.append("min_price", minPrice);
            if (maxPrice) currentParams.append("max_price", maxPrice);

            loadProductsWithParams(1);
        });
    }
   // ---------- فیلتر vip ----------
    if (filterSelect) {
    filterSelect.addEventListener("change", function () {
        const value = this.value;

        // پاک کردن همه حالت‌های قبلی
        currentParams.delete("vip");
        currentParams.delete("ordering");

        if (value === "1") {
            currentParams.set("vip", "1");
        }

        if (value === "price_asc") {
            currentParams.set("ordering", "price");
        }

        if (value === "price_desc") {
            currentParams.set("ordering", "-price");
        }

        loadProductsWithParams(1);
    });
}
    // ---------- API ----------
    function loadProductsWithParams(page) {
        currentParams.set("page", page);

        fetch(`/api/product_category/?${currentParams.toString()}`)
            .then(res => {
                if (!res.ok) throw new Error("API Error");
                return res.json();
            })
            .then(data => {
                renderProducts(data.results);
                renderPagination(data);
            })
            .catch(err => console.error(err));
    }

    // ---------- رندر محصولات ----------
    function renderProducts(products) {
        productList.innerHTML = "";

        if (!products || products.length === 0) {
            productList.innerHTML = "<p>محصولی یافت نشد</p>";
            return;
        }

        products.forEach(product => {
            productList.insertAdjacentHTML("beforeend", renderProductItem(product));
        });
    }

    // ---------- Pagination ----------
    function renderPagination(data) {
        if (!paginationEl || !pageInfoEl) return;

        paginationEl.innerHTML = "";

        const totalCount = data.count;
        const totalPages = Math.ceil(totalCount / PAGE_SIZE);
        const currentPage =
            getPageFromUrl(data.next) ||
            getPageFromUrl(data.previous) ||
            1;

        // info text
        const end = Math.min(currentPage * PAGE_SIZE, totalCount);
        pageInfoEl.innerText = `نمایش ${end} از ${totalCount} نتیجه`;

        // prev arrow
        if (data.previous) {
            paginationEl.insertAdjacentHTML("beforeend", `
                <li class="page-item">
                    <a class="page-link" href="#" data-page="${currentPage - 1}">
                        <i class="fas fa-long-arrow-alt-right"></i>
                    </a>
                </li>
            `);
        }

        // page numbers
        getPaginationRange(currentPage, totalPages).forEach(page => {
            if (page === "...") {
                paginationEl.insertAdjacentHTML("beforeend", `
                    <li class="page-item disabled">
                        <span class="page-link">...</span>
                    </li>
                `);
            } else {
                paginationEl.insertAdjacentHTML("beforeend", `
                    <li class="page-item ${page === currentPage ? "active" : ""}">
                        <a class="page-link" href="#" data-page="${page}">${page}</a>
                    </li>
                `);
            }
        });

        // next arrow
        if (data.next) {
            paginationEl.insertAdjacentHTML("beforeend", `
                <li class="page-item">
                    <a class="page-link" href="#" data-page="${currentPage + 1}">
                        <i class="fas fa-long-arrow-alt-left"></i>
                    </a>
                </li>
            `);
        }

        // click events
        paginationEl.querySelectorAll("a[data-page]").forEach(link => {
            link.addEventListener("click", function (e) {
                e.preventDefault();
                loadProductsWithParams(this.dataset.page);
            });
        });
    }

    // ---------- helpers ----------
    function getPageFromUrl(url) {
        if (!url) return null;
        return Number(new URL(url).searchParams.get("page"));
    }

    function getPaginationRange(current, total) {
        if (total <= 5) {
            return Array.from({ length: total }, (_, i) => i + 1);
        }

        if (current <= 3) {
            return [1, 2, 3, "...", total];
        }

        if (current >= total - 2) {
            return [1, "...", total - 2, total - 1, total];
        }

        return [1, "...", current - 1, current, current + 1, "...", total];
    }

});


// ==============================
// HTML یک محصول
// ==============================
function renderProductItem(product) {
    const detailUrl = `/product/product-detail/${product.slug}/`;


    return `
        <div class="col">
            <div class="product-card" data-product-id="${product.id}">
                <div class="product-media">
                    <div class="product-label">
                        ${product.vip ? '<label class="label-text bg-warning">VIP</label>' : ''}
                    </div>

                    <button class="product-wish wish">
                        <i class="fas fa-heart"></i>
                    </button>

                        <a class="product-image" href="${detailUrl}">
                            <img src="${product.image}" alt="${product.title}">
                        </a>

                    <div class="product-widget">
                        <a class="fas fa-eye" href="${detailUrl}"></a>
                    </div>
                </div>

                <div class="product-content">
                    <h6 class="product-name">
                        <a href="${detailUrl}">${product.title}</a>
                    </h6>

                    <h6 class="product-price">
                        <span>${product.price} ریال</span>
                    </h6>

                    <button type="button" class="product-add">
                        <i class="fas fa-shopping-basket"></i>
                        <span>افزودن</span>
                    </button>
                </div>
            </div>
        </div>
    `;
}
