import { NavLink } from "react-router-dom";
import type { NavItem } from "@/types";
import {
  Sidebar as SidebarRoot,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarTrigger,
} from "@/shared/components/ui/sidebar";
import { useSidebar } from "@/shared/components/ui/hooks/useSidebar";

interface SidebarProps {
  navItems: NavItem[];
  activePage: string;
}

export default function Sidebar({ navItems, activePage }: SidebarProps) {
  const { open } = useSidebar();

  return (
    <SidebarRoot>
      <SidebarHeader>
        {open && <span className="text-xl font-bold whitespace-nowrap">FinSim</span>}
        <SidebarTrigger />
      </SidebarHeader>

      <SidebarMenu>
        {navItems.map((item) => (
          <SidebarMenuItem key={item.key}>
            <SidebarMenuButton asChild isActive={activePage === item.key} tooltip={item.label}>
              <NavLink to={item.endpoint}>
                <item.icon className="w-5 h-5 flex-shrink-0" />
                {open && <span className="ml-3 whitespace-nowrap">{item.label}</span>}
              </NavLink>
            </SidebarMenuButton>
          </SidebarMenuItem>
        ))}
      </SidebarMenu>
    </SidebarRoot>
  );
}
