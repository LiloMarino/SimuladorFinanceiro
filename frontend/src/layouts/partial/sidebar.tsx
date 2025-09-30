import { useState } from "react";
import clsx from "clsx";
import type { NavItem } from "@/types";
import { NavLink } from "react-router-dom";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faBars } from "@fortawesome/free-solid-svg-icons";

interface SidebarProps {
  navItems: NavItem[];
  activePage: string;
}

export default function Sidebar({ navItems, activePage }: SidebarProps) {
  const [open, setOpen] = useState(false);

  return (
    <div
      className={clsx(
        "h-full flex flex-col bg-blue-800 text-white transition-all duration-300",
        open ? "w-64" : "w-16"
      )}
    >
      {/* Cabeçalho */}
      <div
        className={clsx(
          "flex items-center p-4 border-b border-blue-700 transition-all duration-300",
          { "justify-between": open, "justify-center": !open }
        )}
      >
        <span
          className={clsx(
            "text-xl font-bold transition-all duration-300",
            { hidden: !open }
          )}
        >
          FinSim
        </span>
        <button className="focus:outline-none" onClick={() => setOpen(!open)}>
          <FontAwesomeIcon icon={faBars} size="lg" />
        </button>
      </div>

      {/* Navegação */}
      <nav className="mt-4 flex-1 overflow-y-auto">
        <ul>
          {navItems.map((item) => (
            <li key={item.key}>
              <NavLink
                to={item.endpoint}
                className={clsx(
                  "flex items-center p-4 hover:bg-blue-700 transition-all duration-300",
                  { "bg-blue-700": activePage === item.key },
                  { "justify-start": open, "justify-center": !open }
                )}
              >
                <FontAwesomeIcon icon={item.icon} size="lg" className="w-6 flex-shrink-0" />
                {open && <span className="ml-3 whitespace-nowrap">{item.label}</span>}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </div>
  );
}
