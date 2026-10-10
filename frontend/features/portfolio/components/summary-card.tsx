import type { ReactNode } from "react";
import type { LucideIcon } from "lucide-react";
import { Card } from "@/shared/components/ui/card";
import { InfoHint } from "@/shared/components/info-hint";
import { cn } from "@/shared/lib/utils";
import { displayMoneyCompact } from "@/shared/lib/utils/display";

interface SummaryCardProps {
  title: string;
  value: string;
  subtitle: string;
  color?: string;
  icon: LucideIcon;
  iconBg?: string;
  hint?: ReactNode;
}

export function SummaryCard({
  title,
  value,
  subtitle,
  color = "text-gray-600",
  icon: Icon,
  iconBg = "bg-gray-100",
  hint,
}: SummaryCardProps) {
  return (
    <Card className="p-6">
      <div className="flex justify-between items-center gap-4">
        {/* Texto */}
        <div className="min-w-0">
          <div className="flex items-center gap-1.5">
            <p className="text-gray-600">{title}</p>
            {hint && <InfoHint>{hint}</InfoHint>}
          </div>
          <h3 className="text-2xl font-bold">{displayMoneyCompact(value)}</h3>
          <p className={`${color} mt-1`}>{subtitle}</p>
        </div>

        {/* Ícone */}
        <div className={`${iconBg} w-12 h-12 flex items-center justify-center rounded-full flex-shrink-0`}>
          <Icon className={cn("w-5 h-5", color)} />
        </div>
      </div>
    </Card>
  );
}
