import { useState, useEffect, useRef } from "react";

interface SyncConfig {
  id: string;
  sheet_id: string;
  sheet_name: string;
  table_name: string;
  column_mapping: Record<string, string>;
  is_active: boolean;
  created_at: string;
}

interface SyncMonitorProps {
  config: SyncConfig;
}

interface SyncUpdate {
  type: string;
  source?: string;
  rows_updated?: number;
  timestamp: string;
  message?: string;
}

export default function SyncMonitor({ config }: SyncMonitorProps) {
  const [updates, setUpdates] = useState<SyncUpdate[]>([]);
  const [connectionStatus, setConnectionStatus] = useState<
    "connecting" | "connected" | "disconnected"
  >("connecting");
  const [logs, setLogs] = useState<any[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Connect to WebSocket
    const connectWebSocket = () => {
      const wsUrl = `ws://localhost:8000/api/sync/ws/${config.id}`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setConnectionStatus("connected");
        console.log("WebSocket connected");
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setUpdates((prev) => [data, ...prev.slice(0, 49)]); // Keep last 50 updates
        } catch (err) {
          console.error("Error parsing WebSocket message:", err);
        }
      };

      ws.onclose = () => {
        setConnectionStatus("disconnected");
        console.log("WebSocket disconnected");
        // Attempt to reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };

      ws.onerror = (error) => {
        console.error("WebSocket error:", error);
        setConnectionStatus("disconnected");
      };

      wsRef.current = ws;
    };

    connectWebSocket();

    // Fetch sync logs
    const fetchLogs = async () => {
      try {
        const response = await fetch(
          `/api/sync/configurations/${config.id}/logs`
        );
        const logsData = await response.json();
        setLogs(logsData);
      } catch (err) {
        console.error("Error fetching logs:", err);
      }
    };

    fetchLogs();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [config.id]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "connected":
        return "text-green-600";
      case "connecting":
        return "text-yellow-600";
      case "disconnected":
        return "text-red-600";
      default:
        return "text-gray-600";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "connected":
        return "🟢";
      case "connecting":
        return "🟡";
      case "disconnected":
        return "🔴";
      default:
        return "⚪";
    }
  };

  return (
    <div className="space-y-6">
      {/* Connection Status */}
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium text-gray-900">
            Connection Status
          </h3>
          <div
            className={`flex items-center space-x-2 ${getStatusColor(
              connectionStatus
            )}`}
          >
            <span>{getStatusIcon(connectionStatus)}</span>
            <span className="text-sm font-medium capitalize">
              {connectionStatus}
            </span>
          </div>
        </div>
        <div className="mt-2 text-sm text-gray-600">
          <p>Sheet: {config.sheet_name}</p>
          <p>Table: {config.table_name}</p>
        </div>
      </div>

      {/* Real-time Updates */}
      <div>
        <h3 className="text-sm font-medium text-gray-900 mb-3">
          Real-time Updates
        </h3>
        <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
          {updates.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-4">
              No updates yet. Make changes to your sheet or database to see
              real-time sync.
            </p>
          ) : (
            <div className="space-y-2">
              {updates.map((update, index) => (
                <div
                  key={index}
                  className="bg-white rounded p-3 border-l-4 border-blue-400"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-900">
                      {update.type === "sync_update"
                        ? "Sync Update"
                        : update.type}
                    </span>
                    <span className="text-xs text-gray-500">
                      {new Date(update.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                  {update.source && (
                    <p className="text-sm text-gray-600 mt-1">
                      Source: {update.source} • Rows: {update.rows_updated || 0}
                    </p>
                  )}
                  {update.message && (
                    <p className="text-sm text-gray-600 mt-1">
                      {update.message}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Sync Logs */}
      <div>
        <h3 className="text-sm font-medium text-gray-900 mb-3">
          Recent Sync Logs
        </h3>
        <div className="bg-gray-50 rounded-lg p-4 max-h-64 overflow-y-auto">
          {logs.length === 0 ? (
            <p className="text-sm text-gray-500 text-center py-4">
              No sync logs available
            </p>
          ) : (
            <div className="space-y-2">
              {logs.map((log) => (
                <div key={log.id} className="bg-white rounded p-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                          log.status === "SUCCESS"
                            ? "bg-green-100 text-green-800"
                            : "bg-red-100 text-red-800"
                        }`}
                      >
                        {log.status}
                      </span>
                      <span className="text-sm text-gray-900">
                        {log.operation_type}
                      </span>
                      <span className="text-sm text-gray-500">
                        from {log.source}
                      </span>
                    </div>
                    <span className="text-xs text-gray-500">
                      {new Date(log.timestamp).toLocaleString()}
                    </span>
                  </div>
                  {log.error_message && (
                    <p className="text-sm text-red-600 mt-2">
                      {log.error_message}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
