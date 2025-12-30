// Global variables
let currentEditingAddressId = null;
const addressModalElement = document.getElementById('addressModal');
let addressModal = null;

// Get CSRF Token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (addressModalElement) {
        addressModal = new bootstrap.Modal(addressModalElement);
    }

    loadProfileData();
    loadAddresses();
    loadPaymentMethods();

    const addressForm = document.getElementById('addressForm');
    if (addressForm) {
        addressForm.addEventListener('submit', handleAddressFormSubmit);
    }
});

// Load Profile Data
async function loadProfileData() {
    try {
        const response = await fetch('/api/account/profile/', {
            credentials: 'include'
        });

        if (response.status === 403) {
            window.location.href = '/login/';
            return;
        }

        if (!response.ok) throw new Error('Failed to load profile');

        const data = await response.json();

        document.getElementById('profileUsername').value = data.username || '';
        document.getElementById('profileEmail').value = data.email || '';

    } catch (error) {
        console.error('Error loading profile:', error);
        showNotification('خطا در بارگذاری اطلاعات پروفایل', 'error');
    }
}

// Load Addresses
async function loadAddresses() {
    const container = document.getElementById('addressesContainer');

    if (!container) {
        console.error('addressesContainer not found!');
        return;
    }

    try {
        const response = await fetch('/api/account/addresses/', {
            credentials: 'include'
        });

        if (response.status === 403) {
            showNotification('لطفاً ابتدا وارد حساب کاربری خود شوید', 'error');
            setTimeout(() => window.location.href = '/login/', 1500);
            return;
        }

        if (!response.ok) throw new Error('Failed to load addresses');

        const addresses = await response.json();
        renderAddresses(addresses);

    } catch (error) {
        console.error('Error loading addresses:', error);
        container.innerHTML = `
            <div class="col-12 text-center py-4">
                <p class="text-danger">خطا در بارگذاری آدرس‌ها</p>
            </div>
        `;
    }
}

// Render Addresses
function renderAddresses(addresses) {
    const container = document.getElementById('addressesContainer');

    if (!container) {
        console.error('addressesContainer not found!');
        return;
    }

    if (addresses.length === 0) {
        container.innerHTML = `
            <div class="col-12 text-center py-5">
                <i class="icofont-location-pin text-muted mb-3" style="font-size: 4rem; opacity: 0.3;"></i>
                <h5 class="text-muted">هیچ آدرسی ثبت نشده است</h5>
                <p class="text-muted">برای افزودن آدرس جدید روی دکمه "افزودن آدرس" کلیک کنید</p>
            </div>
        `;
        return;
    }

    container.innerHTML = addresses.map(address => `
        <div class="col-md-6 col-lg-4">
            <div class="profile-card address ${address.is_default ? 'active' : ''}">
                <h6>${address.title}</h6>
                <p>${address.full_address}</p>
                <ul class="user-action">
                    ${!address.is_default ? `
                        <li>
                            <button class="icofont-star" 
                                    title="تنظیم به عنوان پیش‌فرض" 
                                    onclick="setDefaultAddress(${address.id})"
                                    style="background: none; border: none; color: #ffc107; cursor: pointer;">
                            </button>
                        </li>
                    ` : ''}
                    <li>
                        <button class="edit icofont-edit" 
                                title="ویرایش" 
                                onclick="editAddress(${address.id})">
                        </button>
                    </li>
                    <li>
                        <button class="trash icofont-ui-delete" 
                                title="حذف" 
                                onclick="deleteAddress(${address.id})">
                        </button>
                    </li>
                </ul>
            </div>
        </div>
    `).join('');
}

// Load Payment Methods
async function loadPaymentMethods() {
    const container = document.getElementById('paymentMethodsContainer');
    container.innerHTML = `
        <div class="col-12 text-center py-4">
            <p class="text-muted">این بخش به زودی فعال می‌شود</p>
        </div>
    `;
}

// Open Add Address Modal
function openAddAddressModal() {
    currentEditingAddressId = null;

    document.getElementById('addressModalLabel').innerHTML = '<i class="icofont-plus-circle me-2"></i> افزودن آدرس جدید';
    document.getElementById('addressForm').reset();

    if (addressModal) {
        addressModal.show();
    }
}

// Edit Address
async function editAddress(id) {
    try {
        const response = await fetch(`/api/account/addresses/${id}/`, {
            credentials: 'include'
        });

        if (!response.ok) throw new Error('Failed to load address');

        const address = await response.json();

        currentEditingAddressId = id;
        document.getElementById('addressModalLabel').innerHTML = '<i class="icofont-edit me-2"></i> ویرایش آدرس';
        document.getElementById('addressTitle').value = address.title;
        document.getElementById('addressFull').value = address.full_address;
        document.getElementById('addressDefault').checked = address.is_default;

        if (addressModal) {
            addressModal.show();
        }

    } catch (error) {
        console.error('Error loading address:', error);
        showNotification('خطا در بارگذاری آدرس', 'error');
    }
}

// Delete Address
async function deleteAddress(id) {
    if (!confirm('آیا از حذف این آدرس اطمینان دارید؟')) {
        return;
    }

    try {
        const response = await fetch(`/api/account/addresses/${id}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrftoken
            },
            credentials: 'include'
        });

        if (!response.ok) throw new Error('Failed to delete address');

        showNotification('آدرس با موفقیت حذف شد', 'success');
        loadAddresses();

    } catch (error) {
        console.error('Error deleting address:', error);
        showNotification('خطا در حذف آدرس', 'error');
    }
}

// Set Default Address
async function setDefaultAddress(id) {
    try {
        const response = await fetch(`/api/account/addresses/${id}/`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            credentials: 'include',
            body: JSON.stringify({ is_default: true })
        });

        if (!response.ok) throw new Error('Failed to set default');

        showNotification('آدرس پیش‌فرض تنظیم شد', 'success');
        loadAddresses();

    } catch (error) {
        console.error('Error setting default:', error);
        showNotification('خطا در تنظیم آدرس پیش‌فرض', 'error');
    }
}

// Handle Address Form Submit
async function handleAddressFormSubmit(e) {
    e.preventDefault();

    const title = document.getElementById('addressTitle').value.trim();
    const fullAddress = document.getElementById('addressFull').value.trim();
    const isDefault = document.getElementById('addressDefault').checked;

    if (!title || !fullAddress) {
        showNotification('لطفاً تمام فیلدها را پر کنید', 'error');
        return;
    }

    const data = {
        title: title,
        full_address: fullAddress,
        is_default: isDefault
    };

    try {
        let url = '/api/account/addresses/';
        let method = 'POST';

        if (currentEditingAddressId) {
            url = `/api/account/addresses/${currentEditingAddressId}/`;
            method = 'PATCH';
        }

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken
            },
            credentials: 'include',
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(JSON.stringify(errorData));
        }

        showNotification('آدرس با موفقیت ذخیره شد', 'success');

        if (addressModal) {
            addressModal.hide();
        }

        loadAddresses();

    } catch (error) {
        console.error('Error saving address:', error);
        showNotification('خطا در ذخیره آدرس', 'error');
    }
}

// Show Notification
function showNotification(message, type = 'info') {
    const alertClass = type === 'error' ? 'alert-danger' : type === 'success' ? 'alert-success' : 'alert-info';

    const notification = document.createElement('div');
    notification.className = `alert ${alertClass} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
    notification.style.zIndex = '9999';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.remove();
    }, 3000);
}
