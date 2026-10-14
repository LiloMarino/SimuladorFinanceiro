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

interface SidebarProps {
  navItems: NavItem[];
  activePage: string;
}

export default function Sidebar({ navItems, activePage }: SidebarProps) {
  return (
    <SidebarRoot collapsible="icon">
      <SidebarHeader className="flex-row items-center justify-between">
        <span className="text-xl font-bold whitespace-nowrap group-data-[collapsible=icon]:hidden">FinSim</span>
        <SidebarTrigger />
      </SidebarHeader>

      <SidebarMenu className="px-2">
        {navItems.map((item) => (
          <SidebarMenuItem key={item.key}>
            <SidebarMenuButton
              isActive={activePage === item.key}
              tooltip={item.label}
              render={<NavLink to={item.endpoint} />}
            >
              <item.icon />
              <span>{item.label}</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        ))}
      </SidebarMenu>
    </SidebarRoot>
  );
}
