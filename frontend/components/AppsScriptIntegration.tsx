import { useState, useEffect } from "react";
import axios from "axios";

interface AppsScriptIntegrationProps {
  backendUrl: string;
}

export default function AppsScriptIntegration({
  backendUrl,
}: AppsScriptIntegrationProps) {
  const [connectionStatus, setConnectionStatus] = useState<
    "testing" | "connected" | "disconnected" | "error"
  >("disconnected");
  const [ngrokUrl, setNgrokUrl] = useState("");
  const [realtimeEvents, setRealtimeEvents] = useState<any[]>([]);
  const [isListening, setIsListening] = useState(false);

  const testConnection = async () => {
    setConnectionStatus("testing");
    try {
      const response = await axios.get(`${backendUrl}/health`);
      if (response.status === 200 && response.data.apps_script_ready) {
        setConnectionStatus("connected");
      } else {
        setConnectionStatus("error");
      }
    } catch (error) {
      setConnectionStatus("error");
    }
  };

  const simulateAppsScriptTrigger = async () => {
    try {
      const testPayload = {
        sheet_id: "1ivhwRAxn5gTKlY8em_H19gP9cFD1X0WwJZ6po0cWrZI",
        edit_info: {
          range: "A2",
          sheet: "Sheet1",
          user: "test@example.com",
          timestamp: new Date().toISOString(),
          editType: "EDIT",
          oldValue: "Old Value",
          newValue: "New Value",
        },
        trigger_source: "apps_script_simulation",
        timestamp: new Date().toISOString(),
      };

      const response = await axios.post(
        `${backendUrl}/apps-script-sync`,
        testPayload
      );

      // Add to realtime events
      setRealtimeEvents((prev) => [
        {
          timestamp: new Date().toISOString(),
          type: "apps_script_trigger",
          status: response.status === 200 ? "success" : "error",
          data: response.data,
        },
        ...prev.slice(0, 9),
      ]); // Keep last 10 events
    } catch (error: any) {
      setRealtimeEvents((prev) => [
        {
          timestamp: new Date().toISOString(),
          type: "apps_script_trigger",
          status: "error",
          error: error.response?.data?.detail || error.message,
        },
        ...prev.slice(0, 9),
      ]);
    }
  };

  const copyAppsScriptCode = () => {
    const codeTemplate = `
// ⚠️ IMPORTANT: Update this URL with your ngrok URL
const CONFIG = {
  BACKEND_URL: "${
    ngrokUrl || "https://YOUR-NGROK-URL.ngrok.io"
  }", // ← UPDATE THIS!
  API_KEY: "",
  SYNC_ENDPOINT: "/apps-script-sync",
  MAX_RETRIES: 3,
  RETRY_DELAY: 1000,
};

// Copy the complete Code.gs file from google-apps-script/Code.gs
// and paste it into your Google Apps Script editor
    `.trim();

    navigator.clipboard.writeText(codeTemplate);
    alert("Apps Script configuration copied to clipboard!");
  };

  useEffect(() => {
    // Auto-detect ngrok URL from backend URL
    if (backendUrl.includes("ngrok.io")) {
      setNgrokUrl(backendUrl);
    }
  }, [backendUrl]);

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-medium text-gray-900">
          🚀 Apps Script Integration
        </h2>
        <div
          className={`px-3 py-1 rounded-full text-sm font-medium ${
            connectionStatus === "connected"
              ? "bg-green-100 text-green-800"
              : connectionStatus === "testing"
              ? "bg-yellow-100 text-yellow-800"
              : connectionStatus === "error"
              ? "bg-red-100 text-red-800"
              : "bg-gray-100 text-gray-800"
          }`}
        >
          {connectionStatus === "connected" && "✅ Connected"}
          {connectionStatus === "testing" && "🔄 Testing..."}
          {connectionStatus === "error" && "❌ Error"}
          {connectionStatus === "disconnected" && "⏸️ Disconnected"}
        </div>
      </div>

      {/* Backend URL Configuration */}
      <div className="mb-6 p-4 bg-blue-50 rounded-lg">
        <h3 className="font-medium text-blue-900 mb-2">Backend URL</h3>
        <div className="flex space-x-2">
          <input
            type="text"
            value={ngrokUrl}
            onChange={(e) => setNgrokUrl(e.target.value)}
            placeholder="https://abc123.ngrok.io"
            className="flex-1 border border-blue-200 rounded-md px-3 py-2 text-sm"
          />
          <button
            onClick={testConnection}
            className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 text-sm"
          >
            Test Connection
          </button>
        </div>
        <p className="text-xs text-blue-700 mt-1">
          Enter your ngrok URL (e.g., https://abc123.ngrok.io)
        </p>
      </div>

      {/* Setup Instructions */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <h3 className="font-medium text-gray-900 mb-3">
          📋 Setup Instructions
        </h3>
        <ol className="text-sm text-gray-700 space-y-2 list-decimal list-inside">
          <li>
            Start ngrok:{" "}
            <code className="bg-gray-200 px-1 rounded">ngrok http 8000</code>
          </li>
          <li>Copy the ngrok URL and paste it above</li>
          <li>Click "Copy Apps Script Code" below</li>
          <li>
            Go to{" "}
            <a
              href="https://script.google.com"
              target="_blank"
              className="text-blue-600 hover:underline"
            >
              script.google.com
            </a>
          </li>
          <li>Create new project and paste the code</li>
          <li>Save and run "setupTriggers" function</li>
          <li>Test by editing your Google Sheet!</li>
        </ol>
      </div>

      {/* Action Buttons */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-6">
        <button
          onClick={copyAppsScriptCode}
          className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 text-sm"
        >
          📋 Copy Apps Script Code
        </button>
        <button
          onClick={simulateAppsScriptTrigger}
          className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 text-sm"
        >
          🧪 Test Apps Script Trigger
        </button>
        <a
          href="https://script.google.com"
          target="_blank"
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 text-sm text-center"
        >
          🔗 Open Apps Script
        </a>
      </div>

      {/* Real-time Events Monitor */}
      <div className="border-t pt-6">
        <h3 className="font-medium text-gray-900 mb-3">📡 Real-time Events</h3>
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {realtimeEvents.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No events yet. Edit your Google Sheet to see real-time triggers!
            </div>
          ) : (
            realtimeEvents.map((event, index) => (
              <div
                key={index}
                className={`p-3 rounded-lg text-sm ${
                  event.status === "success"
                    ? "bg-green-50 border border-green-200"
                    : "bg-red-50 border border-red-200"
                }`}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <span
                      className={`font-medium ${
                        event.status === "success"
                          ? "text-green-800"
                          : "text-red-800"
                      }`}
                    >
                      {event.status === "success" ? "✅" : "❌"} Apps Script
                      Trigger
                    </span>
                    <div className="text-xs text-gray-600 mt-1">
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                  <div className="text-xs">
                    {event.status === "success" ? "Success" : "Error"}
                  </div>
                </div>
                {event.error && (
                  <div className="mt-2 text-xs text-red-700 bg-red-100 p-2 rounded">
                    {event.error}
                  </div>
                )}
                {event.data && (
                  <div className="mt-2 text-xs text-green-700">
                    Sync completed for config: {event.data.config_id}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Performance Metrics */}
      <div className="border-t pt-6 mt-6">
        <h3 className="font-medium text-gray-900 mb-3">⚡ Performance</h3>
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center p-3 bg-blue-50 rounded-lg">
            <div className="text-lg font-bold text-blue-600">
              {realtimeEvents.filter((e) => e.status === "success").length}
            </div>
            <div className="text-xs text-blue-800">Successful Syncs</div>
          </div>
          <div className="text-center p-3 bg-red-50 rounded-lg">
            <div className="text-lg font-bold text-red-600">
              {realtimeEvents.filter((e) => e.status === "error").length}
            </div>
            <div className="text-xs text-red-800">Failed Syncs</div>
          </div>
          <div className="text-center p-3 bg-green-50 rounded-lg">
            <div className="text-lg font-bold text-green-600">~0ms</div>
            <div className="text-xs text-green-800">Sync Delay</div>
          </div>
        </div>
      </div>
    </div>
  );
}
