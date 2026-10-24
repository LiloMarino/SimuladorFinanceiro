import { cva } from "class-variance-authority";

export const popoverContentVariants = cva("", {
  variants: {
    variant: {
      default: "gap-2.5 p-2.5",
      // Seções de ponta a ponta, com divisórias e rolagem própria
      flush: "gap-0 overflow-y-auto p-0",
    },
  },
  defaultVariants: {
    variant: "default",
  },
});
