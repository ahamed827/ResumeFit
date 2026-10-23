"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { AppShell } from "@/components/layout/AppShell";
import { useAuth } from "@/features/auth/AuthContext";
import { api } from "@/lib/api";
import {
  FileText,
  Briefcase,
  Layers,
  CheckSquare,
  PlusCircle,
  TrendingUp,
  ArrowUpRight,
  Clock,
  Sparkles,
  AlertCircle
} from "lucide-react";

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    resumesCount: 0,
    jobsCount: 0,
    matchesCount: 0,
    applicationsCount: 0,
    applicationsByStatus: {} as Record<string, number>,
  });
  const [recentMatches, setRecentMatches] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadDashboardData() {
      try {
        const [resumesRes, jobsRes, matchesRes, appsRes] = await Promise.allSettled([
          api.get("/resumes?limit=5"),
          api.get("/jobs?limit=5"),
          api.get("/matches?limit=5"),
          api.get("/applications/stats"),
        ]);

        const resumesCount = resumesRes.status === "fulfilled" ? resumesRes.value.data.total : 0;
        const jobsCount = jobsRes.status === "fulfilled" ? jobsRes.value.data.total : 0;
        const matchesCount = matchesRes.status === "fulfilled" ? matchesRes.value.data.total : 0;
        const matchesItems = matchesRes.status === "fulfilled" ? matchesRes.value.data.items : [];
        const appStats = appsRes.status === "fulfilled" ? appsRes.value.data : { total_applications: 0, by_status: {} };

        setStats({
          resumesCount,
          jobsCount,
          matchesCount,
          applicationsCount: appStats.total_applications,
          applicationsByStatus: appStats.by_status,
        });
        setRecentMatches(matchesItems);
      } catch (err) {
        console.error("Dashboard data load error:", err);
      } finally {
        setIsLoading(false);
      }
    }

    loadDashboardData();
  }, []);

  return (
    <AppShell>
      <div className="space-y-8">
        {/* Welcome Banner */}
        <div className="p-6 sm:p-8 rounded-2xl bg-gradient-to-r from-indigo-950/80 via-slate-900 to-slate-900 border border-indigo-500/20 shadow-xl flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 text-xs font-semibold mb-3">
              <Sparkles className="h-3.5 w-3.5" />
              <span>Career Optimization Engine</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              Welcome back, {user?.full_name}!
            </h1>
            <p className="mt-2 text-sm text-slate-300 max-w-xl">
              Compare your resumes against target roles, identify critical skill gaps, and track your applications to offer stage.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Link
              href="/matches/new"
              className="flex items-center gap-2 px-4 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-sm shadow-md shadow-indigo-600/30 transition"
            >
              <Layers className="h-4 w-4" />
              <span>Run Match Evaluation</span>
            </Link>
            <Link
              href="/resumes"
              className="flex items-center gap-2 px-4 py-2.5 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium text-sm transition"
            >
              <FileText className="h-4 w-4" />
              <span>Upload Resume</span>
            </Link>
          </div>
        </div>

        {/* 4 Overview Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          <div className="p-5 rounded-xl border border-slate-800 bg-slate-900 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Resumes</p>
              <p className="text-2xl font-bold text-white mt-1">{stats.resumesCount}</p>
              <Link href="/resumes" className="text-xs text-indigo-400 hover:underline mt-2 inline-flex items-center gap-1">
                Manage library <ArrowUpRight className="h-3 w-3" />
              </Link>
            </div>
            <div className="h-12 w-12 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center">
              <FileText className="h-6 w-6" />
            </div>
          </div>

          <div className="p-5 rounded-xl border border-slate-800 bg-slate-900 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Jobs Analyzed</p>
              <p className="text-2xl font-bold text-white mt-1">{stats.jobsCount}</p>
              <Link href="/jobs" className="text-xs text-indigo-400 hover:underline mt-2 inline-flex items-center gap-1">
                View postings <ArrowUpRight className="h-3 w-3" />
              </Link>
            </div>
            <div className="h-12 w-12 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center">
              <Briefcase className="h-6 w-6" />
            </div>
          </div>

          <div className="p-5 rounded-xl border border-slate-800 bg-slate-900 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Matches Evaluated</p>
              <p className="text-2xl font-bold text-white mt-1">{stats.matchesCount}</p>
              <Link href="/matches/new" className="text-xs text-indigo-400 hover:underline mt-2 inline-flex items-center gap-1">
                Compare new <ArrowUpRight className="h-3 w-3" />
              </Link>
            </div>
            <div className="h-12 w-12 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center">
              <TrendingUp className="h-6 w-6" />
            </div>
          </div>

          <div className="p-5 rounded-xl border border-slate-800 bg-slate-900 shadow-sm flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Applications</p>
              <p className="text-2xl font-bold text-white mt-1">{stats.applicationsCount}</p>
              <Link href="/applications" className="text-xs text-indigo-400 hover:underline mt-2 inline-flex items-center gap-1">
                Open tracker <ArrowUpRight className="h-3 w-3" />
              </Link>
            </div>
            <div className="h-12 w-12 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center">
              <CheckSquare className="h-6 w-6" />
            </div>
          </div>
        </div>

        {/* Application Stage Breakdown */}
        <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-bold text-white">Application Pipeline Status</h2>
            <Link href="/applications" className="text-xs font-semibold text-indigo-400 hover:underline">
              View Kanban Board
            </Link>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-3">
            {[
              { key: "saved", label: "Saved", color: "bg-slate-700 text-slate-300" },
              { key: "applied", label: "Applied", color: "bg-blue-500/20 text-blue-400" },
              { key: "screening", label: "Screening", color: "bg-purple-500/20 text-purple-400" },
              { key: "interview", label: "Interview", color: "bg-amber-500/20 text-amber-400" },
              { key: "technical_assessment", label: "Tech Assessment", color: "bg-indigo-500/20 text-indigo-400" },
              { key: "offer", label: "Offer", color: "bg-emerald-500/20 text-emerald-400" },
              { key: "rejected", label: "Rejected", color: "bg-rose-500/20 text-rose-400" },
              { key: "withdrawn", label: "Withdrawn", color: "bg-slate-800 text-slate-400" },
            ].map((stage) => {
              const count = stats.applicationsByStatus[stage.key] || 0;
              return (
                <div key={stage.key} className="p-3 rounded-lg border border-slate-800 bg-slate-950 flex flex-col items-center text-center">
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${stage.color}`}>
                    {stage.label}
                  </span>
                  <span className="text-xl font-bold text-white mt-2">{count}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Recent Matches Table */}
        <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900 shadow-sm">
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-base font-bold text-white">Recent Match Evaluations</h2>
            <Link href="/matches/new" className="text-xs font-semibold text-indigo-400 hover:underline flex items-center gap-1">
              <PlusCircle className="h-3.5 w-3.5" />
              New Evaluation
            </Link>
          </div>

          {recentMatches.length === 0 ? (
            <div className="py-10 text-center border border-dashed border-slate-800 rounded-xl">
              <Layers className="h-10 w-10 text-slate-600 mx-auto mb-2" />
              <p className="text-sm text-slate-400">No match evaluations generated yet.</p>
              <Link
                href="/matches/new"
                className="mt-3 inline-block text-xs font-semibold text-indigo-400 hover:text-indigo-300"
              >
                Match your first resume to a job &rarr;
              </Link>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-slate-800 text-xs font-semibold text-slate-400 uppercase">
                    <th className="pb-3">Overall Score</th>
                    <th className="pb-3">Matched Skills</th>
                    <th className="pb-3">Missing Skills</th>
                    <th className="pb-3">Status</th>
                    <th className="pb-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60">
                  {recentMatches.map((m) => {
                    const score = m.overall_score !== null ? Math.round(m.overall_score) : null;
                    const scoreColor =
                      score !== null
                        ? score >= 75
                          ? "text-emerald-400 border-emerald-500/30 bg-emerald-500/10"
                          : score >= 50
                          ? "text-amber-400 border-amber-500/30 bg-amber-500/10"
                          : "text-rose-400 border-rose-500/30 bg-rose-500/10"
                        : "text-slate-400 border-slate-700 bg-slate-800";

                    return (
                      <tr key={m.id} className="hover:bg-slate-800/40 transition">
                        <td className="py-3.5">
                          <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold border ${scoreColor}`}>
                            {score !== null ? `${score}/100` : "Pending"}
                          </span>
                        </td>
                        <td className="py-3.5 text-slate-300">
                          <span className="font-semibold text-emerald-400">{m.matched_skills?.length || 0}</span> matched
                        </td>
                        <td className="py-3.5 text-slate-300">
                          <span className="font-semibold text-rose-400">{m.missing_skills?.length || 0}</span> missing
                        </td>
                        <td className="py-3.5 capitalize text-xs font-medium text-slate-400">
                          {m.status}
                        </td>
                        <td className="py-3.5 text-right">
                          <Link
                            href={`/matches/${m.id}`}
                            className="text-xs font-semibold text-indigo-400 hover:text-indigo-300 hover:underline"
                          >
                            View Report &rarr;
                          </Link>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
