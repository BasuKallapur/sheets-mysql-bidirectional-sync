import axios from "axios";

interface SyncConfig {
  id: string;
  sheet_id: string;
  sheet_name: string;
  table_name: string;
  column_mapping: Record<string, string>;
  is_active: boolean;
  created_at: string;
}

interface SyncConfigListProps {
  configs: SyncConfig[];
  onConfigDeleted: (configId: string) => void;
  onConfigSelected: (config: SyncConfig) => void;
  onManualSync: (configId: string) => void;
}

export default function SyncConfigList({
  configs,
  onConfigDeleted,
  onConfigSelected,
  onManualSync,
}: SyncConfigListProps) {
  const handleDelete = async (configId: string) => {
    if (!confirm("Are you sure you want to delete this sync configuration?")) {
      return;
    }

    try {
      await axios.delete(`/api/sync/configurations/${configId}`);
      onConfigDeleted(configId);
      alert("Configuration deleted successfully!");
    } catch (err) {
      alert("Failed to delete configuration");
      console.error("Delete error:", err);
    }
  };

  if (configs.length === 0) {
    return (
      <div className="text-center py-6">
        <p className="text-gray-500">No sync configurations found</p>
        <p className="text-sm text-gray-400 mt-1">
          Create one above to get started
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {configs.map((config) => (
        <div
          key={config.id}
          className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
          onClick={() => onConfigSelected(config)}
        >
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <h3 className="text-sm font-medium text-gray-900">
                {config.sheet_name} ↔ {config.table_name}
              </h3>
              <p className="text-xs text-gray-500 mt-1">
                Sheet ID: {config.sheet_id.substring(0, 20)}...
              </p>
              <div className="mt-2">
                <span
                  className={`sync-status ${
                    config.is_active ? "active" : "inactive"
                  }`}
                >
                  {config.is_active ? "Active" : "Inactive"}
                </span>
              </div>
            </div>

            <div className="flex space-x-2 ml-4">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onManualSync(config.id);
                }}
                className="px-3 py-1 text-xs bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
              >
                Sync Now
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  handleDelete(config.id);
                }}
                className="px-3 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200"
              >
                Delete
              </button>
            </div>
          </div>

          <div className="mt-3 text-xs text-gray-600">
            <p>
              Column Mapping: {Object.keys(config.column_mapping).length}{" "}
              columns
            </p>
            <p>Created: {new Date(config.created_at).toLocaleDateString()}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
