import { cva } from "class-variance-authority";

export const alertVariants = cva(
  "group/alert relative grid w-full gap-0.5 rounded-[10px] border px-3.5 py-2.5 text-left text-sm has-data-[slot=alert-action]:relative has-data-[slot=alert-action]:pr-18 has-[>svg]:grid-cols-[auto_1fr] has-[>svg]:gap-x-2 *:[svg]:row-span-2 *:[svg]:translate-y-0.5 *:[svg]:text-current *:[svg:not([class*='size-'])]:size-4",
  {
    variants: {
      variant: {
        default: "bg-card text-card-foreground",
        muted: "border-transparent bg-subtle text-foreground",
        info: "border-info-border bg-info-soft text-foreground *:[svg]:text-primary",
        success: "border-transparent bg-success-soft text-foreground *:[svg]:text-success",
        warning: "border-transparent bg-warning-soft text-foreground *:[svg]:text-warning *:data-[slot=alert-description]:text-foreground",
        destructive:
          "border-transparent bg-destructive-soft text-foreground *:data-[slot=alert-title]:text-destructive *:[svg]:text-destructive",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);
