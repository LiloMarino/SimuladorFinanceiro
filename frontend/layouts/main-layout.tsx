import useActivePage from "@/shared/hooks/useActivePage";
import usePageLabel from "@/shared/hooks/usePageLabel";
import Sidebar from "@/layouts/partial/sidebar";
import Topbar from "@/layouts/partial/topbar";
import type { NavItem } from "@/types";
import { Outlet } from "react-router-dom";
import { SidebarInset, SidebarProvider } from "@/shared/components/ui/sidebar";
import { EdgeTab } from "@/features/tutorial/components/edge-tab";

interface LayoutProps {
  navItems: NavItem[];
}

export default function MainLayout({ navItems }: LayoutProps) {
  const activePage = useActivePage();
  const { label: pageLabel } = usePageLabel();

  return (
    <SidebarProvider className="h-svh overflow-hidden" style={{ "--sidebar-width": "14.5rem" } as React.CSSProperties}>
      <Sidebar navItems={navItems} activePage={activePage} />
      <SidebarInset className="overflow-auto">
        <Topbar pageLabel={pageLabel} />
        <main className="mx-auto flex w-full max-w-[1320px] flex-col gap-5 px-7 pt-6 pb-10">
          <Outlet />
        </main>
      </SidebarInset>
      <EdgeTab />
    </SidebarProvider>
  );
}
