"use client";

import { Combobox as ComboboxPrimitive } from "@base-ui/react/combobox";
import { CheckIcon, ChevronDownIcon, SearchIcon } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { cn } from "@/shared/lib/utils";

const Combobox = ComboboxPrimitive.Root;

const ComboboxCollection = ComboboxPrimitive.Collection;

// Gatilho em forma de botão; a busca mora dentro do popup (ComboboxContent com `search`)
function ComboboxTrigger({ className, children, ...props }: ComboboxPrimitive.Trigger.Props) {
  return (
    <ComboboxPrimitive.Trigger
      data-slot="combobox-trigger"
      render={
        <Button variant="field" size="field" className={cn("w-fit min-w-0 aria-expanded:border-primary", className)} />
      }
      {...props}
    >
      {children}
      <ChevronDownIcon
        className="ml-auto size-4 text-muted-foreground transition-colors group-aria-expanded/button:text-primary"
        aria-hidden
      />
    </ComboboxPrimitive.Trigger>
  );
}

function ComboboxContent({
  className,
  children,
  search,
  side = "bottom",
  sideOffset = 4,
  align = "start",
  ...props
}: ComboboxPrimitive.Popup.Props &
  Pick<ComboboxPrimitive.Positioner.Props, "align" | "side" | "sideOffset"> & {
    // Texto de apoio do campo de busca; sem ele o popup não tem busca
    search?: string | undefined;
  }) {
  return (
    <ComboboxPrimitive.Portal>
      <ComboboxPrimitive.Positioner
        side={side}
        sideOffset={sideOffset}
        align={align}
        collisionAvoidance={{ side: "none", align: "shift", fallbackAxisSide: "none" }}
        positionMethod="absolute"
        className="isolate z-50"
      >
        <ComboboxPrimitive.Popup
          data-slot="combobox-content"
          className={cn(
            "relative isolate z-50 flex max-h-[max(14rem,var(--available-height))] w-max max-w-[360px] min-w-(--anchor-width) origin-(--transform-origin) flex-col overflow-hidden rounded-[10px] bg-popover p-1 text-sm outline-none text-popover-foreground shadow-lg ring-1 ring-foreground/10 duration-100 data-[side=bottom]:slide-in-from-top-2 data-[side=top]:slide-in-from-bottom-2 data-open:animate-in data-open:fade-in-0 data-open:zoom-in-95 data-closed:animate-out data-closed:fade-out-0 data-closed:zoom-out-95",
            className,
          )}
          {...props}
        >
          {/* Sem `search` o campo fica fora da tela: ele dá ao popup a navegação por setas e a digitação para pular até a opção */}
          <div
            className={cn(
              search !== undefined
                ? "-mx-1 -mt-1 mb-1 flex h-10 shrink-0 items-center gap-2 border-b px-3 text-muted-foreground"
                : "sr-only",
            )}
          >
            {search !== undefined && <SearchIcon className="size-4 shrink-0" aria-hidden />}
            <ComboboxPrimitive.Input
              data-slot="combobox-search"
              placeholder={search}
              aria-label={search ?? "Opções"}
              className="h-full min-w-0 flex-1 bg-transparent text-sm text-foreground outline-none placeholder:text-muted-foreground"
            />
          </div>
          {children}
        </ComboboxPrimitive.Popup>
      </ComboboxPrimitive.Positioner>
    </ComboboxPrimitive.Portal>
  );
}

function ComboboxList({ className, ...props }: ComboboxPrimitive.List.Props) {
  return (
    <ComboboxPrimitive.List
      data-slot="combobox-list"
      className={cn(
        "-mx-1 min-h-0 flex-1 scroll-py-1 overflow-x-hidden overflow-y-auto overscroll-contain px-1 data-empty:hidden",
        className,
      )}
      {...props}
    />
  );
}

// Linha de pelo menos 48 px. `indicator`: "check" (✓ à direita, escolha única) ou "checkbox" (caixa à esquerda, várias)
function ComboboxItem({
  className,
  children,
  indicator = "check",
  ...props
}: ComboboxPrimitive.Item.Props & { indicator?: "check" | "checkbox" }) {
  return (
    <ComboboxPrimitive.Item
      data-slot="combobox-item"
      className={cn(
        "group/item flex min-h-12 w-full cursor-default items-center gap-2.5 rounded-md px-2.5 py-2 text-sm outline-hidden select-none data-disabled:cursor-not-allowed data-disabled:text-muted-foreground data-highlighted:bg-muted",
        className,
      )}
      {...props}
    >
      {indicator === "checkbox" && (
        <span
          aria-hidden
          className="flex size-4 shrink-0 items-center justify-center rounded-[4px] border border-input bg-card text-primary-foreground group-data-disabled/item:bg-muted group-aria-selected/item:border-primary group-aria-selected/item:bg-primary"
        >
          <CheckIcon className="size-3 stroke-3 opacity-0 group-aria-selected/item:opacity-100" />
        </span>
      )}
      {children}
      {indicator === "check" && (
        <ComboboxPrimitive.ItemIndicator
          render={<span className="flex size-4 shrink-0 items-center justify-center text-primary" />}
        >
          <CheckIcon className="size-4" />
        </ComboboxPrimitive.ItemIndicator>
      )}
    </ComboboxPrimitive.Item>
  );
}

function ComboboxGroup({ className, ...props }: ComboboxPrimitive.Group.Props) {
  return <ComboboxPrimitive.Group data-slot="combobox-group" className={cn(className)} {...props} />;
}

function ComboboxGroupLabel({ className, ...props }: ComboboxPrimitive.GroupLabel.Props) {
  return (
    <ComboboxPrimitive.GroupLabel
      data-slot="combobox-group-label"
      className={cn(
        "px-2.5 pt-2.5 pb-1 text-xs font-semibold tracking-[0.04em] text-muted-foreground uppercase",
        className,
      )}
      {...props}
    />
  );
}

function ComboboxEmpty({ className, ...props }: ComboboxPrimitive.Empty.Props) {
  return (
    <ComboboxPrimitive.Empty
      data-slot="combobox-empty"
      className={cn("px-2.5 py-3 text-center text-sm text-muted-foreground empty:hidden", className)}
      {...props}
    />
  );
}

function ComboboxSeparator({ className, ...props }: ComboboxPrimitive.Separator.Props) {
  return (
    <ComboboxPrimitive.Separator
      data-slot="combobox-separator"
      className={cn("-mx-1 my-1 h-px bg-border", className)}
      {...props}
    />
  );
}

export {
  Combobox,
  ComboboxCollection,
  ComboboxContent,
  ComboboxEmpty,
  ComboboxGroup,
  ComboboxGroupLabel,
  ComboboxItem,
  ComboboxList,
  ComboboxSeparator,
  ComboboxTrigger,
};
