import { Header } from "@/components/dashboard/header";
import { SidebarProvider } from "@/components/ui/sidebar";
import { Outlet } from "react-router-dom";
import { HeaderProvider } from "@/contexts/header-context";

export function DashboardLayout() {
  return (
    <HeaderProvider>
      <div className="min-h-screen w-full">
        <SidebarProvider>
          <div className="flex w-full">
            <div className="w-full">
              <Header />
              <main className="p-8 overflow-auto">
                <Outlet />
              </main>
            </div>
          </div>
        </SidebarProvider>
      </div>
    </HeaderProvider>
  );
}
