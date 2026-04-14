"use client";

import { Button } from "@/components/ui/button";
import { DiffCard } from "@/components/diff-card";
import type { TrackedMutation } from "@/hooks/use-optimize";

function groupBy<T>(items: T[], key: (item: T) => string) {
  const groups: Record<string, T[]> = {};
  for (const item of items) {
    const k = key(item);
    (groups[k] ??= []).push(item);
  }
  return groups;
}

interface DiffViewerProps {
  changes: TrackedMutation[];
  onUpdate: (id: string, update: Partial<TrackedMutation>) => void;
  onApproveAll: () => void;
}

export function DiffViewer({
  changes,
  onUpdate,
  onApproveAll,
}: DiffViewerProps) {
  const pending = changes.filter((c) => c.status === "pending").length;
  const approved = changes.filter(
    (c) => c.status === "approved" || c.status === "edited"
  ).length;
  const rejected = changes.filter((c) => c.status === "rejected").length;

  const grouped = groupBy(changes, (c) => c.section);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between bg-muted/50 rounded-lg p-3">
        <div className="flex gap-4 text-sm">
          <span>
            Pending: <strong>{pending}</strong>
          </span>
          <span>
            Approved: <strong>{approved}</strong>
          </span>
          <span>
            Rejected: <strong>{rejected}</strong>
          </span>
        </div>
        <Button size="sm" onClick={onApproveAll} disabled={pending === 0}>
          Approve All
        </Button>
      </div>

      {Object.entries(grouped).map(([section, sectionChanges]) => (
        <div key={section}>
          <h3 className="text-sm font-semibold text-muted-foreground mb-2">
            {section}
          </h3>
          <div className="space-y-3">
            {sectionChanges.map((change) => (
              <DiffCard
                key={change.id}
                change={change}
                onApprove={() => onUpdate(change.id, { status: "approved" })}
                onReject={() => onUpdate(change.id, { status: "rejected" })}
                onEdit={(text) =>
                  onUpdate(change.id, { proposed: text, status: "edited" })
                }
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
