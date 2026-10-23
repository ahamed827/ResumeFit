import React from "react";
import Link from "next/link";
import {
  Sparkles,
  FileCheck,
  Target,
  TrendingUp,
  ShieldCheck,
  CheckCircle2,
  ArrowRight,
  Code2,
  Cpu
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Top Header */}
      <header className="border-b border-slate-800/80 bg-slate-900/50 backdrop-blur sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 font-bold text-xl">
            <div className="h-8 w-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white shadow-md shadow-indigo-600/30">
              <Sparkles className="h-5 w-5" />
            </div>
            <span>Resume<span className="text-indigo-400">Fit</span></span>
          </div>

          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="text-sm font-medium text-slate-300 hover:text-white px-3 py-2 transition"
            >
              Sign In
            </Link>
            <Link
              href="/register"
              className="text-sm font-semibold bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg shadow-md shadow-indigo-600/20 transition"
            >
              Get Started Free
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-20 pb-24 md:pt-28 md:pb-32">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-xs font-semibold text-indigo-300 mb-6">
            <Sparkles className="h-3.5 w-3.5" />
            <span>AI-Powered Resume-to-Job Optimization Engine</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white mb-6 leading-tight">
            Know Exactly How Well You Match Before You Apply.
          </h1>

          <p className="text-lg sm:text-xl text-slate-400 max-w-3xl mx-auto mb-10 leading-relaxed">
            Stop sending blind applications. Upload your resume and job description to get a transparent 0–100 match score, evidence-backed skill breakdown, and a personalized plan to bridge every gap.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/register"
              className="w-full sm:w-auto flex items-center justify-center gap-2 px-8 py-3.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 font-semibold text-white shadow-lg shadow-indigo-600/30 transition"
            >
              <span>Analyze Your Resume Now</span>
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/login"
              className="w-full sm:w-auto px-8 py-3.5 rounded-lg border border-slate-700 bg-slate-900/60 hover:bg-slate-800 text-slate-200 font-medium transition"
            >
              View Live Demo
            </Link>
          </div>
        </div>
      </section>

      {/* 3 Step Workflow */}
      <section className="py-20 border-t border-slate-800 bg-slate-900/40">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-2xl sm:text-3xl font-bold text-white mb-3">How ResumeFit Works</h2>
            <p className="text-slate-400">Deterministic scoring combined with multi-stage LLM intelligence.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/80 shadow-sm flex flex-col items-start">
              <div className="h-12 w-12 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center mb-5">
                <FileCheck className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">1. Upload & Extract</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Upload your PDF or DOCX resume. Our parser structures your skills, education, work experience, and projects into verified schemas.
              </p>
            </div>

            <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/80 shadow-sm flex flex-col items-start">
              <div className="h-12 w-12 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center mb-5">
                <Target className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">2. Match & Score</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                We run alias-aware semantic skill matching across 6 weighted components to deliver an objective 0–100 score with exact resume evidence.
              </p>
            </div>

            <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/80 shadow-sm flex flex-col items-start">
              <div className="h-12 w-12 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center mb-5">
                <TrendingUp className="h-6 w-6" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">3. Bridge the Gap</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Receive recommended learning resources, portfolio-grade project ideas, tailored professional summaries, and complete application tracking.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Highlights */}
      <section className="py-20 border-t border-slate-800">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-white mb-6">
                Transparent & Explainable. No Black-Box Guesswork.
              </h2>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="h-5 w-5 text-indigo-400 mt-0.5 shrink-0" />
                  <p className="text-slate-300 text-sm">
                    <strong>Evidence-Based Verification:</strong> Every matched requirement is directly paired with verbatim evidence from your resume.
                  </p>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="h-5 w-5 text-indigo-400 mt-0.5 shrink-0" />
                  <p className="text-slate-300 text-sm">
                    <strong>Alias-Aware Matching:</strong> Automatically recognizes that "JS" is JavaScript, "K8s" is Kubernetes, and "Node" is Node.js.
                  </p>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="h-5 w-5 text-indigo-400 mt-0.5 shrink-0" />
                  <p className="text-slate-300 text-sm">
                    <strong>Weighted 6-Factor Scoring:</strong> Required skills (40%), Experience (20%), Nice-to-haves (15%), Projects (10%), Education (10%), Seniority (5%).
                  </p>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="h-5 w-5 text-indigo-400 mt-0.5 shrink-0" />
                  <p className="text-slate-300 text-sm">
                    <strong>Full Application Tracking:</strong> Organize every opportunity through Saved, Applied, Screening, Interview, and Offer stages.
                  </p>
                </div>
              </div>
            </div>

            <div className="p-8 rounded-2xl border border-slate-800 bg-slate-900 shadow-2xl relative">
              <div className="flex items-center justify-between pb-6 border-b border-slate-800">
                <div>
                  <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider">Evaluation Sample</span>
                  <h4 className="text-lg font-bold text-white">Full-Stack Engineer Match</h4>
                </div>
                <div className="h-12 w-12 rounded-full border-4 border-emerald-500/30 border-t-emerald-400 flex items-center justify-center font-bold text-emerald-400">
                  88
                </div>
              </div>
              <div className="py-4 space-y-3">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-400">Required Skills (40%)</span>
                  <span className="text-emerald-400 font-semibold">92%</span>
                </div>
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div className="bg-emerald-400 h-full rounded-full" style={{ width: "92%" }}></div>
                </div>

                <div className="flex justify-between text-xs pt-1">
                  <span className="text-slate-400">Projects & Practical (10%)</span>
                  <span className="text-emerald-400 font-semibold">100%</span>
                </div>
                <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div className="bg-emerald-400 h-full rounded-full" style={{ width: "100%" }}></div>
                </div>
              </div>
              <div className="pt-4 border-t border-slate-800 text-xs text-slate-400 italic">
                "Candidate demonstrates verified proficiency in React, TypeScript, and FastAPI with 3 production-grade portfolio projects."
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="mt-auto border-t border-slate-800/80 py-8 text-center text-xs text-slate-500">
        <p>&copy; {new Date().getFullYear()} ResumeFit. Built for Computer Science Graduates & Tech Job Seekers.</p>
      </footer>
    </div>
  );
}
