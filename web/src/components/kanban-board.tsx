"use client";

import { useCallback } from "react";
import {
  DndContext,
  DragEndEvent,
  DragOverlay,
  closestCenter,
} from "@dnd-kit/core";
import {
  SortableContext,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import Link from "next/link";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ATSScoreBadge } from "@/components/ats-score-badge";
import { useUpdateApplication } from "@/hooks/use-applications";
import type { ApplicationOut, ApplicationStatus } from "@/lib/types";
import { STATUS_COLUMNS } from "@/lib/types";

const COLUMN_LABELS: Record<ApplicationStatus, string> = {
  draft: "Draft",
  optimized: "Optimized",
  applied: "Applied",
  interview: "Interview",
  offer: "Offer",
  rejected: "Rejected",
};

function ApplicationCard({ app }: { app: ApplicationOut }) {
  const { attributes, listeners, setNodeRef, transform, transition } =
    useSortable({ id: app.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      <Link href={`/dashboard/${app.id}`}>
        <Card className="cursor-pointer hover:shadow-md transition-shadow">
          <CardContent className="p-3">
            <p className="font-medium text-sm">{app.company}</p>
            <p className="text-xs text-muted-foreground truncate">
              {app.role_title}
            </p>
            <div className="flex items-center justify-between mt-2">
              <span className="text-xs text-muted-foreground">
                {new Date(app.created_at).toLocaleDateString()}
              </span>
            </div>
          </CardContent>
        </Card>
      </Link>
    </div>
  );
}

export function KanbanBoard({
  applications,
}: {
  applications: ApplicationOut[];
}) {
  const updateApp = useUpdateApplication();

  const grouped = STATUS_COLUMNS.reduce(
    (acc, status) => {
      acc[status] = applications.filter((a) => a.status === status);
      return acc;
    },
    {} as Record<ApplicationStatus, ApplicationOut[]>
  );

  const handleDragEnd = useCallback(
    (event: DragEndEvent) => {
      const { active, over } = event;
      if (!over) return;

      const overId = over.id as string;
      const newStatus = STATUS_COLUMNS.find((s) => s === overId);
      if (newStatus) {
        updateApp.mutate({ id: active.id as string, status: newStatus });
      }
    },
    [updateApp]
  );

  return (
    <DndContext collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
      <div className="flex gap-4 overflow-x-auto p-6 h-full">
        {STATUS_COLUMNS.map((status) => (
          <div
            key={status}
            className="flex-shrink-0 w-64 bg-muted/40 rounded-lg p-3"
          >
            <h3 className="text-sm font-semibold mb-3 text-muted-foreground uppercase tracking-wider">
              {COLUMN_LABELS[status]}{" "}
              <span className="text-xs">({grouped[status].length})</span>
            </h3>
            <SortableContext
              items={grouped[status].map((a) => a.id)}
              strategy={verticalListSortingStrategy}
            >
              <div className="space-y-2">
                {grouped[status].map((app) => (
                  <ApplicationCard key={app.id} app={app} />
                ))}
              </div>
            </SortableContext>
          </div>
        ))}
      </div>
    </DndContext>
  );
}
