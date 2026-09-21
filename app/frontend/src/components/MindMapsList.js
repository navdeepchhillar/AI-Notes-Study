import { Brain, Trash2, Eye } from "lucide-react";

const MindMapsList = ({ mindMaps, onDelete, onView }) => {
  if (mindMaps.length === 0) {
    return (
      <div className="bg-white border-2 border-black rounded-xl shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] p-12 text-center">
        <Brain className="w-16 h-16 mx-auto mb-4" strokeWidth={3} />
        <h3 className="text-2xl sm:text-3xl lg:text-4xl tracking-tight font-bold mb-4" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
          No Mind Maps Yet
        </h3>
        <p className="text-base leading-relaxed font-medium text-[#4A4A4A]">
          Upload some files and generate your first mind map!
        </p>
      </div>
    );
  }

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {mindMaps.map((mindMap) => (
        <div
          key={mindMap.id}
          data-testid={`mindmap-item-${mindMap.id}`}
          className="bg-white border-2 border-black rounded-xl shadow-[6px_6px_0px_0px_rgba(0,0,0,1)] hover:shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] transition-all duration-200 overflow-hidden"
        >
          <div className="border-b-2 border-black bg-[#D8B4E2] p-4">
            <h3 className="font-bold text-xl" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
              {mindMap.title}
            </h3>
          </div>
          <div className="p-6 space-y-4">
            <p className="text-sm font-medium text-[#4A4A4A]">
              Created: {formatDate(mindMap.created_at)}
            </p>
            <p className="text-sm font-medium text-[#4A4A4A]">
              {mindMap.nodes.length} node{mindMap.nodes.length !== 1 ? 's' : ''} • {mindMap.file_ids.length} file{mindMap.file_ids.length !== 1 ? 's' : ''}
            </p>
            <div className="flex gap-2">
              <button
                data-testid={`view-mindmap-${mindMap.id}`}
                onClick={() => onView(mindMap)}
                className="flex-1 px-4 py-2 bg-[#FFD873] text-black border-2 border-black rounded-md shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:translate-y-[2px] hover:translate-x-[2px] hover:shadow-[2px_2px_0px_0px_rgba(0,0,0,1)] transition-all font-bold text-sm"
              >
                <Eye className="inline-block mr-2 w-4 h-4" strokeWidth={3} />
                View
              </button>
              <button
                data-testid={`delete-mindmap-${mindMap.id}`}
                onClick={() => onDelete(mindMap.id)}
                className="px-4 py-2 bg-[#FF6B6B] text-white border-2 border-black rounded-md hover:translate-y-[2px] hover:translate-x-[2px] transition-all"
              >
                <Trash2 className="w-4 h-4" strokeWidth={3} />
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default MindMapsList;