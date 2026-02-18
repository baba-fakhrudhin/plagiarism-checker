import React from "react";

export default function HighlightedText({ text, highlights = [] }) {
  if (!text) return null;

  let highlightedText = text;

  // Sort by longest matched_text first (prevents nested overwrite issues)
  const sortedHighlights = [...highlights].sort(
    (a, b) => b.matched_text.length - a.matched_text.length
  );

  sortedHighlights.forEach((match) => {
    if (!match.matched_text) return;

    const similarity = match.similarity_score || 0;

    const getColor = () => {
      if (similarity >= 0.85) return "bg-red-300";
      if (similarity >= 0.75) return "bg-orange-300";
      return "bg-yellow-300";
    };

    const escaped = match.matched_text.replace(
      /[.*+?^${}()|[\]\\]/g,
      "\\$&"
    );

    const regex = new RegExp(escaped, "gi");

    highlightedText = highlightedText.replace(
      regex,
      (found) =>
        `<span class="${getColor()} cursor-pointer hover:opacity-80 transition"
          title="Similarity: ${(similarity * 100).toFixed(
            1
          )}%\nSource: ${match.source_url}">
          ${found}
        </span>`
    );
  });

  return (
    <div
      className="bg-gray-50 p-6 rounded-lg border border-gray-200 leading-relaxed text-gray-800 whitespace-pre-wrap"
      dangerouslySetInnerHTML={{ __html: highlightedText }}
    />
  );
}
