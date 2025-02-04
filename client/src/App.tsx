import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { ThemeProvider } from "@/components/theme-provider";
import { DashboardLayout } from "@/layouts/dashboard-layout";
import { ProjectsPage } from "@/pages/projects";
import { ProjectDetailsPage } from "@/pages/project-details";
import { ManageKeysPage } from "@/pages/manage-keys";
import { PlaygroundPage } from "@/pages/playground";
import { RegisterPage } from "./pages/register";
import { LoginPage } from "./pages/login";
import { ProjectTools } from "./pages/project-tools";
import { HeaderProvider } from "@/contexts/header-context";

function App() {
  return (
    <ThemeProvider defaultTheme="system" storageKey="vite-ui-theme">
      <HeaderProvider>
        <BrowserRouter>
          <Routes>
            <Route path="register" element={<RegisterPage />} />
            <Route path="login" element={<LoginPage />} />
            <Route path="/" element={<DashboardLayout />}>
              <Route index element={<Navigate to="/projects" replace />} />
              <Route path="projects" element={<ProjectsPage />} />
              <Route path="projects/:id" element={<ProjectDetailsPage />} />
              <Route
                path="projects/:projectId/tools"
                element={<ProjectTools />}
              />
              <Route
                path="projects/:projectId/playground"
                element={<PlaygroundPage />}
              />
              <Route path="manage-keys" element={<ManageKeysPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </HeaderProvider>
    </ThemeProvider>
  );
}

export default App;
