import { EXPANSIONS, type ExpansionKey } from "@/shared/lib/expansions";
import { cn } from "@/shared/lib/utils";

const SIZES = {
  xs: { box: "size-4 rounded-[4px]", icon: "size-2" },
  sm: { box: "size-5 rounded-[5px]", icon: "size-[11px]" },
  md: { box: "size-9 rounded-lg", icon: "size-[19px]" },
  lg: { box: "size-14 rounded-[14px]", icon: "size-[30px]" },
} as const;

type ExpansionEmblemProps = {
  expansion: ExpansionKey;
  size?: keyof typeof SIZES;
  className?: string;
};

/** O emblema da expansão: um quadrado na cor dela com o ícone. */
export function ExpansionEmblem({ expansion, size = "md", className }: ExpansionEmblemProps) {
  const { icon: Icon, emblemClass } = EXPANSIONS[expansion];
  const { box, icon } = SIZES[size];
  return (
    <span
      aria-hidden
      className={cn("inline-flex shrink-0 items-center justify-center text-white", emblemClass, box, className)}
    >
      <Icon className={icon} />
    </span>
  );
}
