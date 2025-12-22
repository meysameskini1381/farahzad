// =================================================================
// توابع کمکی: پیدا کردن Slug و CSRF
// =================================================================

// از آنجایی که لودر اصلی محصول از #product-detail-root اسلاگ را می‌خواند،
// ما هم برای کامنت‌ها از همان منبع استفاده می‌کنیم.
function getProductSlug() {
    const root = document.getElementById("product-detail-root");
    return root ? root.dataset.slug || root.dataset.productSlug : null;
}

// =================================================================
// 1. لود و نمایش نظرات (GET Request)
// =================================================================

function renderCommentItem(comment) {
    // تابعی فرضی برای رندر کردن یک کامنت به صورت HTML
    // این تابع باید توسط شما بر اساس ساختار HTML فرانت‌اند پیاده‌سازی شود.
    // ساختار اولیه:
    let repliesHtml = '';
    if (comment.replies && comment.replies.length > 0) {
        repliesHtml = `<ul class="review-list child-review-list">${comment.replies.map(renderCommentItem).join('')}</ul>`;
    }

    // تاریخ را برای نمایش بهتر فرمت می‌کنیم
    const date = new Date(comment.created_at).toLocaleDateString('fa-IR');

    return `
        <li class="review-item" data-comment-id="${comment.id}" data-name="${comment.name}">
            <div class="review-media">
                <a class="review-avatar" href="#">
                    <img src="/static/images/avatar/01.jpg" alt="${comment.name}">
                </a>
                <h5 class="review-meta">
                    <a href="#">${comment.name}</a>
                    <span>${date}</span>
                </h5>
            </div>
            <div class="review-content">
                <p>${comment.text}</p>
                <a href="javascript:void(0)" 
                   onclick="setReplyTarget(${comment.id}, '${comment.name}')" 
                   class="review-reply">
                    <i class="icofont-reply"></i> پاسخ
                </a>
            </div>
            ${repliesHtml}
        </li>
    `;
}


function renderComments(comments) {
    const commentsList = document.getElementById('comments-list');

    if (!commentsList) return;

    if (!comments || comments.length === 0) {
        commentsList.innerHTML = '<li class="p-3 text-muted">هنوز نظری ثبت نشده است.</li>';
        return;
    }

    // رندر کامنت‌های سطح اول (درختی شدن در تابع renderCommentItem مدیریت می‌شود)
    commentsList.innerHTML = comments.map(renderCommentItem).join('');
}


function fetchProductComments() {
    const slug = getProductSlug();
    if (!slug) {
        console.error("خطا: Slug محصول برای لود کامنت‌ها پیدا نشد.");
        document.getElementById('comments-list').innerHTML =
            '<li class="p-3 text-danger">خطا در بارگذاری: شناسه محصول نامعتبر.</li>';
        return;
    }

    // نمایش وضعیت بارگذاری
    document.getElementById('comments-list').innerHTML =
        '<li class="p-3 text-muted">در حال بارگذاری نظرات...</li>';

    // endpoint: /api/product-detail/slug-12/
    fetch(`/api/product-detail/${slug}/`)
        .then(res => {
            if (!res.ok) throw new Error("بارگذاری نظرات ناموفق بود.");
            return res.json();
        })
        .then(data => {
            // 'comments' را از ساختار ProductDetailSerializer می‌گیریم
            renderComments(data.comments);
            document.getElementById('comment-count').textContent = `(${data.comments.length})`;
        })
        .catch(err => {
            console.error("خطا در لود نظرات:", err);
            document.getElementById('comments-list').innerHTML =
                '<li class="p-3 text-danger">خطا در بارگذاری نظرات. جزئیات در کنسول ثبت شد.</li>';
        });
}

// =================================================================
// 2. مدیریت حالت پاسخ (Reply Mode)
// =================================================================
let replyTargetParentId = null;

window.setReplyTarget = (parentId, name) => {
    replyTargetParentId = parentId;
    document.getElementById('reply-target-name').textContent = name;
    document.getElementById('reply-info').style.display = 'block';

    // اسکرول به فرم برای شروع پاسخ‌دهی
    document.getElementById('comment-text').focus();
}

window.cancelReply = () => {
    replyTargetParentId = null;
    document.getElementById('reply-info').style.display = 'none';
}


// =================================================================
// 3. ارسال کامنت جدید (POST Request)
// =================================================================

document.addEventListener("DOMContentLoaded", () => {

    // **فراخوانی لود کامنت‌ها پس از لود شدن DOM**
    // (این تابع را می‌توانید به جای اینکه در لودر اصلی محصول صدا بزنید، اینجا بگذارید)
    fetchProductComments();


    // Listener برای فرم ثبت کامنت
    document.getElementById("comment-form")
        ?.addEventListener("submit", function (e) {

        e.preventDefault();

        // بررسی وجود csrftoken سراسری
        const csrftoken = window.csrftoken || document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];

        if (!csrftoken) {
            alert("خطا: توکن امنیتی CSRF موجود نیست. صفحه را رفرش کنید.");
            return;
        }

        const slug = getProductSlug();
        if (!slug) {
            alert("خطا: شناسه محصول برای ارسال کامنت پیدا نشد.");
            return;
        }

        // ساخت بدنه داده‌ها
        const data = {
            text: document.getElementById('comment-text').value,
            name: document.getElementById('comment-name').value,
            email: document.getElementById('comment-email').value,
            rating: document.querySelector('input[name="rating"]:checked')?.value || null, // اگر امتیازدهی اختیاری است
            parent: replyTargetParentId, // اگر در حالت ریپلای هستیم
        };

        // endpoint: /api/product/slug-12/comment/
        fetch(`/api/product/${slug}/comment/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken, // استفاده از توکن
            },
            body: JSON.stringify(data),
        })
        .then(res => {
            if (!res.ok) throw new Error("ثبت ناموفق بود. وضعیت سرور: " + res.status);
            return res.json();
        })
        .then(() => {
            // در صورت موفقیت:
            fetchProductComments();   // ری‌لود کامنت‌ها (بهتر است، اما در پروژه واقعی باید فقط کامنت جدید را اضافه کرد)
            this.reset();             // خالی کردن فرم
            cancelReply();            // خروج از حالت پاسخ‌دهی
        })
        .catch(err => {
            console.error("خطا در ارسال کامنت:", err);
            alert("خطا در ارسال نظر: " + err.message);
        });
    });
});
