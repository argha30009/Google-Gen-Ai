import { AlertCircleIcon, XCircle } from 'lucide-react';
import { useNews } from '../context/NewsContext';
export function FactCheckReport() {
  const { newsData, loading } = useNews();

  console.log('📝 FactCheckReport render - loading:', loading, 'hasData:', !!newsData);

  if (loading) {
    return <div className="bg-white rounded-lg border border-gray-200 p-5">
        <h2 className="text-base font-semibold text-gray-900 mb-3">
          Fact Check Report
        </h2>
        <div className="flex items-center gap-3">
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
          <p className="text-sm text-gray-600">Loading...</p>
        </div>
      </div>;
  }

  if (!newsData) {
    console.log('❌ FactCheckReport: No newsData');
    return <div className="bg-white rounded-lg border border-gray-200 p-5">
        <h2 className="text-base font-semibold text-gray-900 mb-3">
          Fact Check Report
        </h2>
        <p className="text-sm text-gray-600">Search for a news topic to see fact check analysis</p>
      </div>;
  }

  const isNoData = newsData.status === 'no_data';
  const factCheck = newsData.summary?.fact_check || '';
  
  console.log('📄 FactCheckReport: factCheck length:', factCheck.length);

  // Parse markdown for better rendering
  const renderFactCheck = (markdown: string) => {
    const lines = markdown.split('\n');
    const elements: JSX.Element[] = [];
    let key = 0;

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      
      // Horizontal separators
      if (line.trim() === '---') {
        elements.push(<div key={key++} className="border-t border-gray-200 my-4" />);
        continue;
      }

      // Main headers (##)
      if (line.startsWith('## ')) {
        const headerText = line.replace('## ', '').trim();
        elements.push(
          <h3 key={key++} className="text-lg font-bold text-gray-900 mb-3 mt-4">
            {headerText}
          </h3>
        );
        continue;
      }

      // Sub headers (###)
      if (line.startsWith('### ')) {
        const subHeaderText = line.replace('### ', '').trim();
        elements.push(
          <h4 key={key++} className="text-base font-semibold text-gray-800 mb-2 mt-3">
            {subHeaderText}
          </h4>
        );
        continue;
      }

      // Bold text (**text**)
      if (line.includes('**')) {
        const formatted = line.split('**').map((part, idx) => 
          idx % 2 === 1 ? <strong key={idx} className="font-semibold text-gray-900">{part}</strong> : part
        );
        elements.push(<p key={key++} className="text-sm text-gray-700 mb-2">{formatted}</p>);
        continue;
      }

      // Bullet points
      if (line.trim().startsWith('•') || line.trim().startsWith('✓')) {
        elements.push(
          <div key={key++} className="flex items-start gap-2 mb-2 ml-2">
            <span className="text-green-600 mt-0.5">{line.trim()[0]}</span>
            <p className="text-sm text-gray-700 flex-1">{line.trim().slice(1).trim()}</p>
          </div>
        );
        continue;
      }

      // Regular paragraphs
      if (line.trim()) {
        elements.push(<p key={key++} className="text-sm text-gray-700 mb-2 leading-relaxed">{line}</p>);
      }
    }

    return elements;
  };

  return <div className="bg-white rounded-lg border border-gray-200 p-5">
      <h2 className="text-base font-semibold text-gray-900 mb-3">
        Fact Check Report
      </h2>
      {isNoData ? (
        <div className="flex items-center gap-2">
          <span className="flex items-center gap-1.5 px-3 py-1.5 bg-gray-400 text-white text-sm font-medium rounded-full">
            <XCircle className="w-4 h-4" />
            No Data
          </span>
          <p className="text-sm text-gray-600">
            {factCheck || 'Could not find any data for the topic'}
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          <div className="flex items-center gap-2 mb-4">
            <span className="flex items-center gap-1.5 px-3 py-1.5 bg-orange-500 text-white text-sm font-medium rounded-full">
              <AlertCircleIcon className="w-4 h-4" />
              Analysis Complete
            </span>
            <p className="text-sm text-gray-600">
              Based on {newsData.sentiment_analysis.sentiment_summary.total_analyzed} sources
            </p>
          </div>
          <div className="prose prose-sm max-w-none">
            {renderFactCheck(factCheck)}
          </div>
        </div>
      )}
    </div>;
}