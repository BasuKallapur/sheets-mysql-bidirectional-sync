import { useState, useEffect } from "react";
import axios from "axios";
import SyncConfigForm from "../components/SyncConfigForm";
import SyncConfigList from "../components/SyncConfigList";
import SyncMonitor from "../components/SyncMonitor";

interface SyncConfig {
  id: string;
  sheet_id: string;
  sheet_name: string;
  table_name: string;
  column_mapping: Record<string, string>;
  is_active: boolean;
  created_at: string;
}

export default function Home() {
  const [configs, setConfigs] = useState<SyncConfig[]>([]);
  const [selectedConfig, setSelectedConfig] = useState<SyncConfig | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchConfigs = async () => {
    try {
      const response = await axios.get("/api/sync/configurations");
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

  const handleConfigDeleted = (configId: string) => {
    setConfigs(configs.filter((c) => c.id !== configId));
    if (selectedConfig?.id === configId) {
      setSelectedConfig(null);
    }
  };

  const handleManualSync = async (configId: string) => {
    try {
      await axios.post(`/api/sync/configurations/${configId}/manual-sync`);
      alert("Manual sync triggered successfully!");
    } catch (err) {
      alert("Failed to trigger manual sync");
      console.error("Manual sync error:", err);
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
            </p>
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
                  Sync Configurations
                </h2>
                <SyncConfigList
                  configs={configs}
                  onConfigDeleted={handleConfigDeleted}
                  onConfigSelected={setSelectedConfig}
                  onManualSync={handleManualSync}
                />
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
                  <p className="text-gray-500">
                    Select a sync configuration to monitor real-time updates
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
