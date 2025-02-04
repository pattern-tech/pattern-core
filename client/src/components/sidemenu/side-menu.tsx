import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";
import { FolderKanban, PanelsTopLeft, ReceiptText } from "lucide-react";
import { Link } from "react-router-dom";
import logoWhite from "@/assets/logoWhite.svg";
import logoBlack from "@/assets/logoBlack.svg";
import { useTheme } from "../theme-provider";
import { useState } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";

// Menu items.
const items = [
  {
    title: "Projects",
    href: "/projects",
    icon: PanelsTopLeft,
  },
  {
    title: "Billing",
    href: "#",
    icon: ReceiptText,
  },
  {
    title: "Support",
    href: "#",
    icon: FolderKanban,
  },
];

export function SideMenu() {
  const { theme } = useTheme();
  const [isCollapsed, setIsCollapsed] = useState(false);

  const toggleSidebar = () => {
    setIsCollapsed((prev) => !prev);
  };

  return (
    <Sidebar className={isCollapsed ? "w-16" : "w-64"}>
      <img
        src={theme === "light" ? logoBlack : logoWhite}
        alt="Logo"
        className={`w-32 h-auto px-3 pt-4 pb-2 ${isCollapsed ? "hidden" : ""}`}
      />
      <button
        onClick={toggleSidebar}
        className="w-full py-2 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 flex items-center justify-start pl-3"
      >
        {isCollapsed ? <ChevronRight /> : <ChevronLeft />}
      </button>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel className={isCollapsed ? "hidden" : ""}>
            Application
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {items.map((item) => (
                <SidebarMenuItem key={item.title}>
                  <SidebarMenuButton asChild>
                    <Link to={item.href}>
                      <item.icon />
                      <span className={isCollapsed ? "hidden" : ""}>
                        {item.title}
                      </span>
                    </Link>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}
