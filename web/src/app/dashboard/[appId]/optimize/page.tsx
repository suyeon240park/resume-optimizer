"use client";

import { use, useState } from "react";
import Link from "next/link";
import { useApplication } from "@/hooks/use-applications";
import { useResumes } from "@/hooks/use-resumes";
import { useOptimize } from "@/hooks/use-optimize";
import { DiffViewer } from "@/components/diff-viewer";
import { ATSScoreBadge } from "@/components/ats-score-badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { api } from "@/lib/api";

export default function OptimizePage({
  params,
}: {
  params: Promise<{ appId: string }>;
}) {
  const { appId } = use(params);
  const { data: app } = useApplication(appId);
  const { data: resumes } = useResumes();
  const [selectedResumeId, setSelectedResumeId] = useState<string>("");
  const {
    isOptimizing,
    isApplying,
    result,
    changes,
    applyResult,
    error,
    runOptimize,
    updateChange,
    approveAll,
    applyChanges,
  } = useOptimize(appId);

  if (!app) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-pulse text-muted-foreground">Loading...</div>
      </div>
    );
  }

  if (applyResult) {
    return (
      <div className="p-6 max-w-3xl mx-auto space-y-6">
        <Card>
          <CardHeader>
            <CardTitle>Optimization Applied</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-4">
              <span className="text-sm">
                Version {applyResult.version_number} created
              </span>
              <ATSScoreBadge score={applyResult.ats_score} />
            </div>
            <div className="flex gap-3">
              <Button
                render={
                  <a
                    href={api.downloadPdf(applyResult.version_id)}
                    target="_blank"
                    rel="noopener noreferrer"
                  />
                }
              >
                Download PDF
              </Button>
              <Button variant="outline" render={<Link href={`/dashboard/${appId}`} />}>
                Back to Application
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl font-bold">
          Optimize for {app.company} &mdash; {app.role_title}
        </h1>
      </div>

      {!result ? (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Select Base Resume</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <select
              className="w-full border rounded-md p-2 text-sm bg-background"
              value={selectedResumeId}
              onChange={(e) => setSelectedResumeId(e.target.value)}
            >
              <option value="">Choose a resume...</option>
              {resumes?.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name}
                  {r.preset_type ? ` (${r.preset_type})` : ""}
                </option>
              ))}
            </select>

            <Button
              className="w-full"
              disabled={!selectedResumeId || isOptimizing}
              onClick={() => runOptimize(selectedResumeId)}
            >
              {isOptimizing ? (
                <span className="flex items-center gap-2">
                  <span className="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full" />
                  Running optimization...
                </span>
              ) : (
                "Run Optimization"
              )}
            </Button>

            {error && (
              <p className="text-sm text-destructive">{error}</p>
            )}
          </CardContent>
        </Card>
      ) : (
        <>
          <DiffViewer
            changes={changes}
            onUpdate={updateChange}
            onApproveAll={approveAll}
          />

          <div className="flex gap-3">
            <Button
              className="flex-1"
              disabled={
                isApplying ||
                changes.every((c) => c.status === "pending")
              }
              onClick={() => applyChanges(selectedResumeId)}
            >
              {isApplying ? "Applying..." : "Apply Approved Changes"}
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
