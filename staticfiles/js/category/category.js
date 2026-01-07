document.addEventListener('DOMContentLoaded', function() {
    loadCategories();
});

async function loadCategories() {
    const categoryList = document.querySelector('.category-list');

    try {
        const response = await fetch('/api/api/categories/');
        const result = await response.json();

        console.log('API Response:', result);
        console.log('Categories Data:', result.data);

        if (result.status === 'success' && result.data && result.data.length > 0) {
            categoryList.innerHTML = '';
            renderCategories(result.data);
            initCategoryToggle();
        } else {
            categoryList.innerHTML = '<li class="empty-state">دسته‌بندی موجود نیست</li>';
        }
    } catch (error) {
        console.error('خطا در بارگذاری دسته‌بندی‌ها:', error);
        categoryList.innerHTML = '<li class="error-state">خطا در بارگذاری دسته‌بندی‌ها</li>';
    }
}

function renderCategories(categories) {
    const categoryList = document.querySelector('.category-list');

    categories.forEach(category => {
        const hasChildren = category.children && category.children.length > 0;

        console.log(`Category: ${category.title}, Slug: ${category.slug}, Has Children: ${hasChildren}`);

        const li = document.createElement('li');
        li.className = 'category-item';

        li.innerHTML = `
            <div class="category-header-item ${hasChildren ? 'has-dropdown' : ''}">
                <a href="/product/products-category/${category.slug}/" class="category-link">
                    <i class="${category.icon || 'flaticon-vegetable'}"></i>
                    <span class="category-name">${category.title}</span>
                </a>
                ${hasChildren ? '<i class="fas fa-chevron-down dropdown-arrow"></i>' : ''}
            </div>
            ${hasChildren ? `
                <ul class="subcategory-list">
                    ${category.children.map(child => `
                        <li class="subcategory-item">
                            <a href="/product/products-category/${child.slug}/" class="subcategory-link">
                                <i class="fas fa-angle-left"></i>
                                <span>${child.title}</span>
                            </a>
                        </li>
                    `).join('')}
                </ul>
            ` : ''}
        `;

        categoryList.appendChild(li);
    });
}

function initCategoryToggle() {
    const headers = document.querySelectorAll('.category-header-item.has-dropdown');

    headers.forEach(header => {
        const arrow = header.querySelector('.dropdown-arrow');

        if (arrow) {
            arrow.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();

                const categoryItem = header.closest('.category-item');
                const subcategoryList = categoryItem.querySelector('.subcategory-list');

                document.querySelectorAll('.category-item').forEach(item => {
                    if (item !== categoryItem) {
                        item.classList.remove('active');
                        const otherList = item.querySelector('.subcategory-list');
                        const otherArrow = item.querySelector('.dropdown-arrow');

                        if (otherList) otherList.style.maxHeight = '0';
                        if (otherArrow) otherArrow.style.transform = 'rotate(0deg)';
                    }
                });

                const isActive = categoryItem.classList.toggle('active');

                arrow.style.transform = isActive ? 'rotate(180deg)' : 'rotate(0deg)';

                if (subcategoryList) {
                    subcategoryList.style.maxHeight = isActive
                        ? subcategoryList.scrollHeight + 'px'
                        : '0';
                }
            });
        }
    });
}
