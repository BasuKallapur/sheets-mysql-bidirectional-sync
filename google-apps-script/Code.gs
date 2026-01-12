/**
 * Complete Google Apps Script for Superjoin Real-time Sync
 * Copy this entire code to your Google Apps Script editor
 */

// ⚠️ IMPORTANT: Update this URL with your deployed backend URL
const CONFIG = {
  BACKEND_URL: "https://superjoin-sync-production.railway.app", // ← YOUR ACTUAL URL!
  API_KEY: "", // Optional: add if you implement authentication
  SYNC_ENDPOINT: "/apps-script-sync",
  MAX_RETRIES: 3,
  RETRY_DELAY: 1000,
};

/**
 * Main trigger - fires when sheet is edited
 */
function onEdit(e) {
  console.log("Sheet edited, triggering real-time sync...");

  try {
    const editInfo = {
      range: e.range.getA1Notation(),
      sheet: e.source.getActiveSheet().getName(),
      user: Session.getActiveUser().getEmail(),
      timestamp: new Date().toISOString(),
      editType: "EDIT",
      oldValue: e.oldValue || "",
      newValue: e.value || "",
    };

    console.log("Edit details:", editInfo);
    triggerSyncWithRetry(editInfo);
  } catch (error) {
    console.error("Error in onEdit:", error);
    showNotification("❌ Sync error: " + error.toString());
  }
}

/**
 * Trigger sync with retry logic
 */
function triggerSyncWithRetry(editInfo, retryCount = 0) {
  try {
    const sheetId = SpreadsheetApp.getActiveSpreadsheet().getId();

    const payload = {
      sheet_id: sheetId,
      edit_info: editInfo,
      trigger_source: "apps_script",
      timestamp: new Date().toISOString(),
    };

    console.log("Sending sync request:", payload);

    const response = UrlFetchApp.fetch(
      CONFIG.BACKEND_URL + CONFIG.SYNC_ENDPOINT,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "User-Agent": "GoogleAppsScript-SuperjoinSync/1.0",
        },
        payload: JSON.stringify(payload),
        muteHttpExceptions: true,
      }
    );

    const responseCode = response.getResponseCode();
    const responseText = response.getContentText();

    if (responseCode === 200) {
      console.log("✅ Sync successful:", responseText);
      showNotification("✅ Sync completed successfully!");
    } else {
      throw new Error(`HTTP ${responseCode}: ${responseText}`);
    }
  } catch (error) {
    console.error(`Sync attempt ${retryCount + 1} failed:`, error);

    if (retryCount < CONFIG.MAX_RETRIES) {
      console.log(`Retrying in ${CONFIG.RETRY_DELAY}ms...`);
      Utilities.sleep(CONFIG.RETRY_DELAY);
      triggerSyncWithRetry(editInfo, retryCount + 1);
    } else {
      console.error("❌ Max retries exceeded");
      showNotification(
        "❌ Sync failed after " + CONFIG.MAX_RETRIES + " retries"
      );
      logError("triggerSync", error.toString());
    }
  }
}

/**
 * Manual sync function
 */
function manualSync() {
  console.log("🔄 Manual sync triggered");

  const manualInfo = {
    range: "MANUAL_TRIGGER",
    sheet: SpreadsheetApp.getActiveSheet().getName(),
    user: Session.getActiveUser().getEmail(),
    timestamp: new Date().toISOString(),
    editType: "MANUAL",
  };

  showNotification("🔄 Manual sync started...");
  triggerSyncWithRetry(manualInfo);
}

/**
 * Test backend connection
 */
function testConnection() {
  console.log("🧪 Testing backend connection...");

  try {
    const response = UrlFetchApp.fetch(CONFIG.BACKEND_URL + "/health", {
      method: "GET",
      muteHttpExceptions: true,
    });

    if (response.getResponseCode() === 200) {
      const data = JSON.parse(response.getContentText());
      console.log("✅ Backend connection successful:", data);
      showNotification("✅ Backend connection successful!");
    } else {
      throw new Error(`Backend returned ${response.getResponseCode()}`);
    }
  } catch (error) {
    console.error("❌ Connection test failed:", error);
    showNotification("❌ Backend connection failed: " + error.toString());
  }
}

/**
 * Setup triggers - run this once after pasting the code
 */
function setupTriggers() {
  console.log("📡 Setting up triggers...");

  try {
    // Delete existing triggers
    const triggers = ScriptApp.getProjectTriggers();
    triggers.forEach((trigger) => {
      ScriptApp.deleteTrigger(trigger);
    });

    console.log("✅ Triggers setup completed");
    showNotification("✅ Apps Script triggers installed successfully!");
  } catch (error) {
    console.error("❌ Failed to setup triggers:", error);
    showNotification("❌ Failed to setup triggers: " + error.toString());
  }
}

/**
 * Show notification in Google Sheets
 */
function showNotification(message) {
  try {
    SpreadsheetApp.getActiveSpreadsheet().toast(message, "Superjoin Sync", 3);
  } catch (error) {
    console.log("Notification:", message);
  }
}

/**
 * Log errors to a sheet
 */
function logError(source, error) {
  try {
    let logSheet =
      SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Sync_Logs");

    if (!logSheet) {
      logSheet = SpreadsheetApp.getActiveSpreadsheet().insertSheet("Sync_Logs");
      logSheet
        .getRange(1, 1, 1, 4)
        .setValues([["Timestamp", "Source", "Error", "User"]]);
    }

    logSheet.appendRow([
      new Date().toISOString(),
      source,
      error,
      Session.getActiveUser().getEmail(),
    ]);
  } catch (logError) {
    console.error("Failed to log error:", logError);
  }
}

/**
 * Create custom menu - runs automatically when sheet opens
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu("🔄 Superjoin Sync")
    .addItem("📡 Setup Triggers", "setupTriggers")
    .addItem("🔄 Manual Sync", "manualSync")
    .addItem("🧪 Test Connection", "testConnection")
    .addSeparator()
    .addItem("📊 View Sync Logs", "viewSyncLogs")
    .addToUi();
}

/**
 * View sync logs
 */
function viewSyncLogs() {
  const logSheet =
    SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Sync_Logs");
  if (logSheet) {
    SpreadsheetApp.setActiveSheet(logSheet);
    showNotification("📊 Viewing sync logs");
  } else {
    showNotification("📊 No sync logs found");
  }
}
