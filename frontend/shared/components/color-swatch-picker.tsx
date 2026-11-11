import type { KeyboardEvent } from "react";
import { Check } from "lucide-react";
import { cn } from "@/shared/lib/utils";

type Swatch = { value: string; name: string; background: string; foreground: string };

/** Quem já usa uma cor: a sigla aparece sobre a amostra e o nome na dica. */
type SwatchOwner = { color: string; label: string; owner: string };

type ColorSwatchPickerProps = {
  colors: readonly Swatch[];
  /** Cores que outros já usam: ficam esmaecidas e não podem ser escolhidas */
  taken: SwatchOwner[];
  value: string | undefined;
  onChange: (value: string) => void;
  /** Amostras por linha */
  columns: number;
  /** Nome do grupo para leitor de tela */
  label: string;
  disabled?: boolean;
};

const sameColor = (a: string, b: string) => a.toUpperCase() === b.toUpperCase();

/** Grade de amostras de cor: uma escolha só, com o nome da cor selecionada embaixo. */
export function ColorSwatchPicker({
  colors,
  taken,
  value,
  onChange,
  columns,
  label,
  disabled,
}: ColorSwatchPickerProps) {
  const ownerOf = (color: string) => taken.find((t) => sameColor(t.color, color));
  const isSelected = (color: string) => value !== undefined && sameColor(color, value);
  const isBlocked = (color: string) => disabled || (ownerOf(color) !== undefined && !isSelected(color));

  // Uma parada só de Tab: a cor selecionada ou, sem ela, a primeira livre
  const tabStop = (
    colors.find((c) => isSelected(c.value) && !isBlocked(c.value)) ?? colors.find((c) => !isBlocked(c.value))
  )?.value;
  const selected = colors.find((c) => isSelected(c.value));

  // As setas, Home e End movem o foco entre as amostras livres; Enter e Espaço escolhem
  const moveFocus = (event: KeyboardEvent<HTMLButtonElement>) => {
    const keys = ["ArrowRight", "ArrowDown", "ArrowLeft", "ArrowUp", "Home", "End"];
    if (!keys.includes(event.key)) return;
    const group = event.currentTarget.closest('[role="radiogroup"]');
    const radios = Array.from(group?.querySelectorAll<HTMLButtonElement>('[role="radio"]:not(:disabled)') ?? []);
    if (radios.length === 0) return;
    event.preventDefault();
    const current = radios.indexOf(document.activeElement as HTMLButtonElement);
    const forward = event.key === "ArrowRight" || event.key === "ArrowDown";
    const target =
      event.key === "Home"
        ? 0
        : event.key === "End"
          ? radios.length - 1
          : (current + (forward ? 1 : -1) + radios.length) % radios.length;
    radios[target]?.focus();
  };

  return (
    <div className="grid gap-2">
      <div
        role="radiogroup"
        aria-label={label}
        className="grid gap-x-1.5 gap-y-2"
        style={{ gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))` }}
      >
        {colors.map((color) => {
          const owner = ownerOf(color.value);
          const selectedHere = isSelected(color.value);
          const used = owner !== undefined && !selectedHere;
          const description = used ? `${color.name}, de ${owner.owner}` : color.name;
          return (
            <button
              key={color.value}
              type="button"
              role="radio"
              aria-checked={selectedHere}
              aria-label={description}
              title={description}
              tabIndex={color.value === tabStop ? 0 : -1}
              disabled={isBlocked(color.value)}
              onClick={() => onChange(color.value)}
              onKeyDown={moveFocus}
              className={cn(
                "grid size-9 cursor-pointer place-content-center justify-self-center rounded-[10px] text-xs font-semibold outline-none focus-visible:ring-3 focus-visible:ring-ring/50 disabled:cursor-default",
                used && "opacity-45",
                selectedHere && "ring-2 ring-foreground ring-offset-2 ring-offset-card",
              )}
              style={{ backgroundColor: color.background, color: color.foreground }}
            >
              {used && owner.label}
              {selectedHere && <Check className="size-4.5" />}
            </button>
          );
        })}
      </div>
      {selected && (
        <p className="text-xs text-muted-foreground">
          Cor escolhida: <span className="font-semibold text-foreground">{selected.name}</span>
        </p>
      )}
    </div>
  );
}
