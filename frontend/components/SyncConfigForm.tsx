import { useState } from "react";
import axios from "axios";

interface SyncConfigFormProps {
  onConfigCreated: (config: any) => void;
}

const API_BASE = "http://localhost:8000";

export default function SyncConfigForm({
  onConfigCreated,
}: SyncConfigFormProps) {
  const [formData, setFormData] = useState({
    sheet_id: "1ivhwRAxn5gTKlY8em_H19gP9cFD1X0WwJZ6po0cWrZI",
    sheet_name: "Sheet1",
    table_name: "employees",
    column_mapping: {
      Name: "name",
      Email: "email",
      Age: "age",
      City: "city",
    },
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_BASE}/sync`, formData);
      onConfigCreated(response.data);
      alert("Sync configuration created successfully!");
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Failed to create sync configuration"
      );
    } finally {
      setLoading(false);
    }
  };

  const handleColumnMappingChange = (sheetCol: string, dbCol: string) => {
    setFormData((prev) => ({
      ...prev,
      column_mapping: {
        ...prev.column_mapping,
        [sheetCol]: dbCol,
      },
    }));
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-3">
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Google Sheet ID
        </label>
        <input
          type="text"
          value={formData.sheet_id}
          onChange={(e) =>
            setFormData((prev) => ({ ...prev, sheet_id: e.target.value }))
          }
          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="1ivhwRAxn5gTKlY8em_H19gP9cFD1X0WwJZ6po0cWrZI"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Sheet Name
        </label>
        <input
          type="text"
          value={formData.sheet_name}
          onChange={(e) =>
            setFormData((prev) => ({ ...prev, sheet_name: e.target.value }))
          }
          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Sheet1"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700">
          Database Table Name
        </label>
        <input
          type="text"
          value={formData.table_name}
          onChange={(e) =>
            setFormData((prev) => ({ ...prev, table_name: e.target.value }))
          }
          className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="employees"
          required
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Column Mapping (Sheet → Database)
        </label>
        <div className="space-y-2">
          {Object.entries(formData.column_mapping).map(([sheetCol, dbCol]) => (
            <div key={sheetCol} className="flex space-x-2">
              <input
                type="text"
                value={sheetCol}
                onChange={(e) => {
                  const newMapping = { ...formData.column_mapping };
                  delete newMapping[sheetCol];
                  newMapping[e.target.value] = dbCol;
                  setFormData((prev) => ({
                    ...prev,
                    column_mapping: newMapping,
                  }));
                }}
                className="flex-1 border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Sheet Column"
              />
              <span className="flex items-center text-gray-500">→</span>
              <input
                type="text"
                value={dbCol}
                onChange={(e) =>
                  handleColumnMappingChange(sheetCol, e.target.value)
                }
                className="flex-1 border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="DB Column"
              />
            </div>
          ))}
        </div>
        <button
          type="button"
          onClick={() => {
            const newKey = `Column${
              Object.keys(formData.column_mapping).length + 1
            }`;
            handleColumnMappingChange(newKey, newKey.toLowerCase());
          }}
          className="mt-2 text-sm text-blue-600 hover:text-blue-800"
        >
          + Add Column Mapping
        </button>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? "Creating..." : "Create Sync Configuration"}
      </button>
    </form>
  );
}
