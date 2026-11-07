import { X } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { cn } from "@/shared/lib/utils";
import { Swatch } from "../indicator-selector";

interface LegendItemProps {
  token: string;
  name: string;
  value: string;
  onRemove?: () => void;
}

export function LegendItem({ token, name, value, onRemove }: LegendItemProps) {
  const missing = value.startsWith("aparece");
  return (
    <span
      className={cn(
        "group inline-flex h-6.5 items-center gap-1.5 rounded-md bg-subtle px-2 text-xs",
        onRemove && "hover:bg-card hover:ring-1 hover:ring-input hover:ring-inset",
      )}
    >
      <Swatch token={token} shape="line" />
      <span className="font-medium">{name}</span>
      <span
        className={cn("font-mono tabular-nums", missing && "font-sans text-muted-foreground")}
        style={missing ? undefined : { color: `var(${token})` }}
      >
        {value}
      </span>
      {onRemove && (
        <Button
          variant="ghost"
          size="icon-xs"
          className="hidden group-focus-within:inline-flex group-hover:inline-flex"
          aria-label={`Desligar ${name}`}
          onClick={onRemove}
        >
          <X />
        </Button>
      )}
    </span>
  );
}
