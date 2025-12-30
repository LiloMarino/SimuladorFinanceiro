import useActivePage from "@/shared/hooks/useActivePage";
import usePageLabel from "@/shared/hooks/usePageLabel";
import Sidebar from "@/layouts/partial/sidebar";
import Topbar from "@/layouts/partial/topbar";
import type { NavItem } from "@/types";
import { Outlet } from "react-router-dom";

interface LayoutProps {
  navItems: NavItem[];
}

export default function MainLayout({ navItems }: LayoutProps) {
  const activePage = useActivePage();
  const { label: pageLabel } = usePageLabel();

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar navItems={navItems} activePage={activePage} />
      <div className="flex-1 overflow-auto">
        <Topbar pageLabel={pageLabel} />
        <main className="p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
