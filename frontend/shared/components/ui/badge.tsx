import { mergeProps } from "@base-ui/react/merge-props";
import { useRender } from "@base-ui/react/use-render";
import { type VariantProps } from "class-variance-authority";
import { badgeVariants } from "./variants/badgeVariants";
import { cn } from "@/shared/lib/utils";

function Badge({
  className,
  variant = "default",
  size = "default",
  numeric = false,
  render,
  ...props
}: useRender.ComponentProps<"span"> & VariantProps<typeof badgeVariants>) {
  return useRender({
    defaultTagName: "span",
    props: mergeProps<"span">(
      {
        className: cn(badgeVariants({ variant, size, numeric }), className),
      },
      props,
    ),
    render,
    state: {
      slot: "badge",
      variant,
    },
  });
}

export { Badge };
