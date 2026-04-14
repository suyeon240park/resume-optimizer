"use client";

import { useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import type { TrackedMutation, ChangeStatus } from "@/hooks/use-optimize";

const TYPE_STYLES: Record<
  string,
  { bg: string; border: string; label: string }
> = {
  add: {
    bg: "bg-blue-50 dark:bg-blue-950/30",
    border: "border-l-blue-500",
    label: "Keyword Addition",
  },
  edit: {
    bg: "bg-yellow-50 dark:bg-yellow-950/30",
    border: "border-l-yellow-500",
    label: "Edit",
  },
  reorder: {
    bg: "bg-orange-50 dark:bg-orange-950/30",
    border: "border-l-orange-500",
    label: "Reorder",
  },
  remove: {
    bg: "bg-red-50 dark:bg-red-950/30",
    border: "border-l-red-500",
    label: "Remove",
  },
};

interface DiffCardProps {
  change: TrackedMutation;
  onApprove: () => void;
  onReject: () => void;
  onEdit: (text: string) => void;
}

export function DiffCard({
  change,
  onApprove,
  onReject,
  onEdit,
}: DiffCardProps) {
  const [editing, setEditing] = useState(false);
  const [editText, setEditText] = useState(change.proposed ?? "");
  const styles = TYPE_STYLES[change.type] ?? TYPE_STYLES.edit;

  const handleSave = () => {
    onEdit(editText);
    setEditing(false);
  };

  return (
    <div
      className={cn(
        "rounded-md border-l-4 p-4 transition-opacity",
        styles.bg,
        styles.border,
        change.status === "rejected" && "opacity-50"
      )}
    >
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <Badge
            variant="outline"
            className="text-xs"
          >
            {styles.label}
          </Badge>
          {change.status !== "pending" && (
            <Badge
              variant={change.status === "approved" || change.status === "edited" ? "default" : "destructive"}
              className="text-xs"
            >
              {change.status}
            </Badge>
          )}
        </div>
        <div className="flex gap-1 flex-wrap">
          {change.keywords_addressed.map((k) => (
            <code
              key={k}
              className="text-xs bg-muted px-1.5 py-0.5 rounded"
            >
              {k}
            </code>
          ))}
        </div>
      </div>

      {change.target && (
        <div className="mb-2">
          <span className="text-xs font-medium text-muted-foreground">
            Before:
          </span>
          <p
            className={cn(
              "text-sm mt-0.5",
              change.type === "remove" && "line-through text-muted-foreground"
            )}
          >
            {change.target}
          </p>
        </div>
      )}

      {change.proposed && (
        <div className="mb-2">
          <span className="text-xs font-medium text-muted-foreground">
            After:
          </span>
          {editing ? (
            <div className="mt-1 space-y-2">
              <Textarea
                value={editText}
                onChange={(e) => setEditText(e.target.value)}
                rows={3}
                className="text-sm"
              />
              <div className="flex gap-2">
                <Button size="sm" onClick={handleSave}>
                  Save
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setEditing(false)}
                >
                  Cancel
                </Button>
              </div>
            </div>
          ) : (
            <p
              className="text-sm mt-0.5 cursor-pointer hover:bg-muted/50 rounded px-1 -mx-1"
              onClick={() => setEditing(true)}
            >
              {change.proposed}
            </p>
          )}
        </div>
      )}

      <Tooltip>
        <TooltipTrigger className="text-xs text-muted-foreground italic cursor-help truncate text-left w-full">
          {change.rationale}
        </TooltipTrigger>
        <TooltipContent side="bottom" className="max-w-sm">
          <p className="text-sm">{change.rationale}</p>
        </TooltipContent>
      </Tooltip>

      <div className="flex gap-2 mt-3">
        <Button
          size="sm"
          variant={change.status === "approved" ? "default" : "outline"}
          onClick={onApprove}
          disabled={change.status === "approved"}
        >
          Approve
        </Button>
        <Button
          size="sm"
          variant="outline"
          onClick={() => setEditing(true)}
          disabled={editing}
        >
          Edit
        </Button>
        <Button
          size="sm"
          variant={change.status === "rejected" ? "destructive" : "outline"}
          onClick={onReject}
          disabled={change.status === "rejected"}
        >
          Reject
        </Button>
      </div>
    </div>
  );
}
