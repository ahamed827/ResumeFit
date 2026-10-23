"use client";

import React, { useEffect, useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { api } from "@/lib/api";
import { AdminMetrics, User } from "@/types";
import { formatDate } from "@/lib/utils";
import {
  ShieldAlert,
  Users,
  FileText,
  Briefcase,
  Layers,
  Cpu,
  Clock,
  DollarSign,
  AlertTriangle,
  CheckCircle2,
  Loader2,
  RefreshCw,
  Power
} from "lucide-react";

export default function AdminPage() {
  const [metrics, setMetrics] = useState<AdminMetrics | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [aiLogs, setAiLogs] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchAdminData = async () => {
    try {
      const [mRes, uRes, lRes] = await Promise.allSettled([
        api.get("/admin/metrics"),
        api.get("/admin/users"),
        api.get("/admin/ai-usage?limit=10"),
      ]);

      if (mRes.status === "fulfilled") setMetrics(mRes.value.data);
      if (uRes.status === "fulfilled") setUsers(uRes.value.data.items);
      if (lRes.status === "fulfilled") setAiLogs(lRes.value.data.items);
    } catch (err) {
      console.error("Failed to load admin telemetry:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAdminData();
  }, []);

  const toggleUserStatus = async (userId: string, currentStatus: boolean) => {
    try {
      await api.patch(`/admin/users/${userId}/status`, { is_active: !currentStatus });
      await fetchAdminData();
    } catch (err) {
      console.error("Failed to update user status:", err);
    }
  };

  return (
    <AppShell requireRole="admin">
      <div className="space-y-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs font-semibold mb-2">
              <ShieldAlert className="h-3.5 w-3.5" />
              <span>Platform Administration & Observability</span>
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">Admin Telemetry Dashboard</h1>
            <p className="text-xs text-slate-400 mt-1">
              Real-time platform metrics, AI success rates, latency, cost observability, and user management.
            </p>
          </div>

          <button
            onClick={() => {
              setIsLoading(true);
              fetchAdminData();
            }}
            className="flex items-center gap-2 px-3 py-2 rounded-lg border border-slate-700 bg-slate-900 text-xs font-semibold text-slate-300 hover:text-white"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            <span>Refresh Telemetry</span>
          </button>
        </div>

        {/* 6 Platform Metrics */}
        {metrics && (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            <div className="p-4 rounded-xl border border-slate-800 bg-slate-900 flex flex-col justify-between">
              <span className="text-[11px] font-semibold text-slate-400 uppercase">Users</span>
              <p className="text-2xl font-extrabold text-white mt-1">{metrics.total_users}</p>
            </div>
            <div className="p-4 rounded-xl border border-slate-800 bg-slate-900 flex flex-col justify-between">
              <span className="text-[11px] font-semibold text-slate-400 uppercase">Resumes</span>
              <p className="text-2xl font-extrabold text-white mt-1">{metrics.total_resumes_processed}</p>
            </div>
            <div className="p-4 rounded-xl border border-slate-800 bg-slate-900 flex flex-col justify-between">
              <span className="text-[11px] font-semibold text-slate-400 uppercase">Jobs</span>
              <p className="text-2xl font-extrabold text-white mt-1">{metrics.total_jobs_analyzed}</p>
            </div>
            <div className="p-4 rounded-xl border border-slate-800 bg-slate-900 flex flex-col justify-between">
              <span className="text-[11px] font-semibold text-slate-400 uppercase">Matches</span>
              <p className="text-2xl font-extrabold text-white mt-1">{metrics.total_matches_generated}</p>
            </div>
            <div className="p-4 rounded-xl border border-slate-800 bg-slate-900 flex flex-col justify-between">
              <span className="text-[11px] font-semibold text-slate-400 uppercase">AI Success</span>
              <p className="text-2xl font-extrabold text-emerald-400 mt-1">{metrics.ai_success_rate}%</p>
            </div>
            <div className="p-4 rounded-xl border border-slate-800 bg-slate-900 flex flex-col justify-between">
              <span className="text-[11px] font-semibold text-slate-400 uppercase">Avg Latency</span>
              <p className="text-2xl font-extrabold text-indigo-400 mt-1">{metrics.average_ai_latency_ms}ms</p>
            </div>
          </div>
        )}

        {/* Top Missing Skills & Target Roles */}
        {metrics && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900 space-y-4">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                Most Common Missing Skills Across Candidates
              </h3>
              <div className="space-y-2">
                {metrics.most_common_missing_skills.map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-xs">
                    <span className="font-semibold text-slate-200">{item.skill}</span>
                    <span className="px-2 py-0.5 rounded font-mono bg-rose-500/10 text-rose-300 border border-rose-500/20">
                      {item.count} gaps identified
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900 space-y-4">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                Most Popular Target Roles
              </h3>
              <div className="space-y-2">
                {metrics.most_common_target_roles.map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-xs">
                    <span className="font-semibold text-slate-200">{item.role}</span>
                    <span className="px-2 py-0.5 rounded font-mono bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                      {item.count} postings
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* User Management Table */}
        <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900 shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-white">Platform Users ({users.length})</h3>
            <span className="text-xs text-slate-500">Privacy rule: Candidate resume contents masked from UI</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase font-semibold">
                  <th className="pb-3">User</th>
                  <th className="pb-3">Role</th>
                  <th className="pb-3">Registered</th>
                  <th className="pb-3">Status</th>
                  <th className="pb-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-800/40">
                    <td className="py-3">
                      <p className="font-semibold text-white">{u.full_name}</p>
                      <p className="text-[11px] text-slate-500">{u.email}</p>
                    </td>
                    <td className="py-3 capitalize text-slate-300">{u.role}</td>
                    <td className="py-3 text-slate-400">{formatDate(u.created_at)}</td>
                    <td className="py-3">
                      <span
                        className={`px-2 py-0.5 rounded-full font-bold text-[10px] ${
                          u.is_active
                            ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                            : "bg-rose-500/10 text-rose-400 border border-rose-500/30"
                        }`}
                      >
                        {u.is_active ? "Active" : "Disabled"}
                      </span>
                    </td>
                    <td className="py-3 text-right">
                      {u.role !== "admin" && (
                        <button
                          onClick={() => toggleUserStatus(u.id, u.is_active)}
                          className={`px-2.5 py-1 rounded text-xs font-semibold transition ${
                            u.is_active
                              ? "bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30"
                              : "bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                          }`}
                        >
                          {u.is_active ? "Deactivate" : "Activate"}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* AI Usage Logs */}
        <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900 shadow-sm space-y-4">
          <h3 className="text-base font-bold text-white">Recent AI Task Logs</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase font-semibold">
                  <th className="pb-3">Task Type</th>
                  <th className="pb-3">Model</th>
                  <th className="pb-3">Tokens</th>
                  <th className="pb-3">Est. Cost</th>
                  <th className="pb-3">Latency</th>
                  <th className="pb-3">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {aiLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-800/40">
                    <td className="py-2.5 font-sans capitalize text-slate-200">
                      {log.task_type.replace("_", " ")}
                    </td>
                    <td className="py-2.5 text-indigo-400">{log.model_name}</td>
                    <td className="py-2.5 text-slate-300">{log.total_tokens}</td>
                    <td className="py-2.5 text-slate-300">${Number(log.estimated_cost_usd).toFixed(5)}</td>
                    <td className="py-2.5 text-slate-300">{log.latency_ms}ms</td>
                    <td className="py-2.5 font-sans">
                      <span className="text-emerald-400 font-semibold">{log.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
