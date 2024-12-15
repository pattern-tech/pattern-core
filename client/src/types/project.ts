export interface Project {
  id: string;
  name: string;
  description: string;
  apiKeys: number;
  lastActive: string;
  created: string;
  status: "active" | "archived";
}
