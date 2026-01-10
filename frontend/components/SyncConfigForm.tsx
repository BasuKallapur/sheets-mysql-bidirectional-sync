import { useState } from "react";
import axios from "axios";

interface SyncConfigFormProps {
  onConfigCreated: (config: any) => void;
}

export default function SyncConfigForm({
  onConfigCreated,
}: SyncConfigFormProps) {
  const [formData, setFormData] = useState({
    sheet_id: "",
    sheet_name: "",
    table_name: "",
    column_mapping: "{}",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Parse column mapping
      let columnMapping = {};
      try {
        columnMapping = JSON.parse(formData.column_mapping);
      } catch {
        throw new Error("Invalid JSON in column mapping");
      }

      const payload = {
        sheet_id: formData.sheet_id,
        sheet_name: formData.sheet_name,
        table_name: formData.table_name,
        column_mapping: columnMapping,
      };

      const response = await axios.post("/api/sync/configurations", payload);
      onConfigCreated(response.data);

      // Reset form
      setFormData({
        sheet_id: "",
        sheet_name: "",
        table_name: "",
        column_mapping: "{}",
      });

      alert("Sync configuration created successfully!");
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          err.message ||
          "Failed to create configuration"
      );
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-md p-3">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      <div>
        <label
          htmlFor="sheet_id"
          className="block text-sm font-medium text-gray-700"
        >
          Google Sheet ID
        </label>
        <input
          type="text"
          name="sheet_id"
          id="sheet_id"
          required
          value={formData.sheet_id}
          onChange={handleInputChange}
          placeholder="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm px-3 py-2 border"
        />
        <p className="mt-1 text-xs text-gray-500">
          Extract from the Google Sheet URL
        </p>
      </div>

      <div>
        <label
          htmlFor="sheet_name"
          className="block text-sm font-medium text-gray-700"
        >
          Sheet Name
        </label>
        <input
          type="text"
          name="sheet_name"
          id="sheet_name"
          required
          value={formData.sheet_name}
          onChange={handleInputChange}
          placeholder="Sheet1"
          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm px-3 py-2 border"
        />
      </div>

      <div>
        <label
          htmlFor="table_name"
          className="block text-sm font-medium text-gray-700"
        >
          MySQL Table Name
        </label>
        <input
          type="text"
          name="table_name"
          id="table_name"
          required
          value={formData.table_name}
          onChange={handleInputChange}
          placeholder="my_data_table"
          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm px-3 py-2 border"
        />
      </div>

      <div>
        <label
          htmlFor="column_mapping"
          className="block text-sm font-medium text-gray-700"
        >
          Column Mapping (JSON)
        </label>
        <textarea
          name="column_mapping"
          id="column_mapping"
          rows={4}
          value={formData.column_mapping}
          onChange={handleInputChange}
          placeholder='{"Name": "name", "Email": "email", "Age": "age"}'
          className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm px-3 py-2 border"
        />
        <p className="mt-1 text-xs text-gray-500">
          Map sheet column names to database column names
        </p>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
      >
        {loading ? "Creating..." : "Create Sync Configuration"}
      </button>
    </form>
  );
}
