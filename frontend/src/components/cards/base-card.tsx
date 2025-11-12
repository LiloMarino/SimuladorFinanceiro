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
    <div className="bg-white rounded-lg shadow-md overflow-hidden transition-transform transform hover:-translate-y-0.5 hover:shadow-lg transition-all duration-200">
      {/* Header */}
      <div className="p-4 border-b">
        <div className="flex justify-between items-center">
          <h3 className="font-bold text-lg">{header.title}</h3>
          {header.badge && header.badge}
        </div>
        {header.subtitle && <p className="text-gray-500 text-sm">{header.subtitle}</p>}
      </div>

      {/* Body */}
      <div className="p-4">
        {fields.map((field, index) => (
          <div key={index} className={`flex justify-between text-sm ${index < fields.length - 1 ? "mb-2" : ""}`}>
            <span className="text-gray-500">{field.label}</span>
            <span className="font-medium">{field.value}</span>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="bg-gray-50 px-4 py-2 flex justify-end">
        <Link to={footer.linkTo} className="text-blue-600 text-sm font-medium hover:text-blue-800">
          {footer.label}
        </Link>
      </div>
    </div>
  );
}
