import Sidebar from "@/layouts/partial/sidebar";
import Topbar from "@/layouts/partial/topbar";
import type { NavItem } from "@/types";
import useActivePage from "@/hooks/useActivePage";

interface LayoutProps {
  children: React.ReactNode;
  navItems: NavItem[];
}

export default function MainLayout({ children, navItems }: LayoutProps) {
  const activePage = useActivePage();
  const pageLabel = navItems.find((item) => item.key === activePage)?.label || "Example";

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar navItems={navItems} activePage={activePage} />
      <div className="flex-1 overflow-auto">
        <Topbar pageLabel={pageLabel} />
        <main className="p-6">{children}</main>
      </div>
    </div>
  );
}
