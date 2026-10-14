"use client";

import * as React from "react";
import { cn } from "@/shared/lib/utils";

function Table({ className, ...props }: React.ComponentProps<"table">) {
  return (
    <div data-slot="table-container" className="relative w-full overflow-x-auto">
      <table data-slot="table" className={cn("w-full caption-bottom text-sm", className)} {...props} />
    </div>
  );
}

function TableHeader({ className, ...props }: React.ComponentProps<"thead">) {
  return (
    <thead data-slot="table-header" className={cn("[&_tr]:border-b [&_tr]:border-border", className)} {...props} />
  );
}

function TableBody({ className, ...props }: React.ComponentProps<"tbody">) {
  return <tbody data-slot="table-body" className={cn("[&_tr:last-child]:border-0", className)} {...props} />;
}

function TableFooter({ className, ...props }: React.ComponentProps<"tfoot">) {
  return (
    <tfoot
      data-slot="table-footer"
      className={cn("border-t bg-muted/50 font-medium [&>tr]:last:border-b-0", className)}
      {...props}
    />
  );
}

/**
 * `group`: linha de título de um grupo de linhas; `warning`: linha que pede atenção;
 * `editing`: linha aberta para edição logo abaixo de outra; `current`: a linha de quem está vendo.
 */
function TableRow({
  className,
  variant = "default",
  ...props
}: React.ComponentProps<"tr"> & { variant?: "default" | "group" | "warning" | "editing" | "current" }) {
  return (
    <tr
      data-slot="table-row"
      data-variant={variant}
      className={cn(
        "border-b border-muted transition-colors hover:bg-subtle has-aria-expanded:bg-muted/50 data-[state=selected]:bg-muted data-[variant=current]:bg-info-soft/40 data-[variant=current]:font-semibold data-[variant=editing]:bg-info-soft/50 data-[variant=group]:bg-subtle data-[variant=warning]:bg-warning-soft/40 data-[variant=editing]:hover:bg-info-soft/50 data-[variant=warning]:hover:bg-warning-soft/60",
        className,
      )}
      {...props}
    />
  );
}

/** `numeric`: coluna de valores, alinhada à direita. */
function TableHead({ className, numeric = false, ...props }: React.ComponentProps<"th"> & { numeric?: boolean }) {
  return (
    <th
      data-slot="table-head"
      data-numeric={numeric ? "" : undefined}
      className={cn(
        "h-10 bg-subtle px-4 text-left align-middle text-xs font-medium whitespace-nowrap text-muted-foreground data-numeric:text-right [&:has([role=checkbox])]:pr-0",
        className,
      )}
      {...props}
    />
  );
}

/** `numeric`: valor alinhado à direita, em mono com algarismos alinhados. */
function TableCell({ className, numeric = false, ...props }: React.ComponentProps<"td"> & { numeric?: boolean }) {
  return (
    <td
      data-slot="table-cell"
      data-numeric={numeric ? "" : undefined}
      className={cn(
        "px-4 py-3 align-middle whitespace-nowrap data-numeric:text-right data-numeric:font-mono data-numeric:tabular-nums [&:has([role=checkbox])]:pr-0",
        className,
      )}
      {...props}
    />
  );
}

function TableCaption({ className, ...props }: React.ComponentProps<"caption">) {
  return (
    <caption data-slot="table-caption" className={cn("mt-4 text-sm text-muted-foreground", className)} {...props} />
  );
}

export { Table, TableHeader, TableBody, TableFooter, TableHead, TableRow, TableCell, TableCaption };
