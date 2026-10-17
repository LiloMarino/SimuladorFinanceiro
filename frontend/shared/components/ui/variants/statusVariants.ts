import { cva } from "class-variance-authority";

export const statusVariants = cva("inline-flex items-center gap-1.5 text-xs font-medium", {
  variants: {
    status: {
      online: "text-success",
      offline: "text-faint-foreground",
    },
  },
  defaultVariants: {
    status: "offline",
  },
});

export const statusDotVariants = cva("relative inline-flex size-2 rounded-full", {
  variants: {
    status: {
      online: "bg-success",
      offline: "bg-faint-foreground/50",
    },
  },
  defaultVariants: {
    status: "offline",
  },
});
