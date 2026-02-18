import React from 'react';

export default function HighlightedText({ text, highlights }) {
  const getSortedHighlights = () => {
    return highlights.sort((a, b) => a.start - b.start);
  };

  const renderHighlightedText = () => {
    let lastIndex = 0;
    const parts = [];
    const sorted = getSortedHighlights();

    sorted.forEach((highlight, idx) => {
      // Add non-highlighted text
      if (lastIndex < highlight.start) {
        parts.push(
          <span key={`text-${idx}`}>
            {text.substring(lastIndex, highlight.start)}
          </span>
        );
      }

      // Add highlighted text
      const getColor = (type) => {
        switch (type) {
          case 'exact':
            return 'bg-red-300';
          case 'semantic':
            return 'bg-yellow-300';
          case 'paraphrase':
            return 'bg-orange-300';
          default:
            return 'bg-yellow-200';
        }
      };

      parts.push(
        <span
          key={`highlight-${idx}`}
          className={`${getColor(highlight.type)} cursor-pointer hover:opacity-80 transition`}
          title={`${highlight.type} match - ${(highlight.similarity * 100).toFixed(1)}% similar\nSource: ${highlight.source_title || 'Unknown'}`}
        >
          {text.substring(highlight.start, highlight.end)}
        </span>
      );

      lastIndex = highlight.end;
    });

    // Add remaining text
    if (lastIndex < text.length) {
      parts.push(
        <span key="text-end">{text.substring(lastIndex)}</span>
      );
    }

    return parts;
  };

  return (
    <div className="bg-gray-50 p-6 rounded-lg border border-gray-200 leading-relaxed text-gray-800 whitespace-pre-wrap">
      {renderHighlightedText()}
    </div>
  );
}