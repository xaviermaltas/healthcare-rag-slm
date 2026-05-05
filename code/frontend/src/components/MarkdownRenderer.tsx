import React from 'react';

interface MarkdownRendererProps {
  content: string;
}

export function MarkdownRenderer({ content }: MarkdownRendererProps) {
  // Parse markdown and render as HTML
  const renderMarkdown = (text: string) => {
    // Split by lines and process
    const lines = text.split('\n');
    const elements: React.ReactNode[] = [];
    let currentList: React.ReactNode[] = [];
    let inCodeBlock = false;
    let codeBlockContent = '';

    const processInlineMarkdown = (line: string): React.ReactNode[] => {
      // Parse markdown and return React elements
      const parts: React.ReactNode[] = [];
      let lastIndex = 0;
      
      // Combined regex for all markdown patterns
      const regex = /\*\*(.*?)\*\*|__(.*?)__|`(.*?)`|\*(.*?)\*|_(.*?)_/g;
      let match;
      let matchCount = 0;
      
      while ((match = regex.exec(line)) !== null) {
        // Add text before match
        if (match.index > lastIndex) {
          parts.push(line.substring(lastIndex, match.index));
        }
        
        // Add matched element
        if (match[1] !== undefined) {
          // **bold**
          parts.push(
            <strong key={`strong-${matchCount}`} className="font-bold text-gray-900">
              {match[1]}
            </strong>
          );
        } else if (match[2] !== undefined) {
          // __bold__
          parts.push(
            <strong key={`strong-${matchCount}`} className="font-bold text-gray-900">
              {match[2]}
            </strong>
          );
        } else if (match[3] !== undefined) {
          // `code`
          parts.push(
            <code key={`code-${matchCount}`} className="bg-gray-100 text-red-600 px-1 py-0.5 rounded text-sm font-mono">
              {match[3]}
            </code>
          );
        } else if (match[4] !== undefined) {
          // *italic*
          parts.push(
            <em key={`em-${matchCount}`} className="italic text-gray-700">
              {match[4]}
            </em>
          );
        } else if (match[5] !== undefined) {
          // _italic_
          parts.push(
            <em key={`em-${matchCount}`} className="italic text-gray-700">
              {match[5]}
            </em>
          );
        }
        
        matchCount++;
        lastIndex = regex.lastIndex;
      }
      
      // Add remaining text
      if (lastIndex < line.length) {
        parts.push(line.substring(lastIndex));
      }
      
      return parts.length > 0 ? parts : [line];
    };

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];

      // Code blocks
      if (line.startsWith('```')) {
        if (inCodeBlock) {
          elements.push(
            <pre key={`code-${i}`} className="bg-gray-900 text-green-400 p-4 rounded-lg overflow-x-auto text-sm font-mono my-4">
              {codeBlockContent}
            </pre>
          );
          codeBlockContent = '';
          inCodeBlock = false;
        } else {
          inCodeBlock = true;
        }
        continue;
      }

      if (inCodeBlock) {
        codeBlockContent += line + '\n';
        continue;
      }

      // Empty lines
      if (line.trim() === '') {
        // Flush list if we have one
        if (currentList.length > 0) {
          elements.push(
            <ul key={`list-${i}`} className="list-disc list-inside space-y-2 my-4 ml-4">
              {currentList.map((item, idx) => (
                <li key={idx} className="text-gray-700">
                  {item}
                </li>
              ))}
            </ul>
          );
          currentList = [];
        }
        elements.push(<div key={`empty-${i}`} className="h-2" />);
        continue;
      }

      // Headings with # syntax
      if (line.startsWith('# ')) {
        if (currentList.length > 0) {
          elements.push(
            <ul key={`list-${i}`} className="list-disc space-y-2 my-4 ml-6">
              {currentList.map((item, idx) => (
                <li key={idx} className="text-gray-700">
                  {item}
                </li>
              ))}
            </ul>
          );
          currentList = [];
        }
        elements.push(
          <h1 key={`h1-${i}`} className="text-3xl font-bold text-gray-900 mt-8 mb-4 pb-2 border-b-2 border-gray-300">
            {processInlineMarkdown(line.replace(/^# /, ''))}
          </h1>
        );
        continue;
      }

      if (line.startsWith('## ')) {
        if (currentList.length > 0) {
          elements.push(
            <ul key={`list-${i}`} className="list-disc space-y-2 my-4 ml-6">
              {currentList.map((item, idx) => (
                <li key={idx} className="text-gray-700">
                  {item}
                </li>
              ))}
            </ul>
          );
          currentList = [];
        }
        elements.push(
          <h2 key={`h2-${i}`} className="text-2xl font-bold text-gray-900 mt-6 mb-3 pb-1 border-b border-gray-300">
            {processInlineMarkdown(line.replace(/^## /, ''))}
          </h2>
        );
        continue;
      }

      if (line.startsWith('### ')) {
        if (currentList.length > 0) {
          elements.push(
            <ul key={`list-${i}`} className="list-disc space-y-2 my-4 ml-6">
              {currentList.map((item, idx) => (
                <li key={idx} className="text-gray-700">
                  {item}
                </li>
              ))}
            </ul>
          );
          currentList = [];
        }
        elements.push(
          <h3 key={`h3-${i}`} className="text-xl font-bold text-gray-900 mt-4 mb-2">
            {processInlineMarkdown(line.replace(/^### /, ''))}
          </h3>
        );
        continue;
      }

      // Detect **text:** pattern as heading (common in medical documents)
      if (line.match(/^\*\*[^*]+:\*\*$/) || line.match(/^\*\*[^*]+\*\*$/)) {
        if (currentList.length > 0) {
          elements.push(
            <ul key={`list-${i}`} className="list-disc space-y-2 my-4 ml-6">
              {currentList.map((item, idx) => (
                <li key={idx} className="text-gray-700">
                  {item}
                </li>
              ))}
            </ul>
          );
          currentList = [];
        }
        const headingText = line.replace(/\*\*/g, '');
        elements.push(
          <h3 key={`h3-bold-${i}`} className="text-lg font-bold text-gray-900 mt-4 mb-2">
            {headingText}
          </h3>
        );
        continue;
      }

      // List items
      if (line.startsWith('-') || line.startsWith('*')) {
        const itemText = line.replace(/^[-*]\s+/, '');
        currentList.push(
          <>{processInlineMarkdown(itemText)}</>
        );
        continue;
      }

      // Regular paragraphs
      if (currentList.length > 0) {
        elements.push(
          <ul key={`list-${i}`} className="list-disc list-inside space-y-2 my-4 ml-4">
            {currentList.map((item, idx) => (
              <li key={idx} className="text-gray-700">
                {item}
              </li>
            ))}
          </ul>
        );
        currentList = [];
      }

      elements.push(
        <p
          key={`p-${i}`}
          className="text-gray-700 leading-relaxed mb-3"
        >
          {processInlineMarkdown(line)}
        </p>
      );
    }

    // Flush remaining list
    if (currentList.length > 0) {
      elements.push(
        <ul key="final-list" className="list-disc list-inside space-y-2 my-4 ml-4">
          {currentList.map((item, idx) => (
            <li key={idx} className="text-gray-700">
              {item}
            </li>
          ))}
        </ul>
      );
    }

    return elements;
  };

  return (
    <div className="prose prose-sm max-w-none">
      {renderMarkdown(content)}
    </div>
  );
}
