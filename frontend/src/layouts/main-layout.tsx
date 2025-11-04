import useActivePage from "@/hooks/useActivePage";
import usePageLabel from "@/hooks/usePageLabel";
import Sidebar from "@/layouts/partial/sidebar";
import Topbar from "@/layouts/partial/topbar";
import type { NavItem } from "@/types";

interface LayoutProps {
  children: React.ReactNode;
  navItems: NavItem[];
}

export default function MainLayout({ children, navItems }: LayoutProps) {
  const activePage = useActivePage();
  const { label: pageLabel } = usePageLabel();

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
