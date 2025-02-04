import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useHeader } from "@/contexts/header-context";
import { fetchClient } from "@/utils/fetchClient";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface Project {
  id: string;
  workspace_id: string;
  name: string;
  deleted_at: string | null;
  user_id: string;
  created_at: string;
  updated_at: string;
}

export function ProjectDetailsPage() {
  const navigate = useNavigate();
  const { id } = useParams();
  const { setHeaderTitle } = useHeader();
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (id) {
      const fetchProject = async () => {
        try {
          const response = await fetchClient(`/project/${id}`);
          setProject(response.data);
          setHeaderTitle(response.data.name);
        } catch (error) {
          console.error(error);
        } finally {
          setLoading(false);
        }
      };

      fetchProject();
    }
  }, [id, setHeaderTitle]);

  if (loading) return <div>Loading...</div>;
  if (!project) return <div>Project not found</div>;

  const handleTabChange = (value: string) => {
    if (value === "playground") {
      navigate(`/projects/${id}/playground`);
    } else if (value === "settings") {
      navigate(`/projects/${id}/tools`);
    }
  };

  return (
    <div className="space-y-6">
      <Tabs
        defaultValue="overview"
        className="space-y-4"
        onValueChange={handleTabChange}
      >
        <TabsList>
          <TabsTrigger value="playground">Playground</TabsTrigger>
          <TabsTrigger value="settings">Tools</TabsTrigger>
        </TabsList>
      </Tabs>
    </div >
  );
}
