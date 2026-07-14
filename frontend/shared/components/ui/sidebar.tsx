import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { Menu } from "lucide-react";
import { cn } from "@/shared/lib/utils";
import { Button } from "@/shared/components/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/shared/components/ui/tooltip";
import { SidebarContext } from "./context/SidebarContext";
import { useSidebar } from "./hooks/useSidebar";

export function SidebarProvider({
  children,
  defaultOpen = false,
}: {
  children: React.ReactNode;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = React.useState(defaultOpen);
  const toggle = React.useCallback(() => setOpen((o) => !o), []);
  const value = React.useMemo(() => ({ open, toggle }), [open, toggle]);

  return <SidebarContext.Provider value={value}>{children}</SidebarContext.Provider>;
}

export function Sidebar({ className, children, ...props }: React.ComponentProps<"div">) {
  const { open } = useSidebar();

  return (
    <div
      data-slot="sidebar"
      data-state={open ? "expanded" : "collapsed"}
      className={cn(
        "h-full flex flex-col bg-sidebar text-sidebar-foreground transition-all duration-300",
        open ? "w-64" : "w-16",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export function SidebarHeader({ className, children, ...props }: React.ComponentProps<"div">) {
  const { open } = useSidebar();

  return (
    <div
      data-slot="sidebar-header"
      className={cn(
        "flex items-center p-4 border-b border-sidebar-border transition-all duration-300",
        open ? "justify-between" : "justify-center",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}

export function SidebarTrigger({ className, ...props }: React.ComponentProps<typeof Button>) {
  const { toggle } = useSidebar();

  return (
    <Button
      data-slot="sidebar-trigger"
      type="button"
      variant="ghost"
      size="icon"
      className={cn(
        "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
        className
      )}
      onClick={toggle}
      aria-label="Abrir ou fechar menu"
      {...props}
    >
      <Menu />
    </Button>
  );
}

export function SidebarMenu({ className, children, ...props }: React.ComponentProps<"ul">) {
  return (
    <ul data-slot="sidebar-menu" className={cn("mt-4 flex-1 overflow-y-auto", className)} {...props}>
      {children}
    </ul>
  );
}

export function SidebarMenuItem({ className, children, ...props }: React.ComponentProps<"li">) {
  return (
    <li data-slot="sidebar-menu-item" className={className} {...props}>
      {children}
    </li>
  );
}

interface SidebarMenuButtonProps extends React.ComponentProps<"a"> {
  asChild?: boolean;
  isActive?: boolean;
  /** Texto exibido em tooltip quando a sidebar está colapsada. */
  tooltip: string;
}

export function SidebarMenuButton({
  asChild,
  isActive,
  tooltip,
  className,
  children,
  ...props
}: SidebarMenuButtonProps) {
  const { open } = useSidebar();
  const Comp = asChild ? Slot : "a";

  const content = (
    <Comp
      data-slot="sidebar-menu-button"
      data-active={isActive}
      className={cn(
        "flex items-center gap-3 p-4 transition-all duration-300",
        "hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sidebar-ring",
        isActive && "bg-sidebar-accent text-sidebar-accent-foreground",
        open ? "justify-start" : "justify-center",
        className
      )}
      {...props}
    >
      {children}
    </Comp>
  );

  if (open) {
    return content;
  }

  return (
    <Tooltip>
      <TooltipTrigger asChild>{content}</TooltipTrigger>
      <TooltipContent side="right">{tooltip}</TooltipContent>
    </Tooltip>
  );
}
