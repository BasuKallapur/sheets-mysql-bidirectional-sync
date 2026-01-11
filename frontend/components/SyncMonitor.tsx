import { useState, useEffect } from "react";
import axios from "axios";

interface SyncConfig {
  id: string;
  sheet_id: string;
  sheet_name: string;
  table_name: string;
  is_active: boolean;
  created_at: string;
}

interface SyncMonitorProps {
  config: SyncConfig;
}

const API_BASE = "http://localhost:8000";

export default function SyncMonitor({ config }: SyncMonitorProps) {
  const [syncStatus, setSyncStatus] = useState<string>("idle");
  const [lastSync, setLastSync] = useState<Date | null>(null);
  const [syncCount, setSyncCount] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const triggerSync = async () => {
    setSyncStatus("syncing");
    setError(null);

    try {
      const response = await axios.post(`${API_BASE}/manual-sync`);
      setSyncStatus("success");
      setLastSync(new Date());
      setSyncCount((prev) => prev + 1);

      // Reset status after 3 seconds
      setTimeout(() => setSyncStatus("idle"), 3000);
    } catch (err: any) {
      setSyncStatus("error");
      setError(err.response?.data?.detail || "Sync failed");

      // Reset status after 5 seconds
      setTimeout(() => setSyncStatus("idle"), 5000);
    }
  };

  const getStatusColor = () => {
    switch (syncStatus) {
      case "syncing":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "success":
        return "bg-green-100 text-green-800 border-green-200";
      case "error":
        return "bg-red-100 text-red-800 border-red-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  const getStatusIcon = () => {
    switch (syncStatus) {
      case "syncing":
        return "🔄";
      case "success":
        return "✅";
      case "error":
        return "❌";
      default:
        return "⏸️";
    }
  };

  return (
    <div className="space-y-6">
      {/* Config Details */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h3 className="font-medium text-gray-900 mb-2">
          Configuration Details
        </h3>
        <div className="space-y-1 text-sm">
          <div>
            <span className="font-medium">Sheet:</span> {config.sheet_name}
          </div>
          <div>
            <span className="font-medium">Table:</span> {config.table_name}
          </div>
          <div>
            <span className="font-medium">Status:</span>
            <span
              className={`ml-2 px-2 py-1 rounded-full text-xs ${
                config.is_active
                  ? "bg-green-100 text-green-800"
                  : "bg-red-100 text-red-800"
              }`}
            >
              {config.is_active ? "Active" : "Inactive"}
            </span>
          </div>
        </div>
      </div>

      {/* Sync Status */}
      <div className={`border rounded-lg p-4 ${getStatusColor()}`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-lg">{getStatusIcon()}</span>
            <span className="font-medium capitalize">{syncStatus}</span>
          </div>
          {syncStatus === "syncing" && (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current"></div>
          )}
        </div>

        {error && <div className="mt-2 text-sm">{error}</div>}
      </div>

      {/* Sync Statistics */}
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-blue-50 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-blue-600">{syncCount}</div>
          <div className="text-sm text-blue-800">Manual Syncs</div>
        </div>
        <div className="bg-purple-50 rounded-lg p-4 text-center">
          <div className="text-lg font-medium text-purple-600">
            {lastSync ? lastSync.toLocaleTimeString() : "Never"}
          </div>
          <div className="text-sm text-purple-800">Last Sync</div>
        </div>
      </div>

      {/* Manual Sync Button */}
      <button
        onClick={triggerSync}
        disabled={syncStatus === "syncing"}
        className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {syncStatus === "syncing" ? "Syncing..." : "🔄 Trigger Manual Sync"}
      </button>

      {/* Instructions */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <h4 className="font-medium text-yellow-800 mb-2">
          Testing Instructions:
        </h4>
        <ol className="text-sm text-yellow-700 space-y-1 list-decimal list-inside">
          <li>Edit your Google Sheet and add/modify data</li>
          <li>Click "Trigger Manual Sync" to sync changes</li>
          <li>Open DB Browser for SQLite to view database changes</li>
          <li>Edit data in DB Browser and sync again</li>
          <li>Check Google Sheet for updated data</li>
        </ol>
      </div>
    </div>
  );
}
