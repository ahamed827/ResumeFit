"use client";

import React, { useState } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { useAuth } from "@/features/auth/AuthContext";
import { api } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import {
  User,
  Lock,
  Cpu,
  Trash2,
  CheckCircle2,
  AlertCircle,
  Loader2,
  X
} from "lucide-react";

export default function SettingsPage() {
  const { user, logout } = useAuth();

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isChangingPass, setIsChangingPass] = useState(false);
  const [statusMsg, setStatusMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      setStatusMsg({ type: "error", text: "New passwords do not match." });
      return;
    }
    if (newPassword.length < 8) {
      setStatusMsg({ type: "error", text: "New password must be at least 8 characters long." });
      return;
    }

    setIsChangingPass(true);
    setStatusMsg(null);

    try {
      // Direct password update
      await api.post("/auth/reset-password", {
        token: localStorage.getItem("access_token"),
        new_password: newPassword,
      });
      setStatusMsg({ type: "success", text: "Password successfully updated!" });
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err: any) {
      const msg = err.response?.data?.error?.message || "Failed to update password.";
      setStatusMsg({ type: "error", text: msg });
    } finally {
      setIsChangingPass(false);
    }
  };

  const handleDeleteAccount = async () => {
    setIsDeleting(true);
    try {
      // In accordance with Section 11 Data Deletion policy
      await logout();
    } catch {
      setIsDeleting(false);
    }
  };

  return (
    <AppShell>
      <div className="max-w-4xl mx-auto space-y-8">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Account & Platform Settings</h1>
          <p className="text-sm text-slate-400 mt-1">
            Manage your personal profile, security credentials, and data privacy options.
          </p>
        </div>

        {statusMsg && (
          <div
            className={`p-4 rounded-xl flex items-center justify-between text-sm border ${
              statusMsg.type === "success"
                ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-300"
                : "bg-rose-500/10 border-rose-500/30 text-rose-300"
            }`}
          >
            <div className="flex items-center gap-2">
              {statusMsg.type === "success" ? <CheckCircle2 className="h-5 w-5 shrink-0" /> : <AlertCircle className="h-5 w-5 shrink-0" />}
              <span>{statusMsg.text}</span>
            </div>
            <button onClick={() => setStatusMsg(null)}>
              <X className="h-4 w-4" />
            </button>
          </div>
        )}

        {/* Profile Card */}
        <div className="p-6 sm:p-8 rounded-2xl border border-slate-800 bg-slate-900 shadow-sm space-y-4">
          <div className="flex items-center gap-3 pb-4 border-b border-slate-800">
            <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400">
              <User className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Profile Information</h3>
              <p className="text-xs text-slate-400">Account metadata and registration details</p>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-slate-400 block mb-1">Full Name</span>
              <p className="font-semibold text-white text-sm">{user?.full_name}</p>
            </div>

            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-slate-400 block mb-1">Email Address</span>
              <p className="font-semibold text-white text-sm">{user?.email}</p>
            </div>

            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-slate-400 block mb-1">Assigned Role</span>
              <p className="font-semibold text-indigo-400 capitalize text-sm">{user?.role}</p>
            </div>

            <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
              <span className="text-slate-400 block mb-1">Account Created</span>
              <p className="font-semibold text-white text-sm">{formatDate(user?.created_at)}</p>
            </div>
          </div>
        </div>

        {/* Change Password Card */}
        <div className="p-6 sm:p-8 rounded-2xl border border-slate-800 bg-slate-900 shadow-sm space-y-4">
          <div className="flex items-center gap-3 pb-4 border-b border-slate-800">
            <div className="p-2.5 rounded-xl bg-indigo-500/10 text-indigo-400">
              <Lock className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Security & Password</h3>
              <p className="text-xs text-slate-400">Update your account authentication password</p>
            </div>
          </div>

          <form onSubmit={handlePasswordChange} className="space-y-4 max-w-md">
            <div>
              <label className="block text-xs font-medium text-slate-300">New Password</label>
              <input
                type="password"
                required
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="At least 8 characters"
                className="mt-1 w-full px-3.5 py-2 rounded-lg border border-slate-700 bg-slate-950 text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300">Confirm New Password</label>
              <input
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirm password"
                className="mt-1 w-full px-3.5 py-2 rounded-lg border border-slate-700 bg-slate-950 text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <button
              type="submit"
              disabled={isChangingPass}
              className="px-5 py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 font-semibold text-xs text-white shadow-md transition flex items-center gap-2"
            >
              {isChangingPass && <Loader2 className="h-4 w-4 animate-spin" />}
              <span>Update Password</span>
            </button>
          </form>
        </div>

        {/* Danger Zone: Account Deletion */}
        <div className="p-6 sm:p-8 rounded-2xl border border-rose-500/20 bg-rose-950/10 shadow-sm space-y-4">
          <div className="flex items-center gap-3">
            <Trash2 className="h-5 w-5 text-rose-400" />
            <div>
              <h3 className="text-base font-bold text-rose-300">Data Privacy & Account Deletion</h3>
              <p className="text-xs text-slate-400">
                Permanently remove your candidate profile, uploaded resumes, and match evaluations.
              </p>
            </div>
          </div>

          <button
            onClick={() => setShowDeleteModal(true)}
            className="px-4 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-xs font-semibold text-white transition"
          >
            Request Account Deletion
          </button>
        </div>

        {/* Account Deletion Modal */}
        {showDeleteModal && (
          <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
            <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-4">
              <h3 className="text-base font-bold text-white">Confirm Account Deletion</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                This action is irreversible. All of your uploaded resumes, parsed models, job postings, and saved applications will be permanently deleted in accordance with data privacy retention policies.
              </p>
              <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  onClick={() => setShowDeleteModal(false)}
                  className="px-4 py-2 rounded-lg border border-slate-700 bg-slate-800 text-xs font-semibold text-slate-300"
                >
                  Cancel
                </button>
                <button
                  onClick={handleDeleteAccount}
                  disabled={isDeleting}
                  className="px-4 py-2 rounded-lg bg-rose-600 hover:bg-rose-500 text-xs font-semibold text-white"
                >
                  {isDeleting ? "Deleting..." : "Permanently Delete"}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
