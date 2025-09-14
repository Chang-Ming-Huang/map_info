/**
 * Google Apps Script 代碼 - 處理築宜系統傢俱預約諮詢表單
 * 更新版本 - 修復 CORS 問題
 */

// 請將此 ID 替換為您的 Google Sheets ID
const SPREADSHEET_ID = '1vchMFQfQak5MblXJePH8hHT7zuKHFBbqh6EcRw6Nchc';
const SHEET_NAME = 'reservation'; // 工作表名稱

/**
 * 處理來自網站表單的 POST 請求
 */
function doPost(e) {
  console.log('收到 POST 請求');

  try {
    // 解析表單資料
    let formData;
    if (e.postData && e.postData.contents) {
      try {
        formData = JSON.parse(e.postData.contents);
        console.log('解析的表單資料:', formData);
      } catch (parseError) {
        console.error('JSON 解析錯誤:', parseError);
        return createResponse({
          status: 'error',
          message: '無效的資料格式'
        });
      }
    } else {
      console.error('沒有收到表單資料');
      return createResponse({
        status: 'error',
        message: '沒有收到表單資料'
      });
    }

    // 驗證必要欄位
    const requiredFields = ['name', 'phone', 'message'];
    const missingFields = requiredFields.filter(field => !formData[field] || formData[field].trim() === '');

    if (missingFields.length > 0) {
      console.error('缺少必要欄位:', missingFields);
      return createResponse({
        status: 'error',
        message: `缺少必要欄位: ${missingFields.join(', ')}`
      });
    }

    // 清理和驗證資料
    const cleanData = {
      name: formData.name.trim(),
      phone: formData.phone.trim(),
      message: formData.message.trim(),
      timestamp: new Date()
    };

    // 基本電話號碼驗證
    if (!/^[\d\-\(\)\s\+]+$/.test(cleanData.phone)) {
      return createResponse({
        status: 'error',
        message: '電話號碼格式不正確'
      });
    }

    // 將資料寫入 Google Sheets
    const success = writeToSheet(cleanData);

    if (success) {
      // 發送成功通知郵件（可選）
      try {
        sendNotificationEmail(cleanData);
      } catch (emailError) {
        console.error('發送郵件失敗:', emailError);
        // 郵件失敗不影響主要功能
      }

      return createResponse({
        status: 'success',
        message: '預約申請已成功提交！我們會儘快與您聯繫。',
        data: {
          name: cleanData.name,
          submissionTime: cleanData.timestamp.toLocaleString('zh-TW')
        }
      });
    } else {
      throw new Error('資料寫入失敗');
    }

  } catch (error) {
    console.error('表單處理錯誤:', error);

    return createResponse({
      status: 'error',
      message: '提交失敗，請稍後再試或直接聯繫我們。',
      error: error.toString()
    });
  }
}

/**
 * 處理 OPTIONS 預檢請求（重要：修復 CORS）
 */
function doGet(e) {
  console.log('收到 GET 請求 (OPTIONS 預檢)');
  return createResponse({
    status: 'info',
    message: '築宜系統傢俱預約表單 API 運行正常'
  });
}

/**
 * 創建回應（重要：統一 CORS 處理）
 */
function createResponse(data) {
  const response = ContentService
    .createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);

  // 重要：正確的 CORS 標頭設置
  return response.setHeaders({
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    'Access-Control-Max-Age': '3600'
  });
}

/**
 * 將資料寫入 Google Sheets
 */
function writeToSheet(data) {
  try {
    console.log('開始寫入 Google Sheets');

    // 開啟試算表
    const spreadsheet = SpreadsheetApp.openById(SPREADSHEET_ID);
    let sheet = spreadsheet.getSheetByName(SHEET_NAME);

    // 如果工作表不存在，則創建
    if (!sheet) {
      console.log('創建新工作表:', SHEET_NAME);
      sheet = spreadsheet.insertSheet(SHEET_NAME);

      // 添加表頭
      sheet.getRange(1, 1, 1, 4).setValues([['Name', 'Phone', 'Message', 'Timestamp']]);

      // 設置表頭格式
      const headerRange = sheet.getRange(1, 1, 1, 4);
      headerRange.setFontWeight('bold');
      headerRange.setBackground('#4285f4');
      headerRange.setFontColor('white');
    }

    // 準備要插入的資料行
    const rowData = [
      data.name,
      data.phone,
      data.message,
      data.timestamp.toLocaleString('zh-TW', {
        timeZone: 'Asia/Taipei',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    ];

    // 在第二行插入新資料（保持最新的在上方）
    sheet.insertRowBefore(2);
    sheet.getRange(2, 1, 1, 4).setValues([rowData]);

    // 自動調整欄寬
    sheet.autoResizeColumns(1, 4);

    console.log('✅ 資料成功寫入 Google Sheets:', data.name);
    return true;

  } catch (error) {
    console.error('❌ 寫入 Google Sheets 失敗:', error);
    return false;
  }
}

/**
 * 發送通知郵件（可選功能）
 */
function sendNotificationEmail(data) {
  try {
    // 將此郵件地址替換為您要接收通知的郵件地址
    const NOTIFICATION_EMAIL = 'jmhuagn8829@gmail.com';

    if (NOTIFICATION_EMAIL === 'your-email@example.com') {
      console.log('未設置通知郵件地址，跳過郵件通知');
      return;
    }

    const subject = '[築宜系統傢俱] 新的預約諮詢申請';
    const body = `
親愛的築宜團隊，

您收到一筆新的預約諮詢申請：

客戶姓名：${data.name}
聯絡電話：${data.phone}
需求說明：${data.message}
提交時間：${data.timestamp.toLocaleString('zh-TW')}

請儘快與客戶聯繫。

此郵件由系統自動發送，請勿直接回覆。
    `;

    MailApp.sendEmail(NOTIFICATION_EMAIL, subject, body);
    console.log('✅ 通知郵件已發送至:', NOTIFICATION_EMAIL);

  } catch (error) {
    console.error('❌ 發送通知郵件失敗:', error);
    // 即使郵件發送失敗，也不影響主要功能
  }
}

/**
 * 測試函數 - 在 Apps Script 編輯器中運行此函數來測試功能
 */
function testFormSubmission() {
  const testData = {
    name: '測試客戶',
    phone: '0912-345-678',
    message: '我想了解系統傢俱的設計和報價，希望能安排時間討論。'
  };

  console.log('🧪 開始測試表單提交功能...');

  const success = writeToSheet({
    ...testData,
    timestamp: new Date()
  });

  if (success) {
    console.log('✅ 測試成功！資料已寫入 Google Sheets');
    return '測試成功';
  } else {
    console.log('❌ 測試失敗！請檢查 SPREADSHEET_ID 設置');
    return '測試失敗';
  }
}

/**
 * 獲取試算表資訊（用於設置驗證）
 */
function getSpreadsheetInfo() {
  try {
    const spreadsheet = SpreadsheetApp.openById(SPREADSHEET_ID);
    const info = {
      name: spreadsheet.getName(),
      id: spreadsheet.getId(),
      url: spreadsheet.getUrl(),
      sheets: spreadsheet.getSheets().map(sheet => sheet.getName())
    };

    console.log('📊 試算表資訊:', info);
    return info;
  } catch (error) {
    console.error('❌ 無法訪問試算表:', error);
    return null;
  }
}

/**
 * 測試 CORS 設置
 */
function testCORS() {
  console.log('🌐 測試 CORS 設置...');

  const testResponse = createResponse({
    status: 'success',
    message: 'CORS 設置測試成功',
    timestamp: new Date().toISOString()
  });

  console.log('✅ CORS 測試完成');
  return testResponse;
}