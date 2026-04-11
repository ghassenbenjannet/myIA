import { createBrowserRouter, Navigate, Outlet, RouterProvider } from "react-router-dom";

import { AppShell } from "@/components/layout/app-shell";
import { ArtifactViewPage } from "@/pages/artifact-view-page";
import { DashboardPage } from "@/pages/dashboard-page";
import { LookupPage } from "@/pages/lookup-page";
import { ReadsPage } from "@/pages/reads-page";
import { TopicWorkspacePage } from "@/pages/topic-workspace-page";
import { TopicsPage } from "@/pages/topics-page";
import { WorkspacePage } from "@/pages/workspace-page";

function RootLayout() {
  return (
    <AppShell>
      <Outlet />
    </AppShell>
  );
}

const router = createBrowserRouter([
  {
    path: "/",
    element: <RootLayout />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: "workspace", element: <WorkspacePage /> },
      { path: "topics", element: <TopicsPage /> },
      { path: "topics/:topicId", element: <TopicWorkspacePage /> },
      { path: "artifacts/:runId", element: <ArtifactViewPage /> },
      { path: "reads", element: <ReadsPage /> },
      { path: "lookup", element: <LookupPage /> },
      { path: "*", element: <Navigate to="/" replace /> },
    ],
  },
]);

export function AppRouter() {
  return <RouterProvider router={router} />;
}
