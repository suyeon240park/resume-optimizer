import React from "react";

interface Props {
  text: string;
  onChange: (text: string) => void;
}

export function JDPreview({ text, onChange }: Props) {
  return (
    <div>
      <label className="text-xs font-medium text-zinc-500 mb-1 block">
        Job Description
      </label>
      <textarea
        className="w-full border rounded-lg p-3 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-zinc-300"
        rows={8}
        value={text}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Paste or edit the job description..."
      />
      {text && (
        <p className="text-xs text-zinc-400 mt-1">
          {text.split(/\s+/).length} words
        </p>
      )}
    </div>
  );
}
