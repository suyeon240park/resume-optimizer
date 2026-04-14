import React, { useEffect, useState } from "react";
import { extApi, type ResumeOut } from "../lib/api";
import { WEB_URL } from "../../config";

interface Props {
  selected: string;
  onSelect: (id: string) => void;
}

export function ResumePicker({ selected, onSelect }: Props) {
  const [resumes, setResumes] = useState<ResumeOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    extApi
      .listResumes()
      .then(setResumes)
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load resumes"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <p className="text-xs text-zinc-400" aria-busy="true">Loading resumes...</p>;
  }

  if (error) {
    return (
      <p className="text-xs text-red-500">
        {error}
      </p>
    );
  }

  if (resumes.length === 0) {
    return (
      <p className="text-xs text-zinc-500">
        No resumes uploaded.{" "}
        <a
          href={`${WEB_URL}/resumes`}
          target="_blank"
          rel="noopener noreferrer"
          className="underline"
        >
          Upload one
        </a>{" "}
        first.
      </p>
    );
  }

  return (
    <div>
      <label htmlFor="resume-picker" className="text-xs font-medium text-zinc-500 mb-1 block">
        Base Resume
      </label>
      <select
        id="resume-picker"
        className="w-full border rounded-lg p-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-zinc-300"
        value={selected}
        onChange={(e) => onSelect(e.target.value)}
      >
        <option value="">Choose a resume...</option>
        {resumes.map((r) => (
          <option key={r.id} value={r.id}>
            {r.name}
            {r.preset_type ? ` (${r.preset_type})` : ""}
          </option>
        ))}
      </select>
    </div>
  );
}
