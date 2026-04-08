import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import { Upload, FileText, Brain, Trash2, Plus, Loader2 } from "lucide-react";
import { toast } from "sonner";
import FileUploadZone from "../components/FileUploadZone";
import FileList from "../components/FileList";
import CombinedNotesList from "../components/CombinedNotesList";
import MindMapsList from "../components/MindMapsList";
import ProcessNotesDialog from "../components/ProcessNotesDialog";
import GenerateMindMapDialog from "../components/GenerateMindMapDialog";
import ViewNoteDialog from "../components/ViewNoteDialog";
import ViewMindMapDialog from "../components/ViewMindMapDialog";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || "http://127.0.0.1:8000";
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const [files, setFiles] = useState([]);
  const [combinedNotes, setCombinedNotes] = useState([]);
  const [mindMaps, setMindMaps] = useState([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("upload");
  const [showProcessDialog, setShowProcessDialog] = useState(false);
  const [showMindMapDialog, setShowMindMapDialog] = useState(false);
  const [selectedNote, setSelectedNote] = useState(null);
  const [selectedMindMap, setSelectedMindMap] = useState(null);

  const fetchFiles = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/files`);
      setFiles(response.data);
    } catch (e) {
      console.error("Error fetching files:", e);
    }
  }, []);

  const fetchCombinedNotes = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/combined-notes`);
      setCombinedNotes(response.data);
    } catch (e) {
      console.error("Error fetching combined notes:", e);
    }
  }, []);

  const fetchMindMaps = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/mindmaps`);
      setMindMaps(response.data);
    } catch (e) {
      console.error("Error fetching mind maps:", e);
    }
  }, []);

  useEffect(() => {
    fetchFiles();
    fetchCombinedNotes();
    fetchMindMaps();
  }, [fetchFiles, fetchCombinedNotes, fetchMindMaps]);

  const handleFileUpload = async (file) => {
    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      await axios.post(`${API}/upload`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      toast.success(`${file.name} uploaded successfully!`);
      fetchFiles();
    } catch (e) {
      console.error("Error uploading file:", e);
      toast.error("Failed to upload file");
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteFile = async (fileId) => {
    try {
      await axios.delete(`${API}/files/${fileId}`);
      toast.success("File deleted successfully!");
      fetchFiles();
    } catch (e) {
      console.error("Error deleting file:", e);
      toast.error("Failed to delete file");
    }
  };

  const handleDeleteNote = async (noteId) => {
    try {
      await axios.delete(`${API}/combined-notes/${noteId}`);
      toast.success("Note deleted successfully!");
      fetchCombinedNotes();
    } catch (e) {
      console.error("Error deleting note:", e);
      toast.error("Failed to delete note");
    }
  };

  const handleDeleteMindMap = async (mindMapId) => {
    try {
      await axios.delete(`${API}/mindmaps/${mindMapId}`);
      toast.success("Mind map deleted successfully!");
      fetchMindMaps();
    } catch (e) {
      console.error("Error deleting mind map:", e);
      toast.error("Failed to delete mind map");
    }
  };

  return (
    <div data-testid="dashboard" className="min-h-screen bg-[#F4F4F0] p-6 md:p-12">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-12">
        <h1 className="text-4xl sm:text-5xl lg:text-6xl tracking-tighter font-black mb-4" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
          AI Study Notes
        </h1>
        <p className="text-base leading-relaxed font-medium text-[#4A4A4A]">
          Upload your study materials, create combined notes, and generate mind maps with AI
        </p>
      </div>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex gap-4 flex-wrap">
          <button
            data-testid="upload-tab"
            onClick={() => setActiveTab("upload")}
            className={`px-6 py-3 border-2 border-black rounded-md font-bold transition-all duration-200 ${
              activeTab === "upload"
                ? "bg-[#FFD873] text-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]"
                : "bg-white text-black hover:translate-y-[2px] hover:translate-x-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]"
            }`}
          >
            <Upload className="inline-block mr-2 w-5 h-5" strokeWidth={3} />
            Upload Files
          </button>
          <button
            data-testid="notes-tab"
            onClick={() => setActiveTab("notes")}
            className={`px-6 py-3 border-2 border-black rounded-md font-bold transition-all duration-200 ${
              activeTab === "notes"
                ? "bg-[#FFD873] text-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]"
                : "bg-white text-black hover:translate-y-[2px] hover:translate-x-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]"
            }`}
          >
            <FileText className="inline-block mr-2 w-5 h-5" strokeWidth={3} />
            Combined Notes
          </button>
          <button
            data-testid="mindmaps-tab"
            onClick={() => setActiveTab("mindmaps")}
            className={`px-6 py-3 border-2 border-black rounded-md font-bold transition-all duration-200 ${
              activeTab === "mindmaps"
                ? "bg-[#FFD873] text-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]"
                : "bg-white text-black hover:translate-y-[2px] hover:translate-x-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]"
            }`}
          >
            <Brain className="inline-block mr-2 w-5 h-5" strokeWidth={3} />
            Mind Maps
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto">
        {activeTab === "upload" && (
          <div className="space-y-8">
            <FileUploadZone onUpload={handleFileUpload} loading={loading} />
            <FileList files={files} onDelete={handleDeleteFile} />
            {files.length > 0 && (
              <div className="flex gap-4 flex-wrap">
                <button
                  data-testid="create-notes-button"
                  onClick={() => setShowProcessDialog(true)}
                  className="px-6 py-3 bg-[#A3E6D0] text-black border-2 border-black rounded-md shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:translate-y-[2px] hover:translate-x-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all font-bold"
                >
                  <Plus className="inline-block mr-2 w-5 h-5" strokeWidth={3} />
                  Create Combined Notes
                </button>
                <button
                  data-testid="generate-mindmap-button"
                  onClick={() => setShowMindMapDialog(true)}
                  className="px-6 py-3 bg-[#D8B4E2] text-black border-2 border-black rounded-md shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:translate-y-[2px] hover:translate-x-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all font-bold"
                >
                  <Brain className="inline-block mr-2 w-5 h-5" strokeWidth={3} />
                  Generate Mind Map
                </button>
              </div>
            )}
          </div>
        )}

        {activeTab === "notes" && (
          <CombinedNotesList 
            notes={combinedNotes} 
            onDelete={handleDeleteNote}
            onView={(note) => setSelectedNote(note)}
          />
        )}

        {activeTab === "mindmaps" && (
          <MindMapsList 
            mindMaps={mindMaps} 
            onDelete={handleDeleteMindMap}
            onView={(mindMap) => setSelectedMindMap(mindMap)}
          />
        )}
      </div>

      {/* Dialogs */}
      {showProcessDialog && (
        <ProcessNotesDialog
          files={files}
          onClose={() => setShowProcessDialog(false)}
          onSuccess={() => {
            setShowProcessDialog(false);
            fetchCombinedNotes();
            setActiveTab("notes");
          }}
        />
      )}

      {showMindMapDialog && (
        <GenerateMindMapDialog
          files={files}
          onClose={() => setShowMindMapDialog(false)}
          onSuccess={() => {
            setShowMindMapDialog(false);
            fetchMindMaps();
            setActiveTab("mindmaps");
          }}
        />
      )}

      {selectedNote && (
        <ViewNoteDialog
          note={selectedNote}
          onClose={() => setSelectedNote(null)}
        />
      )}

      {selectedMindMap && (
        <ViewMindMapDialog
          mindMap={selectedMindMap}
          onClose={() => setSelectedMindMap(null)}
        />
      )}
    </div>
  );
};

export default Dashboard;