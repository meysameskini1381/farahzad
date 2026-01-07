// static/js/orders_list.js

(function() {
    'use strict';

    const OrdersList = {
        // تنظیمات
        config: {
            apiUrl: '/orders/api/my-orders/',
            currentPage: 1,
            pageSize: 10,
            statusFilter: '',
            isLoading: false,
        },

        // المان‌ها
        elements: {},

        // مقداردهی اولیه
        init() {
            console.log('🚀 OrdersList Starting...');

            // ذخیره المان‌ها
            this.elements = {
                tbody: document.getElementById('orders-tbody'),
                loading: document.getElementById('orders-loading'),
                emptyState: document.getElementById('orders-empty'),
                tableContainer: document.getElementById('orders-table-container'),
                pagination: document.getElementById('orders-pagination'),
                pageInfo: document.getElementById('page-info'),
                paginationList: document.getElementById('pagination-list'),
                pageSizeSelect: document.getElementById('page-size-select'),
                statusFilter: document.getElementById('status-filter'),
            };

            console.log('📦 Elements:', Object.keys(this.elements).filter(k => this.elements[k]));

            // بررسی المان‌ها
            const missing = Object.keys(this.elements).filter(k => !this.elements[k]);
            if (missing.length > 0) {
                console.error('❌ Missing elements:', missing);
                return;
            }

            // رفع مشکل scroll anchoring
            if (this.elements.tableContainer) {
                this.elements.tableContainer.style.overflowAnchor = 'none';
            }

            this.bindEvents();

            // تاخیر کوتاه برای اطمینان از آماده بودن DOM
            setTimeout(() => this.loadOrders(), 100);
        },

        // اتصال رویدادها
        bindEvents() {
            // تغییر تعداد نمایش
            this.elements.pageSizeSelect?.addEventListener('change', (e) => {
                this.config.pageSize = parseInt(e.target.value);
                this.config.currentPage = 1;
                this.loadOrders();
            });

            // تغییر فیلتر وضعیت
            this.elements.statusFilter?.addEventListener('change', (e) => {
                this.config.statusFilter = e.target.value;
                this.config.currentPage = 1;
                this.loadOrders();
            });
        },

        // تغییر وضعیت loading
        setLoadingState(isLoading) {
            this.config.isLoading = isLoading;

            if (isLoading) {
                this.elements.loading.style.display = 'block';
                this.elements.tableContainer.style.display = 'none';
                this.elements.emptyState.style.display = 'none';
                this.elements.pagination.style.display = 'none';
            } else {
                this.elements.loading.style.display = 'none';
            }
        },

        // بارگذاری سفارشات
        async loadOrders() {
            if (this.config.isLoading) {
                console.log('⏳ Already loading...');
                return;
            }

            console.log('📡 Loading Orders...');
            console.log('  Page:', this.config.currentPage);
            console.log('  Size:', this.config.pageSize);
            console.log('  Status:', this.config.statusFilter || 'all');

            this.setLoadingState(true);

            // ساخت URL
            const params = new URLSearchParams({
                page: this.config.currentPage,
                page_size: this.config.pageSize,
            });

            if (this.config.statusFilter) {
                params.append('status', this.config.statusFilter);
            }

            const url = `${this.config.apiUrl}?${params.toString()}`;
            console.log('🌐 URL:', url);

            try {
                const response = await fetch(url, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    credentials: 'same-origin'
                });

                console.log('📥 Response Status:', response.status);

                if (!response.ok) {
                    const text = await response.text();
                    console.error('❌ Response:', text);
                    throw new Error(`HTTP ${response.status}`);
                }

                const data = await response.json();
                console.log('✅ Data received:', {
                    success: data.success,
                    orders: data.data?.orders?.length || 0,
                    total: data.data?.pagination?.total_items || 0
                });

                if (data.success && data.data) {
                    this.renderOrders(data.data.orders);
                    this.renderPagination(data.data.pagination);
                } else {
                    this.showEmpty('خطا در دریافت اطلاعات');
                }

            } catch (error) {
                console.error('💥 Error:', error);
                this.showEmpty('خطا در ارتباط با سرور');
            } finally {
                this.setLoadingState(false);
            }
        },

        // رندر سفارشات
        renderOrders(orders) {
            if (!orders || orders.length === 0) {
                this.showEmpty('هیچ سفارشی یافت نشد');
                return;
            }

            this.elements.tableContainer.style.display = 'block';
            this.elements.emptyState.style.display = 'none';

            const rows = orders.map(order => `
                <tr>
                    <th scope="row">#${this.escapeHtml(order.order_number)}</th>
                    <td>${this.escapeHtml(order.created_at_jalali)}</td>
                    <td>${order.items_count} محصول</td>
                    <td>${this.escapeHtml(order.formatted_total)} ریال</td>
                    <td>${this.getStatusBadge(order.status, order.status_display)}</td>
                    <td>
                        <a href="/orders/${order.id}/" class="btn btn-sm btn-outline-primary">
                            <i class="fas fa-eye"></i> مشاهده
                        </a>
                    </td>
                </tr>
            `).join('');

            this.elements.tbody.innerHTML = rows;
            console.log('✅ Rendered', orders.length, 'orders');
        },

        // نمایش حالت خالی
        showEmpty(message) {
            this.elements.tableContainer.style.display = 'none';
            this.elements.emptyState.style.display = 'block';
            this.elements.pagination.style.display = 'none';

            this.elements.emptyState.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-inbox fa-3x text-muted mb-3"></i>
                    <p class="text-muted">${this.escapeHtml(message)}</p>
                </div>
            `;
        },

        // دریافت badge وضعیت
        getStatusBadge(status, displayText) {
            const classes = {
                'pending': 'text-warning',
                'paid': 'text-success',
                'processing': 'text-info',
                'shipped': 'text-primary',
                'delivered': 'text-success',
                'cancelled': 'text-danger',
                'refunded': 'text-dark'
            };

            return `<span class="fw-bold ${classes[status] || 'text-secondary'}">${this.escapeHtml(displayText)}</span>`;
        },

        // رندر صفحه‌بندی
        renderPagination(pagination) {
            if (!pagination || pagination.total_pages <= 1) {
                this.elements.pagination.style.display = 'none';
                return;
            }

            this.elements.pagination.style.display = 'flex';

            // اطلاعات صفحه
            const start = ((pagination.current_page - 1) * pagination.page_size) + 1;
            const end = Math.min(pagination.current_page * pagination.page_size, pagination.total_items);
            this.elements.pageInfo.textContent = `نمایش ${start} تا ${end} از ${pagination.total_items} سفارش`;

            // دکمه‌های صفحه‌بندی
            const buttons = [];

            // دکمه قبلی
            if (pagination.has_previous) {
                buttons.push(`
                    <li class="page-item">
                        <a class="page-link" href="#" data-page="${pagination.previous_page}">
                            <i class="fas fa-chevron-right"></i>
                        </a>
                    </li>
                `);
            }

            // شماره صفحات
            this.getPageNumbers(pagination.current_page, pagination.total_pages).forEach(page => {
                if (page === '...') {
                    buttons.push('<li class="page-item disabled"><span class="page-link">...</span></li>');
                } else {
                    const active = page === pagination.current_page ? 'active' : '';
                    buttons.push(`
                        <li class="page-item ${active}">
                            <a class="page-link" href="#" data-page="${page}">${page}</a>
                        </li>
                    `);
                }
            });

            // دکمه بعدی
            if (pagination.has_next) {
                buttons.push(`
                    <li class="page-item">
                        <a class="page-link" href="#" data-page="${pagination.next_page}">
                            <i class="fas fa-chevron-left"></i>
                        </a>
                    </li>
                `);
            }

            this.elements.paginationList.innerHTML = buttons.join('');

            // اتصال رویدادها
            this.elements.paginationList.querySelectorAll('a.page-link').forEach(link => {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    const page = parseInt(e.currentTarget.dataset.page);
                    if (page && page !== this.config.currentPage) {
                        this.config.currentPage = page;
                        this.loadOrders();
                        window.scrollTo({ top: 0, behavior: 'smooth' });
                    }
                });
            });

            console.log('✅ Pagination rendered');
        },

        // محاسبه شماره صفحات
        getPageNumbers(current, total) {
            const pages = [];
            const delta = 2;

            for (let i = 1; i <= total; i++) {
                if (i === 1 || i === total || (i >= current - delta && i <= current + delta)) {
                    pages.push(i);
                } else if (pages[pages.length - 1] !== '...') {
                    pages.push('...');
                }
            }

            return pages;
        },

        // Escape HTML
        escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    };

    // اجرا
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => OrdersList.init());
    } else {
        OrdersList.init();
    }

})();
