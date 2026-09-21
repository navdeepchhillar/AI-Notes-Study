import { X } from "lucide-react";

const ViewNoteDialog = ({ note, onClose }) => {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div
        data-testid="view-note-dialog"
        className="bg-white border-2 border-black rounded-xl shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] max-w-4xl w-full max-h-[90vh] overflow-hidden"
      >
        <div className="border-b-2 border-black bg-[#A3E6D0] p-6 flex items-center justify-between">
          <div>
            <h2 className="text-2xl sm:text-3xl tracking-tight font-bold mb-2" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
              {note.title}
            </h2>
            <p className="text-sm font-medium text-[#0A0A0A]">
              Created: {formatDate(note.created_at)}
            </p>
          </div>
          <button
            data-testid="close-note-dialog"
            onClick={onClose}
            className="p-2 hover:bg-black hover:text-white transition-colors border-2 border-black rounded-md"
          >
            <X className="w-6 h-6" strokeWidth={3} />
          </button>
        </div>

        <div className="p-8 overflow-y-auto max-h-[calc(90vh-150px)]">
          <div 
            data-testid="note-content"
            className="prose max-w-none"
            style={{ whiteSpace: 'pre-wrap', fontFamily: 'Outfit, sans-serif' }}
          >
            {note.content}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ViewNoteDialog;