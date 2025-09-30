import type { NavItem } from "@/types";
import { NavLink } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faBars } from "@fortawesome/free-solid-svg-icons";

interface SidebarProps {
  navItems: NavItem[];
  activePage: string;
}

export default function Sidebar({ navItems, activePage }: SidebarProps) {
  return (
    <div className="sidebar-transition bg-blue-800 text-white w-64 md:w-20 flex-shrink-0 h-full overflow-y-auto">
      <div className="flex items-center justify-between p-4 border-b border-blue-700">
        <span className="text-xl font-bold whitespace-nowrap md:hidden">FinSim</span>
        <button className="text-white focus:outline-none">
          <FontAwesomeIcon icon={faBars}  />
        </button>
      </div>

      <nav className="mt-4">
        <ul>
          {navItems.map((item) => (
            <li key={item.key}>
              <NavLink
                to={item.endpoint}
                className={`flex items-center p-4 hover:bg-blue-700 ${
                  activePage === item.key ? "active-nav-item" : ""
                }`}
              >
                <FontAwesomeIcon icon={item.icon}  size="lg" />
                <span className="nav-label ml-3 whitespace-nowrap md:hidden">{item.label}</span>
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  );
}
