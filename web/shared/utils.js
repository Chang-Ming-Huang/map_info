// 共用工具函數
class ReviewManager {
    constructor() {
        this.reviews = [];
        this.currentPage = 1;
        this.reviewsPerPage = 6;
    }

    // 載入JSON評論資料
    async loadReviews() {
        try {
            // 模擬資料，實際使用時會載入JSON檔案
            this.reviews = [
                {
                    reviewer_name: "K C",
                    rating: 5,
                    review_text: "之前看了作品集覺得Nick的風格、美感都很優質，接洽後也覺得Nick非常親切，總是很用心和我們討論提出的任何想法及需求，也給予許多裝潢上的建議，甚至不分晝夜配合我們的時間幫忙趕工，真的非常感謝🙏完工後的家也跟規劃的一樣有質感和美感，很喜歡～非常推薦Nick的設計👍🏻",
                    review_date: "1 週前",
                    images: ["review_002_img_01.jpg", "review_002_img_02.jpg", "review_002_img_03.jpg"],
                    total_images: 3
                },
                {
                    reviewer_name: "david tai",
                    rating: 5,
                    review_text: "這次的裝潢是由Nick負責~整體專案在預算範圍內順利完成，價格控制合理，讓人感受到設計師在前期規劃的用心與專業。在施工過程中，會主動幫忙與各個工班溝通協調，讓我們省去許多來回奔波的麻煩。",
                    review_date: "1 個月前",
                    images: ["review_003_img_01.jpg", "review_003_img_02.jpg", "review_003_img_03.jpg"],
                    total_images: 3
                },
                {
                    reviewer_name: "Trebor Fu",
                    rating: 5,
                    review_text: "本次裝潢是和Nick接洽，在有限的預算內Nick控制地很好與區分該花費與不需要花費的項目。有些我個人特別需求的客製實際做完的模樣與我想像的也差不多，冷氣的配管施作與窗簾盒的搭配也和冷氣師傅配合地很好，值得信任。",
                    review_date: "5 個月前",
                    images: ["review_004_img_01.jpg", "review_004_img_02.jpg", "review_004_img_03.jpg"],
                    total_images: 3
                }
            ];
            return this.reviews;
        } catch (error) {
            console.error('載入評論資料失敗:', error);
            return [];
        }
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
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    // 格式化日期
    formatDate(dateString) {
        return dateString; // 保持原格式
    }
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

// 初始化函數
function initializeApp() {
    setupLazyLoading();
    animateOnScroll();
    
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
