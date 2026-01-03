import { cn } from "@/shared/lib/utils";
import type { ReactNode } from "react";

type SettingsSectionProps = {
  title: string;
  children: ReactNode;
  bordered?: boolean;
  className?: string;
};

export function SettingsSection({ title, children, bordered = false, className }: SettingsSectionProps) {
  return (
    <section className={cn("space-y-4", bordered && "pt-6 border-t", className)}>
      <h2 className="text-lg font-semibold">{title}</h2>
      {children}
    </section>
  );
}
