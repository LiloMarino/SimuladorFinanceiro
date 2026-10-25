"use client";

import { PreviewCard as PreviewCardPrimitive } from "@base-ui/react/preview-card";
import { cn } from "@/shared/lib/utils";

function HoverCard({ ...props }: PreviewCardPrimitive.Root.Props) {
  return <PreviewCardPrimitive.Root data-slot="hover-card" {...props} />;
}

/** `term`: o nome que abre o cartão, sublinhado em pontilhado; `chip`: selo de cartão com borda, como o do governo na topbar. */
function HoverCardTrigger({
  className,
  term = false,
  chip = false,
  ...props
}: PreviewCardPrimitive.Trigger.Props & { term?: boolean; chip?: boolean }) {
  return (
    <PreviewCardPrimitive.Trigger
      data-slot="hover-card-trigger"
      className={cn(
        term &&
          "max-w-56 cursor-help truncate font-semibold underline decoration-faint-foreground decoration-dotted underline-offset-3 outline-none focus-visible:ring-3 focus-visible:ring-ring/50",
        chip &&
          "flex items-center gap-2 rounded-[10px] border bg-card py-[5px] pr-2.5 pl-1.5 text-left outline-none focus-visible:ring-3 focus-visible:ring-ring/50",
        className,
      )}
      {...props}
    />
  );
}

/** `compact`: cartão mais denso, com menos respiro entre os blocos. */
function HoverCardContent({
  className,
  compact = false,
  align = "start",
  alignOffset = 0,
  side = "bottom",
  sideOffset = 6,
  ...props
}: PreviewCardPrimitive.Popup.Props & { compact?: boolean } &
  Pick<PreviewCardPrimitive.Positioner.Props, "align" | "alignOffset" | "side" | "sideOffset">) {
  return (
    <PreviewCardPrimitive.Portal>
      <PreviewCardPrimitive.Positioner
        align={align}
        alignOffset={alignOffset}
        side={side}
        sideOffset={sideOffset}
        className="isolate z-50"
      >
        <PreviewCardPrimitive.Popup
          data-slot="hover-card-content"
          className={cn(
            "z-50 grid w-85 origin-(--transform-origin) rounded-xl bg-popover text-sm text-popover-foreground shadow-md ring-1 ring-foreground/10 outline-hidden duration-100 data-open:animate-in data-open:fade-in-0 data-open:zoom-in-95 data-closed:animate-out data-closed:fade-out-0 data-closed:zoom-out-95",
            compact ? "gap-2 p-3.5" : "gap-3 p-4",
            className,
          )}
          {...props}
        />
      </PreviewCardPrimitive.Positioner>
    </PreviewCardPrimitive.Portal>
  );
}

export { HoverCard, HoverCardContent, HoverCardTrigger };
