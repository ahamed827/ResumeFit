"use client";

import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AppShell } from "@/components/layout/AppShell";
import { api } from "@/lib/api";
import { Resume, Job } from "@/types";
import {
  Layers,
  FileText,
  Briefcase,
  ArrowRight,
  Loader2,
  CheckCircle2,
  AlertCircle,
  Sparkles
} from "lucide-react";

export default function NewMatchPage() {
  const router = useRouter();
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedResumeId, setSelectedResumeId] = useState<string>("");
  const [selectedJobId, setSelectedJobId] = useState<string>("");
  const [isLoading, setIsLoading] = useState(true);
  const [isMatching, setIsMatching] = useState(false);
  const [progressStep, setProgressStep] = useState(0);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const steps = [
    "Normalizing skill aliases and generating vector embeddings...",
    "Running multi-factor semantic alignment check...",
    "Validating evidence quotes from candidate projects & history...",
    "Synthesizing 6-factor deterministic score and improvement plan..."
  ];

  useEffect(() => {
    async function loadResources() {
      try {
        const [resumesRes, jobsRes] = await Promise.all([
          api.get("/resumes"),
          api.get("/jobs"),
        ]);
        const rItems = resumesRes.data.items.filter((r: Resume) => r.extraction_status === "completed");
        const jItems = jobsRes.data.items.filter((j: Job) => j.analysis_status === "completed");

        setResumes(rItems);
        setJobs(jItems);

        if (rItems.length > 0) setSelectedResumeId(rItems[0].id);
        if (jItems.length > 0) setSelectedJobId(jItems[0].id);
      } catch (err) {
        console.error("Failed to load matching candidates:", err);
      } finally {
        setIsLoading(false);
      }
    }
    loadResources();
  }, []);

  const handleRunMatch = async () => {
    if (!selectedResumeId || !selectedJobId) {
      setErrorMsg("Please select both a resume and a target job.");
      return;
    }

    setIsMatching(true);
    setErrorMsg(null);
    setProgressStep(0);

    const stepInterval = setInterval(() => {
      setProgressStep((prev) => (prev < steps.length - 1 ? prev + 1 : prev));
    }, 900);

    try {
      const res = await api.post("/matches", {
        resume_id: selectedResumeId,
        job_id: selectedJobId,
      });

      clearInterval(stepInterval);
      router.push(`/matches/${res.data.id}`);
    } catch (err: any) {
      clearInterval(stepInterval);
      setIsMatching(false);
      const msg = err.response?.data?.error?.message || "Matching calculation failed.";
      setErrorMsg(msg);
    }
  };

  return (
    <AppShell>
      <div className="max-w-4xl mx-auto space-y-8">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-semibold mb-2">
            <Sparkles className="h-3.5 w-3.5" />
            <span>Multi-Stage Matching Pipeline</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Run Resume-to-Job Match Evaluation
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Compare candidate profile against job specifications to generate an explainable score, evidence mapping, and an actionable roadmap.
          </p>
        </div>

        {errorMsg && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm flex items-center gap-3">
            <AlertCircle className="h-5 w-5 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {isMatching ? (
          <div className="p-12 rounded-2xl border border-slate-800 bg-slate-900 shadow-xl text-center space-y-6">
            <Loader2 className="h-12 w-12 text-indigo-500 animate-spin mx-auto" />
            <div>
              <h3 className="text-lg font-bold text-white">Analyzing Compatibility</h3>
              <p className="text-sm text-indigo-400 mt-2 font-medium animate-pulse">
                {steps[progressStep]}
              </p>
            </div>
            <div className="w-full max-w-md mx-auto bg-slate-800 h-2 rounded-full overflow-hidden">
              <div
                className="bg-indigo-500 h-full transition-all duration-700"
                style={{ width: `${((progressStep + 1) / steps.length) * 100}%` }}
              ></div>
            </div>
          </div>
        ) : isLoading ? (
          <div className="p-12 text-center bg-slate-900 border border-slate-800 rounded-2xl">
            <Loader2 className="h-8 w-8 text-indigo-500 animate-spin mx-auto mb-2" />
            <p className="text-sm text-slate-400">Loading your candidate profiles and job postings...</p>
          </div>
        ) : resumes.length === 0 || jobs.length === 0 ? (
          <div className="p-8 rounded-2xl border border-slate-800 bg-slate-900 text-center space-y-4">
            <AlertCircle className="h-10 w-10 text-amber-400 mx-auto" />
            <h3 className="text-base font-bold text-white">Prerequisites Needed</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto">
              You need at least one completed resume and one completed job description in your library to start evaluation.
            </p>
            <div className="flex justify-center gap-4 pt-2">
              {resumes.length === 0 && (
                <button
                  onClick={() => router.push("/resumes")}
                  className="px-4 py-2 rounded-lg bg-indigo-600 text-xs font-semibold text-white"
                >
                  Upload a Resume
                </button>
              )}
              {jobs.length === 0 && (
                <button
                  onClick={() => router.push("/jobs")}
                  className="px-4 py-2 rounded-lg bg-slate-800 border border-slate-700 text-xs font-semibold text-white"
                >
                  Add a Target Job
                </button>
              )}
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Select Resume Card */}
              <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900 space-y-4 shadow-sm">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400">
                    <FileText className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-white">Select Candidate Resume</h3>
                    <p className="text-xs text-slate-400">Choose from your parsed resumes</p>
                  </div>
                </div>

                <div className="space-y-2 pt-2">
                  {resumes.map((resume) => {
                    const isSelected = selectedResumeId === resume.id;
                    return (
                      <div
                        key={resume.id}
                        onClick={() => setSelectedResumeId(resume.id)}
                        className={`p-3.5 rounded-xl border cursor-pointer transition flex items-center justify-between ${
                          isSelected
                            ? "bg-slate-800 border-indigo-500 ring-1 ring-indigo-500/40 text-white"
                            : "bg-slate-950/60 border-slate-800 hover:border-slate-700 text-slate-300"
                        }`}
                      >
                        <div className="min-w-0">
                          <p className="text-sm font-semibold truncate">{resume.original_filename}</p>
                          <p className="text-xs text-slate-500 mt-0.5">
                            {resume.structured_profile?.skills?.length || 0} skills identified
                          </p>
                        </div>
                        {isSelected && <CheckCircle2 className="h-4 w-4 text-indigo-400 shrink-0" />}
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Select Job Card */}
              <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900 space-y-4 shadow-sm">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400">
                    <Briefcase className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-white">Select Target Job</h3>
                    <p className="text-xs text-slate-400">Choose from your analyzed jobs</p>
                  </div>
                </div>

                <div className="space-y-2 pt-2">
                  {jobs.map((job) => {
                    const isSelected = selectedJobId === job.id;
                    return (
                      <div
                        key={job.id}
                        onClick={() => setSelectedJobId(job.id)}
                        className={`p-3.5 rounded-xl border cursor-pointer transition flex items-center justify-between ${
                          isSelected
                            ? "bg-slate-800 border-indigo-500 ring-1 ring-indigo-500/40 text-white"
                            : "bg-slate-950/60 border-slate-800 hover:border-slate-700 text-slate-300"
                        }`}
                      >
                        <div className="min-w-0">
                          <p className="text-sm font-semibold truncate">{job.title}</p>
                          <p className="text-xs text-slate-500 mt-0.5">
                            {job.company_name || "Company Unspecified"}
                          </p>
                        </div>
                        {isSelected && <CheckCircle2 className="h-4 w-4 text-indigo-400 shrink-0" />}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Launch Button */}
            <div className="flex justify-end pt-4">
              <button
                onClick={handleRunMatch}
                disabled={!selectedResumeId || !selectedJobId}
                className="flex items-center gap-2 px-8 py-3.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 font-bold text-sm text-white shadow-xl shadow-indigo-600/30 transition disabled:opacity-50"
              >
                <span>Generate Match Evaluation</span>
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
