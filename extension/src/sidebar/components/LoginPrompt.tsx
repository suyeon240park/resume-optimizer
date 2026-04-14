import React from "react";
import { WEB_URL } from "../../config";

export function LoginPrompt() {
  return (
    <div className="flex flex-col items-center justify-center h-screen p-6 text-center">
      <h2 className="text-lg font-bold mb-2">Sign In Required</h2>
      <p className="text-sm text-zinc-500 mb-4">
        Please sign in on the web dashboard first, then return here.
      </p>
      <a
        href={`${WEB_URL}/login`}
        target="_blank"
        rel="noopener noreferrer"
        className="bg-zinc-900 text-white px-4 py-2 rounded-lg text-sm font-medium"
      >
        Open Dashboard
      </a>
    </div>
  );
}
