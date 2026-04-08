import { FileText, Trash2 } from "lucide-react";

const FileList = ({ files, onDelete }) => {
  if (files.length === 0) {
    return (
      <div className="bg-white border-2 border-black rounded-xl shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] p-8 text-center">
        <p className="text-base leading-relaxed font-medium text-[#4A4A4A]">
          No files uploaded yet. Upload your first study material above!
        </p>
      </div>
    );
  }

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  return (
    <div className="bg-white border-2 border-black rounded-xl shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] overflow-hidden">
      <div className="border-b-2 border-black bg-[#FFD873] p-6">
        <h2 className="text-2xl sm:text-3xl lg:text-4xl tracking-tight font-bold" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
          Uploaded Files ({files.length})
        </h2>
      </div>
      <div className="p-6 space-y-4">
        {files.map((file) => (
          <div
            key={file.id}
            data-testid={`file-item-${file.id}`}
            className="flex items-center justify-between p-4 bg-[#F4F4F0] border-2 border-black rounded-lg transition-all duration-200 hover:shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:translate-y-[-2px] hover:translate-x-[-2px]"
          >
            <div className="flex items-center gap-4 flex-1">
              <div className="p-3 bg-white border-2 border-black rounded-md">
                <FileText className="w-6 h-6" strokeWidth={3} />
              </div>
              <div className="flex-1">
                <h3 className="font-bold text-base">{file.filename}</h3>
                <p className="text-sm font-medium text-[#4A4A4A]">
                  {formatFileSize(file.size)} • {formatDate(file.uploaded_at)}
                </p>
              </div>
            </div>
            <button
              data-testid={`delete-file-${file.id}`}
              onClick={() => onDelete(file.id)}
              className="p-3 bg-[#FF6B6B] text-white border-2 border-black rounded-md hover:translate-y-[2px] hover:translate-x-[2px] transition-all"
            >
              <Trash2 className="w-5 h-5" strokeWidth={3} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FileList;