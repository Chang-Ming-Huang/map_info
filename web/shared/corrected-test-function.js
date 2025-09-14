/**
 * 修正版的測試函數 - 包含郵件測試
 * 請用這個函數替換您 Apps Script 中的 testFormSubmission 函數
 */
function testFormSubmission() {
  const testData = {
    name: '測試客戶',
    phone: '0912-345-678',
    message: '我想了解系統傢俱的設計和報價，希望能安排時間討論。'
  };

  console.log('🧪 開始測試表單提交功能...');

  try {
    // 1. 測試資料寫入
    console.log('步驟 1: 測試資料寫入 Google Sheets...');
    const success = writeToSheet({
      ...testData,
      timestamp: new Date()
    });

    if (success) {
      console.log('✅ 步驟 1 成功：資料已寫入 Google Sheets');
    } else {
      console.log('❌ 步驟 1 失敗：資料寫入失敗');
      return '資料寫入測試失敗';
    }

    // 2. 測試郵件發送 (這是之前缺少的部分！)
    console.log('步驟 2: 測試郵件發送功能...');

    try {
      sendNotificationEmail({
        ...testData,
        timestamp: new Date()
      });
      console.log('✅ 步驟 2 成功：郵件發送指令執行完畢');
      console.log('📬 請檢查您的郵件收件箱 (jmhuagn8829@gmail.com)');
    } catch (emailError) {
      console.error('❌ 步驟 2 失敗：郵件發送錯誤');
      console.error('郵件錯誤詳情:', emailError.toString());
      return `郵件發送測試失敗: ${emailError.toString()}`;
    }

    console.log('🎉 完整測試成功！請檢查 Google Sheets 和郵件收件箱');
    return '完整測試成功！資料寫入 ✅ 郵件發送 ✅';

  } catch (error) {
    console.error('❌ 測試過程發生錯誤:', error);
    return `測試失敗: ${error.toString()}`;
  }
}