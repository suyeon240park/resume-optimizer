"use client";

import { useCallback, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { useCreateResume } from "@/hooks/use-resumes";

export function ResumeUpload() {
  const createResume = useCreateResume();
  const fileRef = useRef<HTMLInputElement>(null);
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [source, setSource] = useState("");
  const [fileName, setFileName] = useState("");

  const handleFile = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;
      setFileName(file.name);
      if (!name) setName(file.name.replace(/\.tex$/, ""));
      const reader = new FileReader();
      reader.onload = () => setSource(reader.result as string);
      reader.readAsText(file);
    },
    [name]
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!source) return;
    await createResume.mutateAsync({ name, latex_source: source });
    setOpen(false);
    setName("");
    setSource("");
    setFileName("");
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger render={<Button />}>
        Upload Resume
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Upload LaTeX Resume</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            placeholder="Resume name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <div>
            <input
              ref={fileRef}
              type="file"
              accept=".tex"
              onChange={handleFile}
              className="hidden"
            />
            <Button
              type="button"
              variant="outline"
              onClick={() => fileRef.current?.click()}
              className="w-full"
            >
              {fileName || "Choose .tex file"}
            </Button>
          </div>
          {source && (
            <p className="text-xs text-muted-foreground">
              {source.length.toLocaleString()} characters loaded
            </p>
          )}
          <Button
            type="submit"
            className="w-full"
            disabled={!source || createResume.isPending}
          >
            {createResume.isPending ? "Uploading..." : "Upload"}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}
