/**
 * 專門測試郵件功能的函數
 * 請將此函數添加到您的 Google Apps Script 中
 */

function testEmailFunction() {
  console.log('🧪 開始測試郵件功能...');

  try {
    const NOTIFICATION_EMAIL = 'jmhuagn8829@gmail.com';

    console.log('📧 準備發送測試郵件到:', NOTIFICATION_EMAIL);

    const subject = '[測試] 築宜系統傢俱郵件功能測試';
    const body = `
這是一封測試郵件。

如果您收到這封郵件，代表郵件功能設定成功！

測試時間：${new Date().toLocaleString('zh-TW')}
發送者：Google Apps Script 自動系統

請勿回覆此郵件。
    `;

    // 嘗試發送郵件
    MailApp.sendEmail(NOTIFICATION_EMAIL, subject, body);

    console.log('✅ 測試郵件發送成功！');
    console.log('📬 請檢查您的收件箱（包括垃圾郵件資料夾）');

    return '測試郵件發送成功！請檢查收件箱。';

  } catch (error) {
    console.error('❌ 郵件發送失敗:', error);
    console.error('錯誤詳情:', error.toString());

    return `郵件發送失敗: ${error.toString()}`;
  }
}

/**
 * 檢查郵件權限的函數
 */
function checkEmailPermissions() {
  console.log('🔒 檢查郵件權限...');

  try {
    // 嘗試取得配額資訊（這需要郵件權限）
    const dailyQuota = MailApp.getRemainingDailyQuota();
    console.log('📊 今日剩余郵件配額:', dailyQuota);

    if (dailyQuota > 0) {
      console.log('✅ 郵件權限正常');
      return `郵件權限正常，今日還可發送 ${dailyQuota} 封郵件`;
    } else {
      console.log('⚠️ 今日郵件配額已用完');
      return '今日郵件配額已用完';
    }

  } catch (error) {
    console.error('❌ 郵件權限檢查失敗:', error);
    return `郵件權限檢查失敗: ${error.toString()}`;
  }
}

/**
 * 詳細的表單提交測試（包含詳細的郵件除錯）
 */
function detailedFormTest() {
  console.log('🔍 開始詳細的表單測試...');

  const testData = {
    name: '郵件測試客戶',
    phone: '0912-123-456',
    message: '這是郵件功能測試，如果您收到郵件通知，代表功能正常！',
    timestamp: new Date()
  };

  try {
    // 1. 測試資料寫入
    console.log('步驟 1: 測試資料寫入...');
    const writeSuccess = writeToSheet(testData);

    if (writeSuccess) {
      console.log('✅ 步驟 1 成功：資料已寫入 Google Sheets');
    } else {
      console.log('❌ 步驟 1 失敗：資料寫入失敗');
      return '資料寫入失敗';
    }

    // 2. 測試郵件發送
    console.log('步驟 2: 測試郵件發送...');

    try {
      sendNotificationEmail(testData);
      console.log('✅ 步驟 2 成功：郵件發送指令執行完畢');
    } catch (emailError) {
      console.error('❌ 步驟 2 失敗：郵件發送出錯');
      console.error('郵件錯誤詳情:', emailError);
      return `郵件發送失敗: ${emailError.toString()}`;
    }

    console.log('🎉 詳細測試完成！請檢查 Google Sheets 和郵件收件箱');
    return '詳細測試完成！請檢查結果。';

  } catch (error) {
    console.error('❌ 詳細測試失敗:', error);
    return `測試失敗: ${error.toString()}`;
  }
}