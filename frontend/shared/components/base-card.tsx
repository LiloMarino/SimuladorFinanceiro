import type { ReactNode } from "react";
import { Link } from "react-router-dom";

interface BaseCardProps {
  header: {
    title: string;
    subtitle?: ReactNode;
    badge?: ReactNode;
  };
  fields: {
    label: string;
    value: ReactNode;
  }[];
  footer: {
    linkTo: string;
    label: string;
  };
}

export default function BaseCard({ header, fields, footer }: BaseCardProps) {
  return (
    <div className="bg-card text-card-foreground rounded-xl border shadow-sm overflow-hidden transition-transform hover:-translate-y-0.5 hover:shadow-lg duration-200 flex flex-col">
      <div className="p-4 border-b">
        <div className="flex justify-between items-center">
          <h3 className="font-bold text-lg">{header.title}</h3>
          {header.badge}
        </div>
        {header.subtitle && <p className="text-muted-foreground text-sm mt-0.5">{header.subtitle}</p>}
      </div>

      <div className="p-4 flex-1">
        {fields.map((field, index) => (
          <div key={index} className={`flex justify-between text-sm ${index < fields.length - 1 ? "mb-2" : ""}`}>
            <span className="text-muted-foreground">{field.label}</span>
            <span className="font-medium">{field.value}</span>
          </div>
        ))}
      </div>

      <div className="bg-muted/50 px-4 py-2 flex justify-end mt-auto">
        <Link to={footer.linkTo} className="text-primary text-sm font-medium hover:text-primary/80">
          {footer.label}
        </Link>
      </div>
    </div>
  );
}
