import React, { useState } from "react";
import type { MutationItem } from "../lib/api";

type TrackedMutation = MutationItem & { status: string };

const TYPE_COLORS: Record<string, string> = {
  add: "border-l-blue-500 bg-blue-50",
  edit: "border-l-yellow-500 bg-yellow-50",
  reorder: "border-l-orange-500 bg-orange-50",
  remove: "border-l-red-500 bg-red-50",
};

interface Props {
  mutations: TrackedMutation[];
  onUpdate: (index: number, update: Partial<TrackedMutation>) => void;
  onApproveAll: () => void;
}

export function MiniDiffViewer({ mutations, onUpdate, onApproveAll }: Props) {
  const pending = mutations.filter((m) => m.status === "pending").length;
  const approved = mutations.filter(
    (m) => m.status === "approved" || m.status === "edited"
  ).length;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between text-xs">
        <span className="text-zinc-500">
          {pending} pending / {approved} approved
        </span>
        <button
          className="text-zinc-900 underline font-medium"
          onClick={onApproveAll}
        >
          Approve All
        </button>
      </div>

      {mutations.map((m, i) => (
        <MiniDiffCard
          key={i}
          mutation={m}
          onApprove={() => onUpdate(i, { status: "approved" })}
          onReject={() => onUpdate(i, { status: "rejected" })}
          onEdit={(text) => onUpdate(i, { proposed: text, status: "edited" })}
        />
      ))}
    </div>
  );
}

function MiniDiffCard({
  mutation,
  onApprove,
  onReject,
  onEdit,
}: {
  mutation: TrackedMutation;
  onApprove: () => void;
  onReject: () => void;
  onEdit: (text: string) => void;
}) {
  const [editing, setEditing] = useState(false);
  const [editText, setEditText] = useState(mutation.proposed ?? "");
  const colorClass = TYPE_COLORS[mutation.type] ?? TYPE_COLORS.edit;

  return (
    <div
      className={`border-l-4 rounded p-3 text-xs ${colorClass} ${
        mutation.status === "rejected" ? "opacity-40" : ""
      }`}
    >
      <div className="flex items-center justify-between mb-1">
        <span className="font-medium text-zinc-600">{mutation.section}</span>
        <div className="flex gap-1">
          {mutation.keywords_addressed.slice(0, 2).map((k) => (
            <span
              key={k}
              className="bg-white/60 px-1 rounded text-zinc-500"
            >
              {k}
            </span>
          ))}
        </div>
      </div>

      {mutation.target && (
        <p
          className={`text-zinc-500 mb-1 ${
            mutation.type === "remove" ? "line-through" : ""
          }`}
        >
          {mutation.target}
        </p>
      )}

      {mutation.proposed && !editing && (
        <button
          type="button"
          className="text-left w-full text-zinc-800 cursor-pointer hover:bg-white/50 rounded px-1 -mx-1"
          onClick={() => setEditing(true)}
          aria-label={`Edit proposed change: ${mutation.proposed}`}
        >
          {mutation.proposed}
        </button>
      )}

      {editing && (
        <div className="space-y-1">
          <textarea
            className="w-full border rounded p-1.5 text-xs resize-none"
            rows={2}
            value={editText}
            onChange={(e) => setEditText(e.target.value)}
          />
          <button
            className="text-zinc-900 underline text-xs"
            onClick={() => {
              onEdit(editText);
              setEditing(false);
            }}
          >
            Save
          </button>
        </div>
      )}

      <p className="text-zinc-400 italic mt-1 truncate" title={mutation.rationale}>
        {mutation.rationale}
      </p>

      <div className="flex gap-2 mt-2">
        <button
          className="px-2 py-1 bg-zinc-900 text-white rounded text-xs disabled:opacity-50"
          disabled={mutation.status === "approved"}
          onClick={onApprove}
        >
          Approve
        </button>
        <button
          className="px-2 py-1 border rounded text-xs"
          onClick={() => setEditing(true)}
        >
          Edit
        </button>
        <button
          className="px-2 py-1 border border-red-200 text-red-600 rounded text-xs disabled:opacity-50"
          disabled={mutation.status === "rejected"}
          onClick={onReject}
        >
          Reject
        </button>
      </div>
    </div>
  );
}
