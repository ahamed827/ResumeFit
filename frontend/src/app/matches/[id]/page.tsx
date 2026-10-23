"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import { api } from "@/lib/api";
import { Match, SummaryResponse } from "@/types";
import {
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  HelpCircle,
  BookOpen,
  FolderGit2,
  TrendingUp,
  BookmarkPlus,
  FileText,
  Loader2,
  X,
  ExternalLink,
  Award,
  ShieldCheck,
  Check
} from "lucide-react";

export default function MatchReportPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();

  const [matchData, setMatchData] = useState<Match | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSavingApp, setIsSavingApp] = useState(false);
  const [appSaved, setAppSaved] = useState(false);

  // Summary generation modal state
  const [isSummaryModalOpen, setIsSummaryModalOpen] = useState(false);
  const [isGeneratingSummary, setIsGeneratingSummary] = useState(false);
  const [tailoredSummary, setTailoredSummary] = useState<SummaryResponse | null>(null);

  useEffect(() => {
    async function fetchMatch() {
      try {
        const res = await api.get(`/matches/${id}`);
        setMatchData(res.data);
      } catch (err) {
        console.error("Failed to load match report:", err);
      } finally {
        setIsLoading(false);
      }
    }
    if (id) fetchMatch();
  }, [id]);

  const handleSaveToApplicationTracker = async () => {
    if (!matchData) return;
    setIsSavingApp(true);
    try {
      await api.post("/applications", {
        job_id: matchData.job_id,
        resume_id: matchData.resume_id,
        status: "saved",
        notes: `Matched with overall score: ${matchData.overall_score || 0}%`,
      });
      setAppSaved(true);
    } catch (err) {
      console.error("Failed to save application:", err);
    } finally {
      setIsSavingApp(false);
    }
  };

  const handleGenerateSummary = async () => {
    if (!matchData) return;
    setIsGeneratingSummary(true);
    setIsSummaryModalOpen(true);
    try {
      const res = await api.post("/summaries", {
        resume_id: matchData.resume_id,
        job_id: matchData.job_id,
      });
      setTailoredSummary(res.data);
    } catch (err) {
      console.error("Failed to generate summary:", err);
    } finally {
      setIsGeneratingSummary(false);
    }
  };

  if (isLoading) {
    return (
      <AppShell>
        <div className="py-24 text-center">
          <Loader2 className="h-10 w-10 text-indigo-500 animate-spin mx-auto mb-4" />
          <p className="text-sm text-slate-400">Loading comprehensive match evaluation...</p>
        </div>
      </AppShell>
    );
  }

  if (!matchData) {
    return (
      <AppShell>
        <div className="py-16 text-center">
          <AlertTriangle className="h-12 w-12 text-rose-400 mx-auto mb-3" />
          <h2 className="text-lg font-bold text-white">Match Report Not Found</h2>
          <Link href="/matches/new" className="mt-4 inline-block text-sm text-indigo-400 hover:underline">
            &larr; Return to Match Engine
          </Link>
        </div>
      </AppShell>
    );
  }

  const score = matchData.overall_score != null ? Math.round(Number(matchData.overall_score)) : 0;
  const comp = matchData.component_scores || {
    required_skills: 0,
    experience_relevance: 0,
    nice_to_have_skills: 0,
    projects_and_practical: 0,
    education_fit: 0,
    seniority_alignment: 0,
  };

  return (
    <AppShell>
      <div className="space-y-8">
        {/* Top Action Bar */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-semibold mb-2">
              <ShieldCheck className="h-3.5 w-3.5" />
              <span>Verified Match Evaluation</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Match Analysis & Optimization Plan
            </h1>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleSaveToApplicationTracker}
              disabled={isSavingApp || appSaved}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold border transition ${
                appSaved
                  ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/40"
                  : "bg-slate-800 border-slate-700 text-slate-200 hover:bg-slate-700"
              }`}
            >
              {appSaved ? <Check className="h-4 w-4" /> : <BookmarkPlus className="h-4 w-4" />}
              <span>{appSaved ? "Saved to Applications" : "Save Application"}</span>
            </button>

            <button
              onClick={handleGenerateSummary}
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md shadow-indigo-600/30 transition"
            >
              <Sparkles className="h-4 w-4" />
              <span>Tailored Summary</span>
            </button>
          </div>
        </div>

        {/* Hero Score & Component Breakdown Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Circular Score Gauge */}
          <div className="lg:col-span-4 p-8 rounded-2xl border border-slate-800 bg-slate-900 shadow-xl flex flex-col items-center justify-center text-center">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">
              Overall Compatibility
            </span>
            <div className="relative h-40 w-40 flex items-center justify-center">
              <svg className="h-full w-full transform -rotate-90" viewBox="0 0 100 100">
                <circle
                  cx="50"
                  cy="50"
                  r="42"
                  className="text-slate-800"
                  strokeWidth="8"
                  stroke="currentColor"
                  fill="transparent"
                />
                <circle
                  cx="50"
                  cy="50"
                  r="42"
                  className={
                    score >= 75
                      ? "text-emerald-400"
                      : score >= 50
                      ? "text-amber-400"
                      : "text-rose-400"
                  }
                  strokeWidth="8"
                  strokeDasharray="264"
                  strokeDashoffset={264 - (264 * score) / 100}
                  strokeLinecap="round"
                  stroke="currentColor"
                  fill="transparent"
                />
              </svg>
              <div className="absolute flex flex-col items-center">
                <span className="text-4xl font-extrabold text-white">{score}</span>
                <span className="text-xs font-semibold text-slate-400">out of 100</span>
              </div>
            </div>

            <div className="mt-6 text-xs text-slate-400">
              {score >= 80 ? (
                <span className="text-emerald-400 font-semibold">Strong Candidate Match</span>
              ) : score >= 60 ? (
                <span className="text-amber-400 font-semibold">Moderate Fit with Bridgeable Gaps</span>
              ) : (
                <span className="text-rose-400 font-semibold">Substantial Skill Gaps Identified</span>
              )}
            </div>
          </div>

          {/* 6-Factor Component Score Bars */}
          <div className="lg:col-span-8 p-6 sm:p-8 rounded-2xl border border-slate-800 bg-slate-900 shadow-xl space-y-4">
            <h3 className="text-base font-bold text-white mb-2">Deterministic Scoring Components</h3>

            {[
              { label: "Required Core Skills (40% Weight)", value: comp.required_skills },
              { label: "Experience Relevance (20% Weight)", value: comp.experience_relevance },
              { label: "Nice-to-Have Skills (15% Weight)", value: comp.nice_to_have_skills },
              { label: "Projects & Practical Evidence (10% Weight)", value: comp.projects_and_practical },
              { label: "Education & Degree Fit (10% Weight)", value: comp.education_fit },
              { label: "Seniority Alignment (5% Weight)", value: comp.seniority_alignment },
            ].map((factor, idx) => (
              <div key={idx} className="space-y-1.5">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-300 font-medium">{factor.label}</span>
                  <span className="text-white font-bold">{Math.round(factor.value)}%</span>
                </div>
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all duration-500 ${
                      factor.value >= 75
                        ? "bg-emerald-400"
                        : factor.value >= 50
                        ? "bg-amber-400"
                        : "bg-rose-400"
                    }`}
                    style={{ width: `${Math.min(100, Math.max(0, factor.value))}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Human-Readable Explanation Callout */}
        {matchData.explanation && (
          <div className="p-6 rounded-2xl border border-indigo-500/20 bg-indigo-950/20 shadow-sm">
            <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-400 mb-2">
              Evaluation Synthesis
            </h4>
            <p className="text-sm text-slate-200 leading-relaxed">{matchData.explanation}</p>
          </div>
        )}

        {/* Strengths & Risks Panels */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-6 rounded-2xl border border-emerald-500/20 bg-slate-900 shadow-sm space-y-3">
            <div className="flex items-center gap-2 text-emerald-400">
              <CheckCircle2 className="h-5 w-5" />
              <h3 className="text-sm font-bold uppercase tracking-wider">Candidate Strengths</h3>
            </div>
            <ul className="space-y-2 text-xs text-slate-300">
              {(matchData.strengths || []).map((s, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-emerald-400 font-bold">•</span>
                  <span>{s}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="p-6 rounded-2xl border border-amber-500/20 bg-slate-900 shadow-sm space-y-3">
            <div className="flex items-center gap-2 text-amber-400">
              <AlertTriangle className="h-5 w-5" />
              <h3 className="text-sm font-bold uppercase tracking-wider">Risks & Considerations</h3>
            </div>
            <ul className="space-y-2 text-xs text-slate-300">
              {(matchData.risks || []).map((r, idx) => (
                <li key={idx} className="flex items-start gap-2">
                  <span className="text-amber-400 font-bold">•</span>
                  <span>{r}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Matched, Partial, and Missing Skills Details */}
        <div className="p-6 sm:p-8 rounded-2xl border border-slate-800 bg-slate-900 shadow-sm space-y-6">
          <h3 className="text-base font-bold text-white">Skills Alignment & Verifiable Resume Evidence</h3>

          {/* Matched skills */}
          <div>
            <h4 className="text-xs font-semibold text-emerald-400 uppercase tracking-wider mb-3">
              Matched Skills ({matchData.matched_skills?.length || 0})
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {matchData.matched_skills?.map((item, idx) => (
                <div key={idx} className="p-3.5 rounded-xl border border-emerald-500/20 bg-slate-950 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-bold text-white">{item.skill}</span>
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 capitalize">
                      {item.category || "Verified"}
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 italic">
                    Evidence: "{item.resume_evidence}"
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Missing skills */}
          {matchData.missing_skills?.length > 0 && (
            <div className="pt-4 border-t border-slate-800">
              <h4 className="text-xs font-semibold text-rose-400 uppercase tracking-wider mb-3">
                Missing Skills ({matchData.missing_skills.length})
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {matchData.missing_skills.map((item, idx) => (
                  <div key={idx} className="p-3 rounded-lg border border-rose-500/20 bg-slate-950 flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-200">{item.skill}</span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded capitalize ${
                        item.importance === "critical"
                          ? "bg-rose-500/20 text-rose-300"
                          : item.importance === "important"
                          ? "bg-amber-500/20 text-amber-300"
                          : "bg-slate-800 text-slate-400"
                      }`}
                    >
                      {item.importance.replace("_", " ")}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Partial skills */}
          {matchData.partial_skills?.length > 0 && (
            <div className="pt-4 border-t border-slate-800">
              <h4 className="text-xs font-semibold text-amber-400 uppercase tracking-wider mb-3">
                Partial or Transferable Skills
              </h4>
              <div className="space-y-2">
                {matchData.partial_skills.map((p, idx) => (
                  <div key={idx} className="p-3 rounded-lg bg-slate-950 border border-slate-800 text-xs">
                    <span className="font-bold text-white">{p.skill}</span> &larr; Transferable from{" "}
                    <span className="font-semibold text-indigo-400">{p.related_resume_skill}</span>
                    <p className="text-slate-400 mt-1">{p.explanation}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Personalized Improvement Plan */}
        {matchData.improvement_plan && (
          <div className="p-6 sm:p-8 rounded-2xl border border-slate-800 bg-slate-900 shadow-sm space-y-8">
            <div>
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-semibold mb-2">
                <TrendingUp className="h-3.5 w-3.5" />
                <span>Actionable Roadmap</span>
              </div>
              <h3 className="text-lg font-bold text-white">Personalized Career Improvement Plan</h3>
              <p className="text-xs text-slate-400 mt-1">
                Concrete steps, recommended learning topics, and practical projects designed to bridge this job's gaps.
              </p>
            </div>

            {/* Recommended Projects */}
            {matchData.improvement_plan.project_ideas?.length > 0 && (
              <div className="space-y-4">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                  <FolderGit2 className="h-4 w-4 text-indigo-400" />
                  <span>Recommended Portfolio Projects</span>
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {matchData.improvement_plan.project_ideas.map((proj, idx) => (
                    <div key={idx} className="p-5 rounded-xl border border-slate-800 bg-slate-950 space-y-3 flex flex-col justify-between">
                      <div>
                        <h5 className="text-sm font-bold text-white">{proj.title}</h5>
                        <p className="text-xs text-slate-400 mt-1">{proj.description}</p>
                        <div className="mt-3 flex flex-wrap gap-1.5">
                          {proj.technologies?.map((t, i) => (
                            <span key={i} className="text-[10px] px-2 py-0.5 rounded font-mono bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                              {t}
                            </span>
                          ))}
                        </div>
                      </div>
                      <ul className="mt-3 space-y-1 list-disc list-inside text-[11px] text-slate-400">
                        {proj.key_features?.map((f, i) => (
                          <li key={i}>{f}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Learning Resources */}
            {matchData.improvement_plan.learning_resources?.length > 0 && (
              <div className="space-y-4">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                  <BookOpen className="h-4 w-4 text-indigo-400" />
                  <span>Targeted Learning Resources</span>
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {matchData.improvement_plan.learning_resources.map((res, idx) => (
                    <a
                      key={idx}
                      href={res.url || "#"}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-3.5 rounded-lg border border-slate-800 bg-slate-950 hover:border-indigo-500/40 hover:bg-slate-900 transition flex items-center justify-between group"
                    >
                      <div className="min-w-0 pr-2">
                        <span className="text-[10px] font-bold uppercase text-indigo-400">{res.resource_type} • {res.topic}</span>
                        <p className="text-xs font-semibold text-white mt-0.5 truncate">{res.resource_name}</p>
                      </div>
                      <ExternalLink className="h-4 w-4 text-slate-500 group-hover:text-indigo-400 shrink-0" />
                    </a>
                  ))}
                </div>
              </div>
            )}

            {/* Resume Improvement Suggestions */}
            {matchData.improvement_plan.resume_improvements?.length > 0 && (
              <div className="space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
                  <FileText className="h-4 w-4 text-indigo-400" />
                  <span>Resume Improvements</span>
                </h4>
                <ul className="space-y-2 text-xs text-slate-300">
                  {matchData.improvement_plan.resume_improvements.map((tip, idx) => (
                    <li key={idx} className="flex items-start gap-2">
                      <span className="text-indigo-400 font-bold">&rarr;</span>
                      <span>{tip}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Tailored Summary Modal */}
        {isSummaryModalOpen && (
          <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-xl w-full p-6 shadow-2xl space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <h3 className="text-base font-bold text-white flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-indigo-400" />
                  <span>Tailored Resume Summary</span>
                </h3>
                <button onClick={() => setIsSummaryModalOpen(false)}>
                  <X className="h-5 w-5 text-slate-400 hover:text-white" />
                </button>
              </div>

              {isGeneratingSummary ? (
                <div className="py-12 text-center">
                  <Loader2 className="h-8 w-8 text-indigo-500 animate-spin mx-auto mb-2" />
                  <p className="text-xs text-slate-400">Synthesizing fact-verified summary for this role...</p>
                </div>
              ) : tailoredSummary ? (
                <div className="space-y-4 text-xs">
                  <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 leading-relaxed text-slate-200">
                    {tailoredSummary.generated_summary}
                  </div>

                  {tailoredSummary.supported_evidence?.length > 0 && (
                    <div>
                      <span className="font-semibold text-slate-400 block mb-1">Verified Facts Used:</span>
                      <ul className="space-y-1 list-disc list-inside text-slate-400">
                        {tailoredSummary.supported_evidence.map((ev, i) => (
                          <li key={i}>{ev}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(tailoredSummary.generated_summary);
                        alert("Summary copied to clipboard!");
                      }}
                      className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 font-semibold text-white text-xs"
                    >
                      Copy to Clipboard
                    </button>
                  </div>
                </div>
              ) : null}
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
