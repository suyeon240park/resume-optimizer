import React, { useState, useEffect } from "react";
import { JDPreview } from "./components/JDPreview";
import { ResumePicker } from "./components/ResumePicker";
import { OptimizeButton } from "./components/OptimizeButton";
import { MiniDiffViewer } from "./components/MiniDiffViewer";
import { DownloadButton } from "./components/DownloadButton";
import { LoginPrompt } from "./components/LoginPrompt";
import { extApi } from "./lib/api";
import type { MutationItem, OptimizeResponse, ApplyResponse } from "./lib/api";

type Step = "jd" | "optimize" | "diff" | "done";

interface ScrapedJD {
  source: string;
  text: string;
}

export function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [step, setStep] = useState<Step>("jd");
  const [jdText, setJdText] = useState("");
  const [jdSource, setJdSource] = useState("");
  const [selectedResumeId, setSelectedResumeId] = useState("");
  const [appId, setAppId] = useState("");
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [optimizeResult, setOptimizeResult] =
    useState<OptimizeResponse | null>(null);
  const [mutations, setMutations] = useState<
    (MutationItem & { status: string })[]
  >([]);
  const [applyResult, setApplyResult] = useState<ApplyResponse | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    chrome.runtime.sendMessage({ type: "GET_TOKEN" }, (res) => {
      if (chrome.runtime.lastError) return;
      setIsLoggedIn(!!res?.token);
    });
  }, []);

  useEffect(() => {
    const extensionOrigin = new URL(chrome.runtime.getURL("/")).origin;
    const handler = (event: MessageEvent) => {
      if (event.origin !== extensionOrigin && event.origin !== window.location.origin) return;
      if (event.data?.type === "JD_SCRAPED" && event.data.payload) {
        const scraped = event.data.payload as ScrapedJD;
        setJdText(scraped.text);
        setJdSource(scraped.source);
      }
    };
    window.addEventListener("message", handler);
    return () => window.removeEventListener("message", handler);
  }, []);

  if (!isLoggedIn) return <LoginPrompt />;

  const handleOptimize = async () => {
    if (!jdText || !selectedResumeId) return;
    setIsOptimizing(true);
    setError("");
    try {
      const app = await extApi.createApplication({
        company: document.title || "Unknown",
        role_title: "Position",
        jd_snapshot: jdText,
        portal_url: window.location?.href,
      });
      setAppId(app.id);

      const result = await extApi.optimize(app.id, selectedResumeId);
      setOptimizeResult(result);
      setMutations(
        result.mutations.map((m, i) => ({ ...m, status: "pending" }))
      );
      setStep("diff");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Optimization failed");
    } finally {
      setIsOptimizing(false);
    }
  };

  const handleApply = async () => {
    const approved = mutations.filter(
      (m) => m.status === "approved" || m.status === "edited"
    );
    try {
      const result = await extApi.applyMutations(
        appId,
        selectedResumeId,
        approved
      );
      setApplyResult(result);
      setStep("done");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Apply failed");
    }
  };

  return (
    <div className="flex flex-col h-screen">
      <header className="px-4 py-3 border-b bg-zinc-50 flex items-center justify-between">
        <h1 className="font-bold text-sm">Resume Optimizer</h1>
        {jdSource && (
          <span className="text-xs text-zinc-400">via {jdSource}</span>
        )}
      </header>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {error && (
          <div className="bg-red-50 text-red-700 text-xs p-2 rounded">
            {error}
          </div>
        )}

        {step === "jd" && (
          <>
            <JDPreview text={jdText} onChange={setJdText} />
            <ResumePicker
              selected={selectedResumeId}
              onSelect={setSelectedResumeId}
            />
            <OptimizeButton
              disabled={!jdText || !selectedResumeId}
              loading={isOptimizing}
              onClick={handleOptimize}
            />
          </>
        )}

        {step === "diff" && (
          <>
            <MiniDiffViewer
              mutations={mutations}
              onUpdate={(idx, update) =>
                setMutations((prev) =>
                  prev.map((m, i) => (i === idx ? { ...m, ...update } : m))
                )
              }
              onApproveAll={() =>
                setMutations((prev) =>
                  prev.map((m) => ({ ...m, status: "approved" }))
                )
              }
            />
            <button
              className="w-full py-2 bg-zinc-900 text-white rounded-lg text-sm font-medium disabled:opacity-50"
              disabled={mutations.every((m) => m.status === "pending")}
              onClick={handleApply}
            >
              Apply Approved Changes
            </button>
          </>
        )}

        {step === "done" && applyResult && (
          <DownloadButton
            versionId={applyResult.version_id}
            versionNumber={applyResult.version_number}
            atsScore={applyResult.ats_score}
          />
        )}
      </div>
    </div>
  );
}
