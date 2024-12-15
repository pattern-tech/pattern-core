import { useEffect, useState } from "react";
import { fetchClient } from "@/utils/fetchClient";
import { ProjectCard } from "@/components/projects/project-card";
import { Project } from "@/types/project";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { Modal } from "@/components/ui/modal";
import { Input } from "@/components/ui/input";
import { useForm, SubmitHandler } from "react-hook-form";

type CreateProjectFormInputs = {
  name: string;
};

export function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [workspaceId, setWorkspaceId] = useState<string>("");

  const { register, handleSubmit, reset } = useForm<CreateProjectFormInputs>();

  useEffect(() => {
    async function fetchProjects() {
      try {
        // Fetch workspaces
        const workspaces = await fetchClient("/workspace");
        const defaultWorkspace = workspaces.data[0];
        setWorkspaceId(defaultWorkspace.id);

        // Fetch projects for the default workspace
        const projectsData = await fetchClient(
          `/workspace/${defaultWorkspace.id}`
        );
        setProjects(projectsData.data.projects || []);
      } catch (error) {
        console.error("Failed to load projects:", error);
      } finally {
        setLoading(false);
      }
    }

    fetchProjects();
  }, []);

  const createProject: SubmitHandler<CreateProjectFormInputs> = async (data) => {
    try {
      const response = await fetchClient("/project", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: "Bearer your-jwt-token",
        },
        body: JSON.stringify({
          name: data.name,
          workspace_id: workspaceId,
        }),
      });
      setProjects((prev) => [...prev, response.data]);
      reset();
      setIsModalOpen(false);
    } catch (error) {
      console.error("Failed to create project:", error);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Projects</h1>
          <p className="text-muted-foreground">
            Manage your API projects and keys
          </p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          New Project
        </Button>
      </div>

      {loading ? (
        <p>Loading...</p>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {projects.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      )}

      {/* Modal for creating a project */}
      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}>
        <h2 className="text-xl font-bold mb-4">Create New Project</h2>
        <form onSubmit={handleSubmit(createProject)}>
          <div className="space-y-4">
            <Input
              type="text"
              placeholder="Project Name"
              {...register("name", { required: true })}
            />
            <Button type="submit">Create</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
