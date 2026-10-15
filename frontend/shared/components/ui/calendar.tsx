import * as React from "react";
import { ChevronLeftIcon, ChevronRightIcon } from "lucide-react";
import { DayPicker, getDefaultClassNames } from "react-day-picker";
import { ptBR } from "react-day-picker/locale";
import { cn } from "@/shared/lib/utils";
import { buttonVariants } from "@/shared/components/ui/variants/buttonVariants";

function Calendar({
  className,
  classNames,
  showOutsideDays = true,
  captionLayout = "label",
  ...props
}: React.ComponentProps<typeof DayPicker>) {
  const defaultClassNames = getDefaultClassNames();

  return (
    <DayPicker
      locale={ptBR}
      showOutsideDays={showOutsideDays}
      captionLayout={captionLayout}
      className={cn("p-1", className)}
      classNames={{
        root: cn("w-fit", defaultClassNames.root),
        months: cn("relative flex flex-col gap-4", defaultClassNames.months),
        month: cn("flex w-full flex-col gap-3", defaultClassNames.month),
        nav: cn("absolute inset-x-0 top-0 flex h-8 items-center justify-between", defaultClassNames.nav),
        button_previous: cn(
          buttonVariants({ variant: "ghost", size: "icon-sm" }),
          "select-none aria-disabled:opacity-50",
          defaultClassNames.button_previous,
        ),
        button_next: cn(
          buttonVariants({ variant: "ghost", size: "icon-sm" }),
          "select-none aria-disabled:opacity-50",
          defaultClassNames.button_next,
        ),
        month_caption: cn("flex h-8 items-center justify-center px-9", defaultClassNames.month_caption),
        dropdowns: cn("flex h-8 items-center justify-center gap-1.5 text-sm font-semibold", defaultClassNames.dropdowns),
        dropdown_root: cn(
          "relative rounded-md border border-input has-focus:border-ring has-focus:ring-3 has-focus:ring-ring/50",
          defaultClassNames.dropdown_root,
        ),
        dropdown: cn("absolute inset-0 cursor-pointer opacity-0", defaultClassNames.dropdown),
        caption_label: cn(
          "text-sm font-semibold select-none",
          captionLayout !== "label" && "flex h-8 items-center gap-1 pr-1 pl-2 text-sm",
          defaultClassNames.caption_label,
        ),
        month_grid: cn("w-full border-collapse", defaultClassNames.month_grid),
        weekdays: cn("flex", defaultClassNames.weekdays),
        weekday: cn(
          "flex-1 text-[0.8rem] font-medium text-muted-foreground select-none",
          defaultClassNames.weekday,
        ),
        week: cn("mt-1 flex w-full", defaultClassNames.week),
        day: cn("group/day relative aspect-square size-9 p-0 text-center select-none", defaultClassNames.day),
        day_button: cn(
          buttonVariants({ variant: "ghost", size: "icon-sm" }),
          "size-9 font-normal group-data-[selected=true]/day:bg-primary group-data-[selected=true]/day:text-primary-foreground group-data-[selected=true]/day:hover:bg-primary-hover",
          defaultClassNames.day_button,
        ),
        today: cn("[&_button]:bg-muted [&_button]:font-semibold", defaultClassNames.today),
        outside: cn("text-muted-foreground aria-selected:text-muted-foreground", defaultClassNames.outside),
        disabled: cn("text-muted-foreground opacity-50", defaultClassNames.disabled),
        hidden: cn("invisible", defaultClassNames.hidden),
        ...classNames,
      }}
      components={{
        Chevron: ({ className: chevronClassName, orientation, ...chevronProps }) => {
          const Icon = orientation === "left" ? ChevronLeftIcon : ChevronRightIcon;
          return <Icon className={cn("size-4", chevronClassName)} {...chevronProps} />;
        },
      }}
      {...props}
    />
  );
}

export { Calendar };
