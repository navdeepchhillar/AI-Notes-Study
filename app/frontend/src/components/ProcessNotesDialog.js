import { useState } from "react";
import axios from "axios";
import { X, Loader2, FileText } from "lucide-react";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ProcessNotesDialog = ({ files, onClose, onSuccess }) => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(false);

  const toggleFile = (fileId) => {
    setSelectedFiles((prev) =>
      prev.includes(fileId)
        ? prev.filter((id) => id !== fileId)
        : [...prev, fileId]
    );
  };

  const handleSubmit = async () => {
    if (selectedFiles.length === 0) {
      toast.error("Please select at least one file");
      return;
    }
    if (!title.trim()) {
      toast.error("Please enter a title");
      return;
    }

    try {
      setLoading(true);
      await axios.post(`${API}/process-notes`, {
        file_ids: selectedFiles,
        title: title.trim(),
      });
      toast.success("Combined notes created successfully!");
      onSuccess();
    } catch (e) {
      console.error("Error processing notes:", e);
      toast.error("Failed to create combined notes");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div
        data-testid="process-notes-dialog"
        className="bg-white border-2 border-black rounded-xl shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] max-w-2xl w-full max-h-[90vh] overflow-hidden"
      >
        <div className="border-b-2 border-black bg-[#A3E6D0] p-6 flex items-center justify-between">
          <h2 className="text-2xl sm:text-3xl tracking-tight font-bold" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
            Create Combined Notes
          </h2>
          <button
            data-testid="close-dialog"
            onClick={onClose}
            className="p-2 hover:bg-black hover:text-white transition-colors border-2 border-black rounded-md"
          >
            <X className="w-6 h-6" strokeWidth={3} />
          </button>
        </div>

        <div className="p-6 overflow-y-auto max-h-[calc(90vh-200px)]">
          <div className="mb-6">
            <label className="block text-xs uppercase tracking-[0.2em] font-bold mb-2">
              Title
            </label>
            <input
              data-testid="notes-title-input"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="My Study Notes"
              className="w-full bg-white border-2 border-black rounded-md p-3 focus:ring-0 focus:outline-none focus:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-shadow font-medium"
            />
          </div>

          <div>
            <label className="block text-xs uppercase tracking-[0.2em] font-bold mb-4">
              Select Files to Combine
            </label>
            <div className="space-y-3">
              {files.map((file) => (
                <div
                  key={file.id}
                  data-testid={`file-checkbox-${file.id}`}
                  onClick={() => toggleFile(file.id)}
                  className={`flex items-center gap-4 p-4 border-2 border-black rounded-lg cursor-pointer transition-all duration-200 ${
                    selectedFiles.includes(file.id)
                      ? "bg-[#FFD873] shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]"
                      : "bg-white hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]"
                  }`}
                >
                  <div className="flex items-center gap-3 flex-1">
                    <FileText className="w-5 h-5" strokeWidth={3} />
                    <span className="font-bold text-sm">{file.filename}</span>
                  </div>
                  <div
                    className={`w-6 h-6 border-2 border-black rounded ${
                      selectedFiles.includes(file.id) ? "bg-black" : "bg-white"
                    }`}
                  >
                    {selectedFiles.includes(file.id) && (
                      <svg
                        className="w-full h-full text-white"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={3}
                          d="M5 13l4 4L19 7"
                        />
                      </svg>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="border-t-2 border-black p-6 bg-[#F4F4F0]">
          <button
            data-testid="submit-process-notes"
            onClick={handleSubmit}
            disabled={loading}
            className="w-full px-6 py-3 bg-[#FFD873] text-black border-2 border-black rounded-md shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:translate-y-[2px] hover:translate-x-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all font-bold disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <Loader2 className="inline-block mr-2 w-5 h-5 animate-spin" />
                Processing...
              </>
            ) : (
              "Create Combined Notes"
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProcessNotesDialog;