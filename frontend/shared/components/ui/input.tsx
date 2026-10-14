import * as React from "react";
import { Input as InputPrimitive } from "@base-ui/react/input";
import { cn } from "@/shared/lib/utils";

type InputProps = React.ComponentProps<"input"> & {
  /** Altura: `lg` para o campo principal de uma tela, `xl` para o valor de uma boleta */
  fieldSize?: "default" | "lg" | "xl";
  /** Valores, datas e códigos: fonte mono com algarismos alinhados */
  numeric?: boolean;
};

function Input({ className, type, fieldSize = "default", numeric = false, ...props }: InputProps) {
  return (
    <InputPrimitive
      type={type}
      data-slot="input"
      data-size={fieldSize}
      data-numeric={numeric ? "" : undefined}
      className={cn(
        "h-10 w-full min-w-0 rounded-lg border border-input bg-card px-3 py-1 text-sm transition-colors outline-none file:inline-flex file:h-6 file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-muted-foreground focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50 disabled:pointer-events-none disabled:cursor-not-allowed disabled:bg-input/50 disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-3 aria-invalid:ring-destructive/12 dark:bg-input/30 dark:disabled:bg-input/80 dark:aria-invalid:border-destructive/50 dark:aria-invalid:ring-destructive/40 data-[size=lg]:h-11 data-[size=lg]:text-[15px] data-[size=xl]:h-12 data-[size=xl]:text-lg data-numeric:font-mono data-numeric:tabular-nums",
        className,
      )}
      {...props}
    />
  );
}

export { Input };
