// 共用工具函數 - 已整合 DataAPI 功能
// 注意：請確保同時載入 dataAPI.js

// 傳統的 ReviewManager（向後兼容）
class LegacyReviewManager {
    constructor() {
        this.reviews = [];
        this.currentPage = 1;
        this.reviewsPerPage = 6;
    }

    // 載入JSON評論資料（使用模擬資料）
    async loadReviews() {
        try {
            console.log('⚠️ 使用舊版 ReviewManager，建議升級至 DataAPI');
            
            this.reviews = [
                {
                    reviewer_name: "K C",
                    author_name: "K C",
                    rating: 5,
                    review_text: "之前看了作品集覺得Nick的風格、美感都很優質，接洽後也覺得Nick非常親切，總是很用心和我們討論提出的任何想法及需求，也給予許多裝潢上的建議，甚至不分晝夜配合我們的時間幫忙趕工，真的非常感謝🙏完工後的家也跟規劃的一樣有質感和美感，很喜歡～非常推薦Nick的設計👍🏻",
                    text: "之前看了作品集覺得Nick的風格、美感都很優質，接洽後也覺得Nick非常親切，總是很用心和我們討論提出的任何想法及需求，也給予許多裝潢上的建議，甚至不分晝夜配合我們的時間幫忙趕工，真的非常感謝🙏完工後的家也跟規劃的一樣有質感和美感，很喜歡～非常推薦Nick的設計👍🏻",
                    review_date: "1 週前",
                    relative_time_description: "1 週前",
                    images: [],
                    total_images: 0
                },
                {
                    reviewer_name: "david tai",
                    author_name: "david tai",
                    rating: 5,
                    review_text: "這次的裝潢是由Nick負責~整體專案在預算範圍內順利完成，價格控制合理，讓人感受到設計師在前期規劃的用心與專業。在施工過程中，會主動幫忙與各個工班溝通協調，讓我們省去許多來回奔波的麻煩。",
                    text: "這次的裝潢是由Nick負責~整體專案在預算範圍內順利完成，價格控制合理，讓人感受到設計師在前期規劃的用心與專業。在施工過程中，會主動幫忙與各個工班溝通協調，讓我們省去許多來回奔波的麻煩。",
                    review_date: "1 個月前",
                    relative_time_description: "1 個月前",
                    images: [],
                    total_images: 0
                },
                {
                    reviewer_name: "Trebor Fu",
                    author_name: "Trebor Fu",
                    rating: 5,
                    review_text: "本次裝潢是和Nick接洽，在有限的預算內Nick控制地很好與區分該花費與不需要花費的項目。有些我個人特別需求的客製實際做完的模樣與我想像的也差不多，冷氣的配管施作與窗簾盒的搭配也和冷氣師傅配合地很好，值得信任。",
                    text: "本次裝潢是和Nick接洽，在有限的預算內Nick控制地很好與區分該花費與不需要花費的項目。有些我個人特別需求的客製實際做完的模樣與我想像的也差不多，冷氣的配管施作與窗簾盒的搭配也和冷氣師傅配合地很好，值得信任。",
                    review_date: "5 個月前",
                    relative_time_description: "5 個月前",
                    images: [],
                    total_images: 0
                }
            ];
            return this.reviews;
        } catch (error) {
            console.error('載入評論資料失敗:', error);
            return [];
        }
    }

    // 顯示評論
    displayReviews(reviews, containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`找不到容器: ${containerId}`);
            return;
        }

        if (!reviews || reviews.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #666;">目前沒有評論資料</p>';
            return;
        }

        const reviewsHTML = reviews.slice(0, this.reviewsPerPage).map(review => {
            const stars = '★'.repeat(review.rating || 5);
            const reviewText = review.review_text || review.text || '';
            const authorName = review.reviewer_name || review.author_name || 'Anonymous';
            const reviewDate = review.review_date || review.relative_time_description || '';

            return `
                <div class="review-card">
                    <div class="review-stars">${stars}</div>
                    <p class="review-text">${reviewText}</p>
                    <div class="review-author">${authorName} · ${reviewDate}</div>
                </div>
            `;
        }).join('');

        container.innerHTML = reviewsHTML;
    }

    // 生成星級評分HTML
    generateStars(rating) {
        let stars = '';
        for (let i = 1; i <= 5; i++) {
            if (i <= rating) {
                stars += '<span class="text-yellow-400">★</span>';
            } else {
                stars += '<span class="text-gray-300">☆</span>';
            }
        }
        return stars;
    }

    // 截斷文字
    truncateText(text, maxLength = 150) {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    // 格式化日期
    formatDate(dateString) {
        return dateString; // 保持原格式
    }
}

// 智能 ReviewManager 選擇器
function createReviewManager() {
    // 檢查是否有 DataAPI 可用
    if (typeof EnhancedReviewManager !== 'undefined') {
        console.log('✅ 使用增強版 ReviewManager (含 DataAPI)');
        return new EnhancedReviewManager();
    } else {
        console.log('⚠️ DataAPI 不可用，使用傳統版 ReviewManager');
        return new LegacyReviewManager();
    }
}

// 智能 ReviewManager 工厂函数（避免重複聲明）
if (typeof ReviewManager === 'undefined') {
    // 主要的 ReviewManager 類（智能選擇實現）
    class ReviewManager extends LegacyReviewManager {
        constructor() {
            super();
            
            // 如果有 DataAPI，升級到增強版
            if (typeof EnhancedReviewManager !== 'undefined') {
                return new EnhancedReviewManager();
            }
        }
    }
    
    // 將 ReviewManager 設為全局可用
    window.ReviewManager = ReviewManager;
}

// 圖片懶加載
function setupLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('opacity-0');
                img.classList.add('opacity-100');
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
}

// 平滑滾動
function smoothScrollTo(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// 動畫效果
function animateOnScroll() {
    const elements = document.querySelectorAll('.animate-on-scroll');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in-up');
            }
        });
    }, {
        threshold: 0.1
    });

    elements.forEach(el => observer.observe(el));
}

// Lightbox功能
function initializeLightbox() {
    const lightbox = document.getElementById('lightbox');
    if (!lightbox) return;

    const lightboxImg = document.getElementById('lightbox-img');
    const closeBtn = document.getElementById('lightbox-close');
    
    let touchStartX = 0;
    let touchStartY = 0;
    let isDragging = false;

    function openLightbox(src) {
        lightboxImg.src = src;
        lightbox.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }

    function closeLightbox() {
        lightbox.style.display = 'none';
        lightboxImg.src = '';
        document.body.style.overflow = 'auto';
    }

    document.body.addEventListener('touchstart', function(e) {
        if (e.target.tagName === 'IMG' && (e.target.closest('.review-image') || e.target.closest('.review-images'))) {
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
            isDragging = false;
        }
    }, { passive: true });

    document.body.addEventListener('touchmove', function(e) {
        if (touchStartX === 0 && touchStartY === 0) return;
        const deltaX = Math.abs(e.touches[0].clientX - touchStartX);
        const deltaY = Math.abs(e.touches[0].clientY - touchStartY);
        if (deltaX > 10 || deltaY > 10) {
            isDragging = true;
        }
    }, { passive: true });

    document.body.addEventListener('touchend', function(e) {
        if (!isDragging && e.target.tagName === 'IMG' && (e.target.closest('.review-image') || e.target.closest('.review-images'))) {
            if (!e.target.closest('#lightbox')) {
                e.preventDefault();
                openLightbox(e.target.src);
            }
        }
        // Reset
        touchStartX = 0;
        touchStartY = 0;
        isDragging = false;
    });

    // Fallback for mouse clicks on desktop
    document.body.addEventListener('click', function(e) {
        // Check if it's a touch device; if so, touchend already handled it.
        if ('ontouchstart' in window) return;
        
        if (e.target.tagName === 'IMG' && (e.target.closest('.review-image') || e.target.closest('.review-images'))) {
            if (!e.target.closest('#lightbox')) {
                e.preventDefault();
                openLightbox(e.target.src);
            }
        }
    });

    closeBtn.addEventListener('click', closeLightbox);

    lightbox.addEventListener('click', function(e) {
        if (e.target === lightbox) {
            closeLightbox();
        }
    });
}

// 評論文字截斷與展開功能
function setupReviewTruncation(containerElement) {
    const TRUNCATE_CHAR_LIMIT = 80; // 可調整的字元限制

    containerElement.querySelectorAll('.review-text').forEach(textElement => {
        // 如果已經處理過，則跳過
        if (textElement.dataset.isTruncated) {
            return;
        }

        const fullText = textElement.innerHTML.trim();
        textElement.dataset.fullText = fullText;

        if (fullText.length > TRUNCATE_CHAR_LIMIT) {
            const truncatedText = fullText.substring(0, TRUNCATE_CHAR_LIMIT);
            textElement.innerHTML = `
                ${truncatedText}... 
                <a href="#" class="show-more-link" style="color: #007bff; text-decoration: none; font-weight: bold;">看全文</a>
            `;
            textElement.dataset.isTruncated = 'true';
        }
    });
}

// 初始化函數
function initializeApp() {
    setupLazyLoading();
    animateOnScroll();
    initializeLightbox(); // 初始化 lightbox
    
    // 為「看全文」連結設定全域點擊事件監聽
    document.body.addEventListener('click', function(e) {
        if (e.target.classList.contains('show-more-link')) {
            e.preventDefault();
            const textElement = e.target.closest('.review-text');
            if (textElement && textElement.dataset.fullText) {
                textElement.innerHTML = textElement.dataset.fullText;
            }
        }
    });

    // 設定平滑滾動連結
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            smoothScrollTo(targetId);
        });
    });
}

// DOM載入完成後初始化
document.addEventListener('DOMContentLoaded', initializeApp);
