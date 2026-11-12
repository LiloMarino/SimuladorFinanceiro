import { useState } from "react";
import { Search } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardHeader } from "@/shared/components/ui/card";
import { Empty, EmptyContent, EmptyDescription, EmptyHeader, EmptyTitle } from "@/shared/components/ui/empty";
import { InputGroup, InputGroupAddon, InputGroupInput } from "@/shared/components/ui/input-group";
import { Label } from "@/shared/components/ui/label";
import { OptionSelect, type SelectOption } from "@/shared/components/option-select";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { Switch } from "@/shared/components/ui/switch";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { ErrorState } from "@/shared/components/error-state";
import { usePortfolio } from "@/shared/hooks/queries/usePortfolio";
import { useVariableIncomeStocks } from "@/shared/hooks/queries/useVariableIncomeStocks";
import { AssetOriginFlag } from "@/shared/components/asset-origin-flag";
import { ASSET_CLASSES, ASSET_CLASS_LABELS } from "@/shared/lib/asset-class";
import { ASSET_ORIGIN_LABELS, ASSET_ORIGINS } from "@/shared/lib/asset-origin";
import { MarketTable } from "../components/market-table";
import type { AssetClass, AssetOrigin } from "@/types";

type Filter = "ALL" | AssetClass;
const ALL_SECTORS = "__all__";
const NO_SECTOR = "__none__";

export default function VariableIncomePage() {
  const { data: quotes, isLoading, error, refetch } = useVariableIncomeStocks();
  const { data: portfolio } = usePortfolio();
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<Filter>("ALL");
  // Nenhuma origem marcada mostra todas
  const [origins, setOrigins] = useState<AssetOrigin[]>([]);
  const [onlyHeld, setOnlyHeld] = useState(false);
  const [sector, setSector] = useState(ALL_SECTORS);

  const holdings = new Map((portfolio?.variable_income ?? []).map((p) => [p.ticker, p.size]));
  const all = quotes ?? [];
  const sectors = [...new Set(all.map((q) => q.sector).filter((s): s is string => !!s))].sort();
  const withoutSector = all.filter((q) => !q.sector).length;
  const heldCount = all.filter((q) => holdings.has(q.ticker)).length;
  // A lista mostra a contagem de cada setor; "Sem setor" fecha a lista
  const sectorItems: SelectOption[] = [
    { value: ALL_SECTORS, label: "Todos os setores", triggerLabel: "Todos", count: all.length },
    ...sectors.map((s, index) => ({
      value: s,
      label: s,
      count: all.filter((q) => q.sector === s).length,
      dividerBefore: index === 0,
    })),
    ...(withoutSector > 0 ? [{ value: NO_SECTOR, label: "Sem setor", count: withoutSector, dividerBefore: true }] : []),
  ];

  const term = search.trim().toLowerCase();
  const visible = all.filter(
    (q) =>
      (!term || q.ticker.toLowerCase().includes(term) || q.name.toLowerCase().includes(term)) &&
      (filter === "ALL" || q.asset_class === filter) &&
      (origins.length === 0 || origins.includes(q.origin)) &&
      (!onlyHeld || holdings.has(q.ticker)) &&
      (sector === ALL_SECTORS || (sector === NO_SECTOR ? !q.sector : q.sector === sector)),
  );
  const clearFilters = () => {
    setSearch("");
    setFilter("ALL");
    setOrigins([]);
    setOnlyHeld(false);
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
            {ASSET_CLASSES.map((value) => (
              <ToggleGroupItem key={value} value={value}>
                {ASSET_CLASS_LABELS[value]}
              </ToggleGroupItem>
            ))}
          </ToggleGroup>
          <ToggleGroup
            multiple
            variant="segmented"
            size="field"
            aria-label="Filtrar por origem"
            value={origins}
            onValueChange={(values) => setOrigins(values as AssetOrigin[])}
          >
            {ASSET_ORIGINS.map((origin) => (
              <ToggleGroupItem key={origin} value={origin}>
                <AssetOriginFlag origin={origin} />
                {ASSET_ORIGIN_LABELS[origin]}
              </ToggleGroupItem>
            ))}
          </ToggleGroup>
          <div className="ml-auto flex items-center gap-3">
            <div className="flex h-10 items-center gap-2 rounded-lg border border-input px-3">
              <Switch id="only-held" checked={onlyHeld} onCheckedChange={setOnlyHeld} />
              <Label htmlFor="only-held">Na carteira · {heldCount}</Label>
            </div>
            {/* Sempre visível: sem setores na base, fica desabilitado */}
            <OptionSelect
              options={sectorItems}
              value={sector}
              onChange={setSector}
              prefix="Setor"
              disabled={sectors.length === 0}
              searchPlaceholder="Buscar setor"
              aria-label="Filtrar por setor"
              className="min-w-[200px]"
            />
          </div>
        </div>
      </CardHeader>
      {renderBody()}
    </Card>
  );
}
