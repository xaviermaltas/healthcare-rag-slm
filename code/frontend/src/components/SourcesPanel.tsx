import { FileText, TrendingUp, ExternalLink, Search } from 'lucide-react';

interface Source {
  title: string;
  specialty?: string;
  score: number;
  source?: string;
  url?: string;
}

interface SourcesPanelProps {
  sources: Source[];
}

export function SourcesPanel({ sources }: SourcesPanelProps) {
  if (!sources || sources.length === 0) {
    return null;
  }

  const getScoreColor = (score: number): string => {
    if (score >= 0.8) return 'bg-green-100 border-green-300 text-green-800';
    if (score >= 0.6) return 'bg-yellow-100 border-yellow-300 text-yellow-800';
    return 'bg-orange-100 border-orange-300 text-orange-800';
  };

  const getScoreBadgeColor = (score: number): string => {
    if (score >= 0.8) return 'bg-green-600 text-white';
    if (score >= 0.6) return 'bg-yellow-600 text-white';
    return 'bg-orange-600 text-white';
  };

  const handleSearchProtocol = (title: string) => {
    const searchQuery = encodeURIComponent(title);
    window.open(`https://www.google.com/search?q=${searchQuery}`, '_blank');
  };

  return (
    <div>
      <div className="flex items-center gap-2 mb-4">
        <FileText className="w-5 h-5 text-blue-600" />
        <h3 className="text-lg font-bold text-gray-900">📚 Fonts Consultades</h3>
        <span className="text-sm text-gray-500">({sources.length} protocols recuperats)</span>
      </div>
      
      <div className="space-y-3">
        {sources.map((source, idx) => (
          <div
            key={idx}
            className={`border-2 rounded-lg p-4 shadow-sm transition-all hover:shadow-md ${getScoreColor(source.score)}`}
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <FileText className="w-4 h-4 flex-shrink-0" />
                  <p className="font-semibold text-sm leading-tight">
                    {source.title || source.source || `Protocol ${idx + 1}`}
                  </p>
                </div>
                
                {source.specialty && (
                  <p className="text-xs opacity-75 mb-2">
                    <span className="font-medium">Especialitat:</span> {source.specialty}
                  </p>
                )}
                
                {/* Search button */}
                <button
                  onClick={() => handleSearchProtocol(source.title || source.source || '')}
                  className="mt-2 flex items-center gap-1 text-xs text-blue-600 hover:text-blue-800 hover:underline transition-colors"
                >
                  <Search className="w-3 h-3" />
                  <span>Cercar protocol</span>
                  <ExternalLink className="w-3 h-3" />
                </button>
              </div>
              
              <div className="flex flex-col items-end gap-1 flex-shrink-0">
                <div className="flex items-center gap-1">
                  <TrendingUp className="w-3 h-3" />
                  <span className={`text-xs font-bold px-2 py-1 rounded-full ${getScoreBadgeColor(source.score)}`}>
                    {(source.score * 100).toFixed(0)}%
                  </span>
                </div>
                <span className="text-xs opacity-60">Rellevància</span>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-xs text-blue-800">
          <span className="font-semibold">ℹ️ Nota:</span> Els protocols amb major puntuació de rellevància (score) 
          han tingut més pes en la generació del document. Tots els protocols superen el llindar mínim de similitud (0.5).
        </p>
      </div>
    </div>
  );
}
