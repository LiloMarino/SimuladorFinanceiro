import { useRef } from "react";
import type { LucideIcon } from "lucide-react";
import { SidebarMenuBadge, SidebarMenuButton, SidebarMenuItem } from "@/shared/components/ui/sidebar";
import { useTutorial } from "../hooks/useTutorial";
import { TutorialNudge } from "./tutorial-nudge";

interface TutorialMenuItemProps {
  label: string;
  icon: LucideIcon;
}

/** Item "Como jogar" do menu lateral (acesso "Item no menu"): contorno azul e contador enquanto há tópico para ver. */
export function TutorialMenuItem({ label, icon: Icon }: TutorialMenuItemProps) {
  const { state, unseenCount, open } = useTutorial();
  const anchor = useRef<HTMLLIElement>(null);

  if (state.style !== "menu-item") return null;

  return (
    <>
      <SidebarMenuItem ref={anchor}>
        <SidebarMenuButton variant={unseenCount > 0 ? "highlight" : "default"} onClick={() => open()}>
          <Icon />
          <span>{label}</span>
        </SidebarMenuButton>
        {unseenCount > 0 && <SidebarMenuBadge tone="primary">{unseenCount}</SidebarMenuBadge>}
      </SidebarMenuItem>
      <TutorialNudge style="menu-item" anchor={anchor} side="right" />
    </>
  );
}
