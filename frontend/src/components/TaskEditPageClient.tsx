'use client';

import { useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuth } from "@/lib/auth-client";
import { AuthGuard } from "../components/AuthGuard";
import { TaskForm } from "../components/TaskForm";
import { taskApi } from "@/lib/api";
import type { TaskUpdate } from "../types/task";

export default function TaskEditPageClient() {
  const router = useRouter();
  const params = useParams();
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [error, setError] = useState("");

  const taskId = params && params.id ? parseInt(params.id as string) : NaN;

  // Fetch task details
  const {
    data: task,
    isLoading,
    error: fetchError,
  } = useQuery({
    queryKey: ["task", taskId],
    queryFn: () => taskApi.get(user?.id || "", taskId),
    enabled: !!user?.id && !isNaN(taskId),
  });

  // Update task mutation
  const updateMutation = useMutation({
    mutationFn: (updatedTask: TaskUpdate) =>
      taskApi.update(user?.id || "", taskId, updatedTask),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["tasks"] });
      queryClient.invalidateQueries({ queryKey: ["task", taskId] });
      router.push("/tasks");
    },
    onError: (err: Error) => {
      setError(err.message || "Failed to update task");
    },
  });

  const handleUpdate = (taskData: TaskUpdate) => {
    setError("");
    updateMutation.mutate(taskData);
  };

  const handleCancel = () => {
    router.push("/tasks");
  };

  return (
    <AuthGuard>
      <div style={{ maxWidth: "800px", margin: "0 auto", padding: "20px" }}>
        <header style={{ marginBottom: "30px" }}>
          <h1>Edit Task</h1>
        </header>

        {isLoading && (
          <div style={{ textAlign: "center", padding: "40px" }}>
            <div>Loading task...</div>
          </div>
        )}

        {fetchError && (
          <div
            style={{
              padding: "20px",
              backgroundColor: "#fee",
              border: "1px solid #fcc",
              borderRadius: "4px",
              color: "#c00",
              marginBottom: "20px",
            }}
          >
            Error loading task: {(fetchError as Error).message}
          </div>
        )}

        {error && (
          <div
            style={{
              padding: "10px",
              marginBottom: "15px",
              backgroundColor: "#fee",
              border: "1px solid #fcc",
              borderRadius: "4px",
              color: "#c00",
            }}
          >
            {error}
          </div>
        )}

        {task && (
          <TaskForm
            onSubmit={handleUpdate}
            onCancel={handleCancel}
            loading={updateMutation.isPending}
            initialData={{
              title: task.title,
              description: task.description || undefined,
            }}
          />
        )}
      </div>
    </AuthGuard>
  );
}