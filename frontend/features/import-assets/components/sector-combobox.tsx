import { useState } from "react";
import { ChevronsUpDown, Plus } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/shared/components/ui/command";
import { Popover, PopoverContent, PopoverTrigger } from "@/shared/components/ui/popover";

type SectorComboboxProps = {
  id: string;
  /** Setores que já existem na base */
  sectors: string[];
  value: string;
  onChange: (sector: string) => void;
};

/** Setor com busca entre os existentes e, no fim, a opção de criar um com o que foi digitado. */
export function SectorCombobox({ id, sectors, value, onChange }: SectorComboboxProps) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");

  const typed = search.trim();
  const canCreate = typed !== "" && !sectors.some((name) => name.toLowerCase() === typed.toLowerCase());

  const choose = (sector: string) => {
    onChange(sector);
    setOpen(false);
    setSearch("");
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger
        render={
          <Button id={id} type="button" variant="outline" role="combobox" aria-expanded={open} className="justify-between" />
        }
      >
        <span className={value ? "truncate font-normal" : "truncate font-normal text-muted-foreground"}>
          {value || "Escolha ou crie um setor"}
        </span>
        <ChevronsUpDown className="text-faint-foreground" />
      </PopoverTrigger>
      <PopoverContent align="start" className="w-72">
        <Command>
          <CommandInput value={search} onValueChange={setSearch} placeholder="Buscar setor" />
          <CommandList>
            <CommandEmpty>Nenhum setor com esse nome.</CommandEmpty>
            <CommandGroup>
              {sectors.map((name) => (
                <CommandItem key={name} value={name} selected={name === value} onSelect={() => choose(name)}>
                  {name}
                </CommandItem>
              ))}
              {canCreate && (
                <CommandItem forceMount value={`__create__${typed}`} onSelect={() => choose(typed)}>
                  <Plus className="text-primary" />
                  <span className="text-primary">Criar setor “{typed}”</span>
                </CommandItem>
              )}
            </CommandGroup>
          </CommandList>
        </Command>
      </PopoverContent>
    </Popover>
  );
}
