import useActivePage from "@/shared/hooks/useActivePage";
import usePageLabel from "@/shared/hooks/usePageLabel";
import Sidebar from "@/layouts/partial/sidebar";
import Topbar from "@/layouts/partial/topbar";
import type { NavItem } from "@/types";
import { Outlet } from "react-router-dom";
import { SidebarInset, SidebarProvider } from "@/shared/components/ui/sidebar";

interface LayoutProps {
  navItems: NavItem[];
}

export default function MainLayout({ navItems }: LayoutProps) {
  const activePage = useActivePage();
  const { label: pageLabel } = usePageLabel();

  return (
    <SidebarProvider className="h-svh overflow-hidden">
      <Sidebar navItems={navItems} activePage={activePage} />
      <SidebarInset className="overflow-auto">
        <Topbar pageLabel={pageLabel} />
        <main className="p-6">
          <Outlet />
        </main>
      </SidebarInset>
    </SidebarProvider>
  );
}
