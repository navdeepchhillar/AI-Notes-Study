import { useCallback, useMemo } from "react";
import { X } from "lucide-react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
} from "reactflow";
import "reactflow/dist/style.css";
import dagre from "dagre";

const ViewMindMapDialog = ({ mindMap, onClose }) => {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  // Layout the nodes using dagre
  const getLayoutedElements = (nodes, edges) => {
    const dagreGraph = new dagre.graphlib.Graph();
    dagreGraph.setDefaultEdgeLabel(() => ({}));
    dagreGraph.setGraph({ rankdir: 'TB', ranksep: 100, nodesep: 80 });

    nodes.forEach((node) => {
      dagreGraph.setNode(node.id, { width: 200, height: 80 });
    });

    edges.forEach((edge) => {
      dagreGraph.setEdge(edge.source, edge.target);
    });

    dagre.layout(dagreGraph);

    const layoutedNodes = nodes.map((node) => {
      const nodeWithPosition = dagreGraph.node(node.id);
      return {
        ...node,
        position: {
          x: nodeWithPosition.x - 100,
          y: nodeWithPosition.y - 40,
        },
      };
    });

    return { nodes: layoutedNodes, edges };
  };

  // Color scheme based on level
  const getNodeColor = (level) => {
    const colors = ['#FFD873', '#A3E6D0', '#D8B4E2', '#FFFFFF'];
    return colors[level % colors.length];
  };

  // Convert mind map data to React Flow format
  const initialNodes = useMemo(() => {
    return mindMap.nodes.map((node) => ({
      id: node.id,
      data: { label: node.label },
      position: { x: 0, y: 0 },
      style: {
        background: getNodeColor(node.level || 0),
        padding: '16px',
        border: '2px solid #0A0A0A',
        borderRadius: '8px',
        boxShadow: '4px 4px 0px 0px rgba(0,0,0,1)',
        fontSize: '14px',
        fontWeight: '600',
        fontFamily: 'Outfit, sans-serif',
        width: 200,
      },
    }));
  }, [mindMap.nodes]);

  const initialEdges = useMemo(() => {
    return mindMap.edges.map((edge, index) => ({
      id: `e${edge.from}-${edge.to}-${index}`,
      source: edge.from,
      target: edge.to,
      type: 'smoothstep',
      style: { stroke: '#0A0A0A', strokeWidth: 2 },
    }));
  }, [mindMap.edges]);

  const { nodes: layoutedNodes, edges: layoutedEdges } = useMemo(
    () => getLayoutedElements(initialNodes, initialEdges),
    [initialNodes, initialEdges]
  );

  const [nodes, setNodes, onNodesChange] = useNodesState(layoutedNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(layoutedEdges);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div
        data-testid="view-mindmap-dialog"
        className="bg-white border-2 border-black rounded-xl shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] max-w-6xl w-full max-h-[90vh] overflow-hidden"
      >
        <div className="border-b-2 border-black bg-[#D8B4E2] p-6 flex items-center justify-between">
          <div>
            <h2 className="text-2xl sm:text-3xl tracking-tight font-bold mb-2" style={{ fontFamily: 'Cabinet Grotesk, sans-serif' }}>
              {mindMap.title}
            </h2>
            <p className="text-sm font-medium text-[#0A0A0A]">
              Created: {formatDate(mindMap.created_at)} • {mindMap.nodes.length} nodes
            </p>
          </div>
          <button
            data-testid="close-mindmap-dialog"
            onClick={onClose}
            className="p-2 hover:bg-black hover:text-white transition-colors border-2 border-black rounded-md"
          >
            <X className="w-6 h-6" strokeWidth={3} />
          </button>
        </div>

        <div data-testid="mindmap-canvas" className="h-[600px] bg-[#F4F4F0]">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            fitView
            minZoom={0.5}
            maxZoom={1.5}
          >
            <Background color="#0A0A0A" gap={16} />
            <Controls className="border-2 border-black rounded-md" />
            <MiniMap
              className="border-2 border-black rounded-md"
              nodeColor={(node) => node.style.background}
            />
          </ReactFlow>
        </div>
      </div>
    </div>
  );
};

export default ViewMindMapDialog;