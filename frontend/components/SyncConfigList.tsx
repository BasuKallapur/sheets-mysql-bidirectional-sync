interface SyncConfig {
  id: string;
  sheet_id: string;
  sheet_name: string;
  table_name: string;
  is_active: boolean;
  created_at: string;
}

interface SyncConfigListProps {
  configs: SyncConfig[];
  onConfigSelected: (config: SyncConfig) => void;
  onManualSync: () => void;
}

export default function SyncConfigList({
  configs,
  onConfigSelected,
  onManualSync,
}: SyncConfigListProps) {
  if (configs.length === 0) {
    return (
      <div className="text-center py-8">
        <div className="text-gray-500 mb-4">No sync configurations found</div>
        <p className="text-sm text-gray-400">
          Create your first sync configuration above
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {configs.map((config) => (
        <div
          key={config.id}
          className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 cursor-pointer transition-colors"
          onClick={() => onConfigSelected(config)}
        >
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <h3 className="font-medium text-gray-900">
                {config.sheet_name} ↔ {config.table_name}
              </h3>
              <p className="text-sm text-gray-500 mt-1">
                Sheet ID: {config.sheet_id.substring(0, 20)}...
              </p>
              <p className="text-xs text-gray-400 mt-1">
                Created: {new Date(config.created_at).toLocaleDateString()}
              </p>
            </div>
            <div className="flex items-center space-x-2">
              <span
                className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
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
      ))}

      <div className="pt-4 border-t border-gray-200">
        <button
          onClick={onManualSync}
          className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition-colors"
        >
          🔄 Trigger Manual Sync for All
        </button>
      </div>
    </div>
  );
}
