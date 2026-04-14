"use client";

import { use } from "react";
import Link from "next/link";
import { useApplication, useVersions } from "@/hooks/use-applications";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { ATSScoreBadge } from "@/components/ats-score-badge";
import { api } from "@/lib/api";

export default function ApplicationDetailPage({
  params,
}: {
  params: Promise<{ appId: string }>;
}) {
  const { appId } = use(params);
  const { data: app, isLoading } = useApplication(appId);
  const { data: versions } = useVersions(appId);

  if (isLoading || !app) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-pulse text-muted-foreground">Loading...</div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold">{app.company}</h1>
          <p className="text-muted-foreground">{app.role_title}</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline">{app.status}</Badge>
          <Link href={`/dashboard/${appId}/optimize`}>
            <Button>Optimize Resume</Button>
          </Link>
        </div>
      </div>

      <Separator />

      {app.jd_analysis && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">JD Analysis</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex gap-2 flex-wrap">
              <Badge variant="secondary">{app.jd_analysis.seniority}</Badge>
              <Badge variant="secondary">{app.jd_analysis.team_function}</Badge>
            </div>
            <div>
              <p className="text-xs font-medium text-muted-foreground mb-1">
                Required Skills
              </p>
              <div className="flex gap-1.5 flex-wrap">
                {app.jd_analysis.required_skills.map((s) => (
                  <Badge
                    key={s.skill}
                    variant={
                      s.importance === "critical" ? "default" : "outline"
                    }
                    className="text-xs"
                  >
                    {s.skill}
                  </Badge>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Job Description</CardTitle>
        </CardHeader>
        <CardContent>
          <pre className="whitespace-pre-wrap text-sm text-muted-foreground font-sans">
            {app.jd_snapshot}
          </pre>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Resume Versions</CardTitle>
        </CardHeader>
        <CardContent>
          {!versions || versions.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No versions yet.{" "}
              <Link
                href={`/dashboard/${appId}/optimize`}
                className="underline"
              >
                Run your first optimization
              </Link>
              .
            </p>
          ) : (
            <div className="space-y-2">
              {versions.map((v) => (
                <div
                  key={v.id}
                  className="flex items-center justify-between p-3 border rounded-md"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-medium">
                      v{v.version_number}
                    </span>
                    <ATSScoreBadge score={v.ats_score} />
                    <span className="text-xs text-muted-foreground">
                      {new Date(v.created_at).toLocaleString()}
                    </span>
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    render={
                      <a
                        href={api.downloadPdf(v.id)}
                        target="_blank"
                        rel="noopener noreferrer"
                      />
                    }
                  >
                    Download PDF
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
