"use client";

import { useState } from "react";
import { useApplications, useCreateApplication } from "@/hooks/use-applications";
import { KanbanBoard } from "@/components/kanban-board";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

export default function DashboardPage() {
  const { data: applications, isLoading } = useApplications();
  const createApp = useCreateApplication();
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({
    company: "",
    role_title: "",
    jd_snapshot: "",
    portal_url: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await createApp.mutateAsync(form);
    setOpen(false);
    setForm({ company: "", role_title: "", jd_snapshot: "", portal_url: "" });
  };

  return (
    <div className="flex flex-col h-full">
      <header className="flex items-center justify-between px-6 py-4 border-b">
        <h1 className="text-xl font-bold">Applications</h1>
        <Dialog open={open} onOpenChange={setOpen}>
          <DialogTrigger render={<Button />}>
            New Application
          </DialogTrigger>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>Add Application</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input
                placeholder="Company"
                value={form.company}
                onChange={(e) =>
                  setForm((f) => ({ ...f, company: e.target.value }))
                }
                required
              />
              <Input
                placeholder="Role Title"
                value={form.role_title}
                onChange={(e) =>
                  setForm((f) => ({ ...f, role_title: e.target.value }))
                }
                required
              />
              <Input
                placeholder="Job Posting URL (optional)"
                value={form.portal_url}
                onChange={(e) =>
                  setForm((f) => ({ ...f, portal_url: e.target.value }))
                }
              />
              <Textarea
                placeholder="Paste the job description here..."
                value={form.jd_snapshot}
                onChange={(e) =>
                  setForm((f) => ({ ...f, jd_snapshot: e.target.value }))
                }
                rows={8}
                required
              />
              <Button type="submit" className="w-full" disabled={createApp.isPending}>
                {createApp.isPending ? "Creating..." : "Create"}
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </header>

      {isLoading ? (
        <div className="flex items-center justify-center flex-1">
          <div className="animate-pulse text-muted-foreground">
            Loading applications...
          </div>
        </div>
      ) : (
        <KanbanBoard applications={applications ?? []} />
      )}
    </div>
  );
}
