import { useState } from "react";
import { Search } from "lucide-react";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Checkbox } from "@/shared/components/ui/checkbox";
import { InputGroup, InputGroupAddon, InputGroupInput } from "@/shared/components/ui/input-group";
import type { CorrelationAssets } from "@/types";
import { MAX_TICKERS, bySector, oneOfEachSector } from "../lib/assets";

interface AssetPickerProps {
  assets: CorrelationAssets["assets"];
  held: string[];
  selected: string[];
  onToggle: (ticker: string) => void;
  onReplace: (tickers: string[]) => void;
}

/** Os ativos com preço agrupados por setor, com atalhos para a carteira e para um de cada setor. */
export function AssetPicker({ assets, held, selected, onToggle, onReplace }: AssetPickerProps) {
  const [search, setSearch] = useState("");
  const term = search.trim().toUpperCase();
  const groups = bySector(assets.filter((a) => a.ticker.includes(term)));
  const full = selected.length >= MAX_TICKERS;

  return (
    <Card size="sm">
      <CardHeader>
        <CardTitle>Ativos</CardTitle>
        <CardDescription>
          {selected.length} de {MAX_TICKERS}
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-2.5">
          <InputGroup>
            <InputGroupAddon>
              <Search />
            </InputGroupAddon>
            <InputGroupInput value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Buscar ticker" />
          </InputGroup>

          {/* Atalhos: sempre à vista, desabilitados quando não se aplicam */}
          <div className="flex flex-wrap gap-1.5">
            <Button
              variant="info"
              size="xs"
              disabled={held.length === 0}
              onClick={() => onReplace(held.slice(0, MAX_TICKERS))}
            >
              Minha carteira · {held.length}
            </Button>
            <Button variant="secondary" size="xs" onClick={() => onReplace(oneOfEachSector(assets))}>
              Um de cada setor
            </Button>
            <Button variant="secondary" size="xs" disabled={selected.length === 0} onClick={() => onReplace([])}>
              Limpar
            </Button>
          </div>

          {/* Ativos por setor */}
          {groups.length === 0 ? (
            <p className="py-3 text-center text-[13px] text-muted-foreground">Nenhum ticker com “{search.trim()}”.</p>
          ) : (
            <div className="grid max-h-[560px] gap-0.5 overflow-y-auto">
              {groups.map(([sector, items]) => (
                <div key={sector} className="grid">
                  <span className="px-1 pt-2.5 pb-1 text-[11px] font-semibold tracking-[0.06em] text-faint-foreground uppercase">
                    {sector}
                  </span>
                  {items.map((a) => {
                    const checked = selected.includes(a.ticker);
                    return (
                      <label
                        key={a.ticker}
                        className="flex cursor-pointer items-center gap-2.5 rounded-md px-1 py-1.5 hover:bg-subtle"
                      >
                        <Checkbox
                          checked={checked}
                          disabled={!checked && full}
                          onCheckedChange={() => onToggle(a.ticker)}
                        />
                        <span className="font-mono text-[13px] font-medium">{a.ticker}</span>
                        {held.includes(a.ticker) && (
                          <Badge variant="info" size="sm">
                            na carteira
                          </Badge>
                        )}
                      </label>
                    );
                  })}
                </div>
              ))}
            </div>
          )}
          {full && <p className="text-xs text-faint-foreground">Até {MAX_TICKERS} ativos por vez.</p>}
        </div>
      </CardContent>
    </Card>
  );
}
