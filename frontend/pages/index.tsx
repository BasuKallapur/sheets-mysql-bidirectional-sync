import { useState, useEffect } from "react";
import axios from "axios";
import SyncConfigForm from "../components/SyncConfigForm";
import SyncConfigList from "../components/SyncConfigList";
import SyncMonitor from "../components/SyncMonitor";
import AppsScriptIntegration from "../components/AppsScriptIntegration";

interface SyncConfig {
  id: string;
  sheet_id: string;
  sheet_name: string;
  table_name: string;
  is_active: boolean;
  created_at: string;
}

const API_BASE = "http://localhost:8000";

export default function Home() {
  const [configs, setConfigs] = useState<SyncConfig[]>([]);
  const [selectedConfig, setSelectedConfig] = useState<SyncConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<"dashboard" | "apps-script">(
    "dashboard"
  );

  const fetchConfigs = async () => {
    try {
      const response = await axios.get(`${API_BASE}/sync`);
      setConfigs(response.data);
      setError(null);
    } catch (err) {
      setError("Failed to fetch sync configurations");
      console.error("Error fetching configs:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConfigs();
  }, []);

  const handleConfigCreated = (newConfig: SyncConfig) => {
    setConfigs([...configs, newConfig]);
  };

  const handleManualSync = async () => {
    try {
      const response = await axios.post(`${API_BASE}/manual-sync`);
      if (response.status === 200) {
        alert("Manual sync triggered successfully!");
      } else {
        alert("Failed to trigger manual sync");
      }
    } catch (err) {
      alert("Failed to trigger manual sync");
      console.error("Manual sync error:", err);
    }
  };

  const handleSheetToDbSync = async () => {
    try {
      const response = await axios.post(`${API_BASE}/sync-sheet-to-db`);
      if (response.status === 200) {
        alert("Sheet → Database sync completed!");
      } else {
        alert("Failed to sync Sheet → Database");
      }
    } catch (err) {
      alert("Failed to sync Sheet → Database");
      console.error("Sheet to DB sync error:", err);
    }
  };

  const handleDbToSheetSync = async () => {
    try {
      const response = await axios.post(`${API_BASE}/sync-db-to-sheet`);
      if (response.status === 200) {
        alert("Database → Sheet sync completed!");
      } else {
        alert("Failed to sync Database → Sheet");
      }
    } catch (err) {
      alert("Failed to sync Database → Sheet");
      console.error("DB to Sheet sync error:", err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">
              Superjoin Sync Dashboard
            </h1>
            <p className="mt-2 text-gray-600">
              Real-time bidirectional sync between Google Sheets and MySQL
              Database with Apps Script Integration
            </p>
          </div>

          {/* Tab Navigation */}
          <div className="mb-6">
            <nav className="flex space-x-8">
              <button
                onClick={() => setActiveTab("dashboard")}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === "dashboard"
                    ? "border-blue-500 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                📊 Sync Dashboard
              </button>
              <button
                onClick={() => setActiveTab("apps-script")}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === "apps-script"
                    ? "border-blue-500 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                🚀 Apps Script Integration
              </button>
            </nav>
          </div>

          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 rounded-md p-4">
              <div className="flex">
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">Error</h3>
                  <div className="mt-2 text-sm text-red-700">{error}</div>
                </div>
              </div>
            </div>
          )}

          {/* Tab Content */}
          {activeTab === "dashboard" && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              <div className="space-y-6">
                <div className="bg-white shadow rounded-lg p-6">
                  <h2 className="text-lg font-medium text-gray-900 mb-4">
                    Create New Sync Configuration
                  </h2>
                  <SyncConfigForm onConfigCreated={handleConfigCreated} />
                </div>

                <div className="bg-white shadow rounded-lg p-6">
                  <h2 className="text-lg font-medium text-gray-900 mb-4">
                    Sync Configurations ({configs.length})
                  </h2>
                  <SyncConfigList
                    configs={configs}
                    onConfigSelected={setSelectedConfig}
                    onManualSync={handleManualSync}
                  />

                  {/* Separate Sync Controls */}
                  <div className="mt-6 pt-6 border-t border-gray-200">
                    <h3 className="text-md font-medium text-gray-900 mb-3">
                      Manual Sync Controls
                    </h3>
                    <div className="space-y-2">
                      <button
                        onClick={handleSheetToDbSync}
                        className="w-full bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 text-sm"
                      >
                        📊 Sheet → Database
                      </button>
                      <button
                        onClick={handleDbToSheetSync}
                        className="w-full bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 text-sm"
                      >
                        🗄️ Database → Sheet
                      </button>
                      <button
                        onClick={handleManualSync}
                        className="w-full bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 text-sm"
                      >
                        🔄 Bidirectional Sync
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">
                  Real-time Sync Monitor
                </h2>
                {selectedConfig ? (
                  <SyncMonitor config={selectedConfig} />
                ) : (
                  <div className="text-center py-12">
                    <div className="text-gray-500 mb-4">
                      Select a sync configuration to monitor real-time updates
                    </div>
                    <button
                      onClick={handleManualSync}
                      className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                    >
                      Trigger Manual Sync
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}

          {activeTab === "apps-script" && (
            <AppsScriptIntegration backendUrl={API_BASE} />
          )}
        </div>
      </div>
    </div>
  );
}
