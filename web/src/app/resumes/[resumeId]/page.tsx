"use client";

import { use } from "react";
import { useResume } from "@/hooks/use-resumes";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function ResumeDetailPage({
  params,
}: {
  params: Promise<{ resumeId: string }>;
}) {
  const { resumeId } = use(params);
  const { data: resume, isLoading } = useResume(resumeId);

  if (isLoading || !resume) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-pulse text-muted-foreground">Loading...</div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold">{resume.name}</h1>
        {resume.preset_type && (
          <Badge variant="secondary" className="mt-1">
            {resume.preset_type}
          </Badge>
        )}
      </div>

      <Tabs defaultValue="sections">
        <TabsList>
          <TabsTrigger value="sections">Parsed Sections</TabsTrigger>
          <TabsTrigger value="source">LaTeX Source</TabsTrigger>
        </TabsList>

        <TabsContent value="sections" className="space-y-4 mt-4">
          {resume.sections?.map((section) => (
            <Card key={section.name}>
              <CardHeader>
                <CardTitle className="text-base">{section.name}</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {section.entries.map((entry, i) => (
                  <div key={i} className="text-sm border-l-2 pl-3 py-1">
                    <span className="text-xs font-mono text-muted-foreground">
                      \\{entry.command}
                    </span>
                    {entry.args.map((arg, j) => (
                      <p key={j} className="text-foreground">
                        {arg}
                      </p>
                    ))}
                    {entry.children?.map((child, k) => (
                      <p
                        key={k}
                        className="text-muted-foreground ml-4 text-xs"
                      >
                        {child.args[0]}
                      </p>
                    ))}
                  </div>
                ))}
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        <TabsContent value="source" className="mt-4">
          <Card>
            <CardContent className="p-4">
              <pre className="text-xs font-mono whitespace-pre-wrap overflow-x-auto max-h-[600px] overflow-y-auto">
                {resume.latex_source}
              </pre>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
