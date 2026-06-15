import type { LucideIcon } from "lucide-react";
import { Card } from "@/shared/components/ui/card";
import { cn } from "@/shared/lib/utils";
import { displayMoneyCompact } from "@/shared/lib/utils/display";

interface SummaryCardProps {
  title: string;
  value: number;
  subtitle: string;
  color?: string;
  icon: LucideIcon;
  iconBg?: string;
}

export function SummaryCard({
  title,
  value,
  subtitle,
  color = "text-gray-600",
  icon: Icon,
  iconBg = "bg-gray-100",
}: SummaryCardProps) {
  return (
    <Card className="p-6">
      <div className="flex justify-between items-center gap-4">
        {/* Texto */}
        <div className="min-w-0">
          <p className="text-gray-600">{title}</p>
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
