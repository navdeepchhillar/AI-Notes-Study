import { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, Loader2 } from "lucide-react";

const FileUploadZone = ({ onUpload, loading }) => {
  const onDrop = useCallback(
    (acceptedFiles) => {
      acceptedFiles.forEach((file) => {
        onUpload(file);
      });
    },
    [onUpload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
      "text/plain": [".txt"],
    },
    multiple: true,
  });

  return (
    <div
      {...getRootProps()}
      data-testid="file-upload-zone"
      className={`border-4 border-dashed border-black rounded-2xl p-12 text-center cursor-pointer transition-colors duration-200 ${
        isDragActive ? "bg-[#A3E6D0]" : "bg-[#F4F4F0] hover:bg-[#A3E6D0]"
      }`}
    >
      <input {...getInputProps()} />
      <div className="flex flex-col items-center justify-center gap-4">
        {loading ? (
          <Loader2 className="w-16 h-16 animate-spin" strokeWidth={3} />
        ) : (
          <Upload className="w-16 h-16" strokeWidth={3} />
        )}
        <h3 className="text-2xl sm:text-3xl lg:text-4xl tracking-tight font-bold" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
          {isDragActive ? "Drop files here" : "Upload Study Materials"}
        </h3>
        <p className="text-base leading-relaxed font-medium text-[#4A4A4A]">
          Drop PDF, DOCX, or TXT files here, or click to browse
        </p>
        <div className="flex gap-3 mt-4">
          <span className="px-4 py-2 bg-white border-2 border-black rounded-md text-xs uppercase tracking-[0.2em] font-bold">
            PDF
          </span>
          <span className="px-4 py-2 bg-white border-2 border-black rounded-md text-xs uppercase tracking-[0.2em] font-bold">
            DOCX
          </span>
          <span className="px-4 py-2 bg-white border-2 border-black rounded-md text-xs uppercase tracking-[0.2em] font-bold">
            TXT
          </span>
        </div>
      </div>
    </div>
  );
};

export default FileUploadZone;