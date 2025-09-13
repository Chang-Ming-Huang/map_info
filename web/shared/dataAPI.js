// 數據 API 類 - 用於載入最新的評論數據和圖片
class DataAPI {
    constructor() {
        this.latestJsonFile = null;
        this.reviews = [];
        this.imageBaseUrl = '';
    }

    // 獲取所有可用的 JSON 檔案列表（模擬）
    getAvailableJsonFiles() {
        // 由於瀏覽器無法直接讀取目錄，這裡我們需要預設可能的檔案名稱
        // 實際部署時可能需要服務端 API 來獲取檔案列表
        const today = new Date();
        const dateStr = today.toISOString().slice(0, 10).replace(/-/g, '');
        
        // 根據已知的檔案模式生成可能的檔案名稱
        const possibleFiles = [
            `20250913_020338.json`,
            `20250913_015556.json`, 
            `20250913_012613.json`,
            // 可以添加更多已知的檔案
        ];

        return possibleFiles;
    }

    // 根據時間戳記找到最新的 JSON 檔案
    findLatestJsonFile(fileList) {
        if (!fileList || fileList.length === 0) return null;

        // 解析檔案名稱中的時間戳記並排序
        const sortedFiles = fileList.sort((a, b) => {
            const timestampA = this.extractTimestamp(a);
            const timestampB = this.extractTimestamp(b);
            return timestampB.localeCompare(timestampA); // 降序，最新的在前
        });

        return sortedFiles[0];
    }

    // 從檔案名稱中提取時間戳記
    extractTimestamp(filename) {
        const match = filename.match(/(\d{8}_\d{6})/);
        return match ? match[1] : '00000000_000000';
    }

    // 載入最新的 JSON 數據
    async loadLatestReviews() {
        try {
            const availableFiles = this.getAvailableJsonFiles();
            this.latestJsonFile = this.findLatestJsonFile(availableFiles);
            
            if (!this.latestJsonFile) {
                throw new Error('沒有找到可用的 JSON 檔案');
            }

            // 嘗試載入 JSON 檔案
            const response = await fetch(`../../${this.latestJsonFile}`);
            
            if (!response.ok) {
                throw new Error(`載入 JSON 檔案失敗: ${response.status}`);
            }

            const data = await response.json();
            
            // 處理圖片路徑
            this.reviews = this.processReviewsData(data);
            
            console.log(`✅ 成功載入最新評論數據: ${this.latestJsonFile}`);
            console.log(`📊 共載入 ${this.reviews.length} 則評論`);
            
            return this.reviews;
            
        } catch (error) {
            console.warn('⚠️ 載入最新 JSON 數據失敗，使用備用數據:', error.message);
            return this.getFallbackReviews();
        }
    }

    // 處理評論數據，設定正確的圖片路徑
    processReviewsData(rawData) {
        if (!Array.isArray(rawData)) {
            console.error('JSON 數據格式不正確');
            return [];
        }

        return rawData.map(review => {
            // 處理圖片路徑
            const processedImages = this.processImagePaths(review);
            
            return {
                reviewer_name: review.reviewer_name || 'Anonymous',
                author_name: review.reviewer_name || 'Anonymous', // 兼容舊版本
                rating: review.rating || 5,
                review_text: review.review_text || '',
                text: review.review_text || '', // 兼容舊版本
                review_date: review.review_date || '',
                relative_time_description: review.review_date || '', // 兼容舊版本
                images: processedImages,
                total_images: review.total_images || 0,
                image_directory: review.image_directory || '',
                scraped_at: review.scraped_at || '',
                business_name: review.business_name || '築宜系統傢俱',
                location: review.location || '桃園店'
            };
        });
    }

    // 處理圖片路徑，轉換為相對於 web/style-* 的路徑
    processImagePaths(review) {
        if (!review.images || !Array.isArray(review.images)) {
            return [];
        }

        const imageDirectory = review.image_directory || '';
        
        return review.images.map(imageName => {
            // 從 web/style-*/ 到 root 的路徑是 ../../
            // 圖片在 images/timestamp/ 目錄下
            if (imageDirectory) {
                return `../../${imageDirectory}/${imageName}`;
            } else {
                // 如果沒有明確的目錄，嘗試從時間戳記推斷
                const timestamp = this.extractTimestamp(this.latestJsonFile || '');
                return `../../images/${timestamp}/${imageName}`;
            }
        });
    }

    // 備用評論數據（當無法載入真實數據時使用）
    getFallbackReviews() {
        return [
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
    }

    // 獲取評論統計信息
    getReviewStats() {
        if (!this.reviews || this.reviews.length === 0) {
            return {
                totalReviews: 0,
                averageRating: 0,
                totalImages: 0
            };
        }

        const totalReviews = this.reviews.length;
        const totalRating = this.reviews.reduce((sum, review) => sum + (review.rating || 0), 0);
        const averageRating = totalReviews > 0 ? (totalRating / totalReviews).toFixed(1) : 0;
        const totalImages = this.reviews.reduce((sum, review) => sum + (review.total_images || 0), 0);

        return {
            totalReviews,
            averageRating,
            totalImages,
            latestJsonFile: this.latestJsonFile
        };
    }
}

// 增強的 ReviewManager 類，使用 DataAPI
class EnhancedReviewManager {
    constructor() {
        this.dataAPI = new DataAPI();
        this.reviews = [];
        this.reviewsToShow = 3;
        this.reviewsPerPage = 5;
    }

    // 載入最新的評論數據
    async loadReviews() {
        try {
            this.reviews = await this.dataAPI.loadLatestReviews();
            this.reviewsToShow = 3; // Reset on new load
            return this.reviews;
        } catch (error) {
            console.error('載入評論失敗:', error);
            return [];
        }
    }

    // 顯示評論
    displayReviews(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`找不到容器: ${containerId}`);
            return;
        }

        if (!this.reviews || this.reviews.length === 0) {
            container.innerHTML = '<p style="text-align: center; color: #666;">目前沒有評論資料</p>';
            return;
        }

        const reviewsToDisplay = this.reviews.slice(0, this.reviewsToShow);

        const reviewsHTML = reviewsToDisplay.map(review => {
            const stars = '★'.repeat(review.rating || 5);
            const reviewText = review.review_text || review.text || '';
            const authorName = review.reviewer_name || review.author_name || 'Anonymous';
            const reviewDate = review.review_date || review.relative_time_description || '';

            let imageHtml = '';
            if (review.images && review.images.length > 0) {
                const imagesToShow = review.images.slice(0, 3);
                const imageElements = imagesToShow.map(imgSrc => `
                    <img src="${imgSrc}" alt="評論圖片" style="max-width: 32%; height: auto; border-radius: 8px; display: inline-block;" 
                         onerror="this.style.display='none'">
                `).join('');

                imageHtml = `
                    <div class="review-image" style="margin-top: 15px; display: flex; gap: 2%; flex-wrap: wrap;">
                        ${imageElements}
                    </div>
                    ${review.images.length > 3 ? `<p style="font-size: 0.8em; color: #666; margin-top: 5px;">+${review.images.length - 3} 張圖片</p>` : ''}
                `;
            }

            return `
                <div class="review-card">
                    <div class="review-stars">${stars}</div>
                    <p class="review-text">${reviewText}</p>
                    ${imageHtml}
                    <div class="review-author">${authorName} · ${reviewDate}</div>
                </div>
            `;
        }).join('');

        let showMoreButtonHTML = '';
        if (this.reviewsToShow < this.reviews.length) {
            showMoreButtonHTML = `<br><div style="text-align: center;"><button class="btn show-more-reviews" style="background: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">顯示更多評論</button></div>`;
        }

        container.innerHTML = reviewsHTML + showMoreButtonHTML;

        if (typeof setupReviewTruncation === 'function') {
            setupReviewTruncation(container);
        }
        
        const showMoreBtn = container.querySelector('.show-more-reviews');
        if (showMoreBtn) {
            showMoreBtn.onclick = () => this.showMoreReviews(containerId);
        }
    }

    showMoreReviews(containerId) {
        this.reviewsToShow += this.reviewsPerPage;
        this.displayReviews(containerId);
    }

    // 獲取統計信息
    async getStats() {
        if (this.reviews.length === 0) {
            await this.loadReviews();
        }
        return this.dataAPI.getReviewStats();
    }
}

// 向後兼容：保持原有的 ReviewManager 類名可用
class ReviewManager extends EnhancedReviewManager {
    constructor() {
        super();
    }
}

// 自動初始化和測試函數
async function testDataAPI() {
    console.log('🧪 測試 DataAPI...');
    
    const dataAPI = new DataAPI();
    const reviews = await dataAPI.loadLatestReviews();
    const stats = dataAPI.getReviewStats();
    
    console.log('📊 評論統計:', stats);
    console.log('📝 評論數據樣本:', reviews.slice(0, 2));
    
    return { reviews, stats };
}

// 如果在開發環境中，可以啟用測試
if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
    // 自動測試（僅在本地開發時）
    document.addEventListener('DOMContentLoaded', () => {
        setTimeout(() => {
            testDataAPI();
        }, 1000);
    });
}