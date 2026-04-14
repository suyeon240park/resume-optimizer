import React from "react";
import { API_URL } from "../../config";

interface Props {
  versionId: string;
  versionNumber: number;
  atsScore: number | null;
}

export function DownloadButton({ versionId, versionNumber, atsScore }: Props) {
  return (
    <div className="text-center space-y-3 py-8">
      <div className="text-3xl">&#10003;</div>
      <h2 className="font-bold">Optimization Applied</h2>
      <p className="text-sm text-zinc-500">
        Version {versionNumber} created
        {atsScore !== null && (
          <span className="ml-1 font-medium text-zinc-700">
            (ATS: {atsScore}%)
          </span>
        )}
      </p>
      <a
        href={`${API_URL}/api/versions/${versionId}/pdf`}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-block bg-zinc-900 text-white px-6 py-2.5 rounded-lg text-sm font-medium"
      >
        Download PDF
      </a>
    </div>
  );
}
