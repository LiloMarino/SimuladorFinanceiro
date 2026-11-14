"use client";

import type * as React from "react";
import { Menu as MenuPrimitive } from "@base-ui/react/menu";
import { cn } from "@/shared/lib/utils";
import { badgeVariants } from "./variants/badgeVariants";

function DropdownMenu({ ...props }: MenuPrimitive.Root.Props) {
  return <MenuPrimitive.Root data-slot="dropdown-menu" {...props} />;
}

/** `badge`: o gatilho tem o corpo de um selo, para o selo que abre o menu de troca do valor; `block`: o gatilho é um bloco de linhas de texto (rótulo e valor) que acende ao passar o mouse. */
function DropdownMenuTrigger({
  variant = "default",
  className,
  ...props
}: Omit<MenuPrimitive.Trigger.Props, "className"> & { variant?: "default" | "badge" | "block"; className?: string }) {
  return (
    <MenuPrimitive.Trigger
      data-slot="dropdown-menu-trigger"
      data-variant={variant}
      className={cn(
        variant === "badge" &&
          cn(
            badgeVariants({ variant: "secondary" }),
            "cursor-pointer hover:bg-muted/70 disabled:cursor-default disabled:opacity-60",
          ),
        variant === "block" &&
          "grid cursor-pointer rounded-md px-2 py-1 text-left outline-none hover:bg-subtle focus-visible:ring-2 focus-visible:ring-ring/50 aria-expanded:bg-subtle aria-expanded:ring-1 aria-expanded:ring-border aria-expanded:ring-inset",
        className,
      )}
      {...props}
    />
  );
}

function DropdownMenuContent({
  className,
  align = "end",
  alignOffset = 0,
  side = "bottom",
  sideOffset = 4,
  ...props
}: MenuPrimitive.Popup.Props & Pick<MenuPrimitive.Positioner.Props, "align" | "alignOffset" | "side" | "sideOffset">) {
  return (
    <MenuPrimitive.Portal>
      <MenuPrimitive.Positioner
        align={align}
        alignOffset={alignOffset}
        side={side}
        sideOffset={sideOffset}
        className="isolate z-50"
      >
        <MenuPrimitive.Popup
          data-slot="dropdown-menu-content"
          className={cn(
            "z-50 grid min-w-50 origin-(--transform-origin) rounded-[10px] bg-popover p-1 text-popover-foreground shadow-md ring-1 ring-foreground/10 outline-hidden duration-100 data-open:animate-in data-open:fade-in-0 data-open:zoom-in-95 data-closed:animate-out data-closed:fade-out-0 data-closed:zoom-out-95",
            className,
          )}
          {...props}
        />
      </MenuPrimitive.Positioner>
    </MenuPrimitive.Portal>
  );
}

/** `selected`: o item que está valendo; `fund`: o item valendo quando é a conta de uma gestora; `action`: chamada para outra tela, em destaque; `rich`: item de mais de uma linha (nome e resumo). */
function DropdownMenuItem({
  className,
  variant = "default",
  size = "default",
  ...props
}: MenuPrimitive.Item.Props & {
  variant?: "default" | "destructive" | "selected" | "fund" | "action";
  size?: "default" | "rich";
}) {
  return (
    <MenuPrimitive.Item
      data-slot="dropdown-menu-item"
      data-variant={variant}
      data-size={size}
      className={cn(
        "flex h-8.5 cursor-pointer items-center gap-2 rounded-md px-2.5 text-[13px] outline-hidden select-none data-disabled:pointer-events-none data-disabled:opacity-50 data-highlighted:bg-muted data-[size=rich]:h-auto data-[size=rich]:items-start data-[size=rich]:py-2 data-[variant=destructive]:text-destructive data-[variant=action]:font-medium data-[variant=action]:text-primary data-[variant=selected]:bg-info-soft data-[variant=fund]:bg-fund-soft [&>svg]:size-3.5 [&>svg]:shrink-0",
        className,
      )}
      {...props}
    />
  );
}

/** Título de um grupo de itens do menu. */
function DropdownMenuLabel({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="dropdown-menu-label"
      className={cn("px-2.5 py-1.5 text-xs font-semibold tracking-[.06em] text-sidebar-muted uppercase", className)}
      {...props}
    />
  );
}

function DropdownMenuSeparator({ className, ...props }: MenuPrimitive.Separator.Props) {
  return (
    <MenuPrimitive.Separator
      data-slot="dropdown-menu-separator"
      className={cn("my-1 h-px bg-border", className)}
      {...props}
    />
  );
}

export {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
};
