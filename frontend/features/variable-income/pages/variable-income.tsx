import { useState } from "react";
import { Search } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardHeader } from "@/shared/components/ui/card";
import { Empty, EmptyContent, EmptyDescription, EmptyHeader, EmptyTitle } from "@/shared/components/ui/empty";
import { InputGroup, InputGroupAddon, InputGroupInput } from "@/shared/components/ui/input-group";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/shared/components/ui/select";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { ErrorState } from "@/shared/components/error-state";
import { usePortfolio } from "@/shared/hooks/queries/usePortfolio";
import { useVariableIncomeStocks } from "@/shared/hooks/queries/useVariableIncomeStocks";
import { MarketTable } from "../components/market-table";
import type { AssetClass } from "@/types";

type Filter = "ALL" | "HELD" | AssetClass;
// Um botão por classe da API: classe nova sem rótulo não compila
const CLASS_FILTER_LABELS: Record<AssetClass, string> = {
  STOCK: "Ações",
  FII: "FII",
  ETF: "ETF",
  BDR: "BDR",
  CRYPTO: "Cripto",
};
const ALL_SECTORS = "__all__";
const NO_SECTOR = "__none__";

export default function VariableIncomePage() {
  const { data: quotes, isLoading, error, refetch } = useVariableIncomeStocks();
  const { data: portfolio } = usePortfolio();
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<Filter>("ALL");
  const [sector, setSector] = useState(ALL_SECTORS);

  const holdings = new Map((portfolio?.variable_income ?? []).map((p) => [p.ticker, p.size]));
  const all = quotes ?? [];
  const sectors = [...new Set(all.map((q) => q.sector).filter((s): s is string => !!s))].sort();
  const withoutSector = all.filter((q) => !q.sector).length;
  // O menu mostra a contagem de cada setor; "Sem setor" fecha a lista
  const sectorItems = [
    { value: ALL_SECTORS, label: `Todos · ${all.length}` },
    ...sectors.map((s) => ({ value: s, label: `${s} · ${all.filter((q) => q.sector === s).length}` })),
    ...(withoutSector > 0 ? [{ value: NO_SECTOR, label: `Sem setor · ${withoutSector}` }] : []),
  ];
  const sectorName = (value: string) => (value === ALL_SECTORS ? "todos" : value === NO_SECTOR ? "sem setor" : value);

  const term = search.trim().toLowerCase();
  const visible = all.filter(
    (q) =>
      (!term || q.ticker.toLowerCase().includes(term) || q.name.toLowerCase().includes(term)) &&
      (filter === "ALL" || (filter === "HELD" ? holdings.has(q.ticker) : q.asset_class === filter)) &&
      (sector === ALL_SECTORS || (sector === NO_SECTOR ? !q.sector : q.sector === sector)),
  );
  const clearFilters = () => {
    setSearch("");
    setFilter("ALL");
    setSector(ALL_SECTORS);
  };

  // Sem dado, com erro ou sem resultado: a tabela fica com o cabeçalho e a mensagem ocupa uma linha
  const message = error ? (
    <ErrorState
      title="Não deu pra carregar os ativos"
      description="A partida continua; tente de novo."
      error={error}
      onRetry={() => void refetch()}
    />
  ) : all.length === 0 ? (
    <Empty>
      <EmptyHeader>
        <EmptyTitle>Nenhum ativo na base</EmptyTitle>
        <EmptyDescription>O host importa ações na Central de dados, fora da partida.</EmptyDescription>
      </EmptyHeader>
    </Empty>
  ) : visible.length === 0 ? (
    <Empty>
      <EmptyHeader>
        <EmptyTitle>{term ? `Nada com “${search.trim()}”` : "Nenhum ativo com esse filtro"}</EmptyTitle>
      </EmptyHeader>
      <EmptyContent>
        <Button variant="link" size="sm" onClick={clearFilters}>
          Limpar filtros
        </Button>
      </EmptyContent>
    </Empty>
  ) : null;

  const renderBody = () => {
    if (isLoading) {
      return (
        <CardContent>
          <div className="grid gap-4">
            {Array.from({ length: 6 }, (_, i) => (
              <Skeleton key={i} className="h-10" />
            ))}
          </div>
        </CardContent>
      );
    }
    return <MarketTable quotes={visible} holdings={holdings} message={message} />;
  };

  return (
    <Card className="overflow-hidden">
      {/* Filtros */}
      <CardHeader>
        <div className="flex flex-wrap items-center gap-3">
          <InputGroup size="lg" className="w-64">
            <InputGroupAddon>
              <Search />
            </InputGroupAddon>
            <InputGroupInput
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Buscar ticker ou nome"
            />
          </InputGroup>
          <ToggleGroup
            variant="segmented"
            size="field"
            aria-label="Filtrar ativos"
            value={[filter]}
            onValueChange={(values) => values[0] && setFilter(values[0] as Filter)}
          >
            <ToggleGroupItem value="ALL">Todos · {all.length}</ToggleGroupItem>
            <ToggleGroupItem value="HELD">Na carteira · {holdings.size}</ToggleGroupItem>
            {(Object.entries(CLASS_FILTER_LABELS) as [AssetClass, string][]).map(([value, label]) => (
              <ToggleGroupItem key={value} value={value}>
                {label}
              </ToggleGroupItem>
            ))}
          </ToggleGroup>
          {/* Sempre visível: sem setores na base, fica desabilitado */}
          <Select
            items={sectorItems}
            value={sector}
            disabled={sectors.length === 0}
            onValueChange={(value) => setSector(value ?? ALL_SECTORS)}
          >
            <SelectTrigger size="lg" aria-label="Filtrar por setor" className="ml-auto">
              <SelectValue>
                {(value: string) => (
                  <>
                    <span className="text-muted-foreground">Setor:</span> {sectorName(value)}
                  </>
                )}
              </SelectValue>
            </SelectTrigger>
            <SelectContent>
              {sectorItems.map((item) => (
                <SelectItem key={item.value} value={item.value}>
                  {item.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </CardHeader>
      {renderBody()}
    </Card>
  );
}
