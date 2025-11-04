import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { Card } from "@/components/ui/card";
import type { IconProp } from "@fortawesome/fontawesome-svg-core";
import { formatPrice } from "@/lib/utils/formatting";

interface SummaryCardProps {
  title: string;
  value: number;
  subtitle: string;
  color?: string;
  icon: IconProp;
  iconBg?: string;
}

export function SummaryCard({
  title,
  value,
  subtitle,
  color = "text-gray-600",
  icon,
  iconBg = "bg-gray-100",
}: SummaryCardProps) {
  return (
    <Card key={title} className="p-6">
      <div className="flex justify-between items-center">
        <div>
          <p className="text-gray-600">{title}</p>
          <h3 className="text-2xl font-bold">{formatPrice(value)}</h3>
          <p className={`${color} mt-1`}>{subtitle}</p>
        </div>
        <div className={`${iconBg} w-12 h-12 flex items-center justify-center rounded-full`}>
          <FontAwesomeIcon icon={icon} className={color} />
        </div>
      </div>
    </Card>
  );
}
