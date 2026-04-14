import React from "react";

interface Props {
  disabled: boolean;
  loading: boolean;
  onClick: () => void;
}

export function OptimizeButton({ disabled, loading, onClick }: Props) {
  return (
    <button
      className="w-full py-2.5 bg-zinc-900 text-white rounded-lg text-sm font-medium disabled:opacity-50 flex items-center justify-center gap-2"
      disabled={disabled || loading}
      aria-busy={loading}
      onClick={onClick}
    >
      {loading && (
        <span
          className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full"
          aria-hidden="true"
        />
      )}
      {loading ? "Optimizing..." : "Optimize Resume"}
    </button>
  );
}
