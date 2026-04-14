"use client";

import Link from "next/link";
import { useResumes, useDeleteResume } from "@/hooks/use-resumes";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { ResumeUpload } from "@/components/resume-upload";

export default function ResumesPage() {
  const { data: resumes, isLoading } = useResumes();
  const deleteResume = useDeleteResume();

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold">Resumes</h1>
        <ResumeUpload />
      </div>

      {isLoading ? (
        <div className="animate-pulse text-muted-foreground">Loading...</div>
      ) : !resumes || resumes.length === 0 ? (
        <Card>
          <CardContent className="p-8 text-center text-muted-foreground">
            No resumes uploaded yet. Click &quot;Upload Resume&quot; to add your
            LaTeX resume.
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {resumes.map((r) => (
            <Card key={r.id}>
              <CardContent className="p-4 flex items-center justify-between">
                <Link
                  href={`/resumes/${r.id}`}
                  className="flex-1 hover:underline"
                >
                  <p className="font-medium">{r.name}</p>
                  <p className="text-xs text-muted-foreground">
                    Updated {new Date(r.updated_at).toLocaleDateString()}
                  </p>
                </Link>
                <div className="flex items-center gap-2">
                  {r.preset_type && (
                    <Badge variant="secondary">{r.preset_type}</Badge>
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-destructive"
                    onClick={() => deleteResume.mutate(r.id)}
                  >
                    Delete
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
