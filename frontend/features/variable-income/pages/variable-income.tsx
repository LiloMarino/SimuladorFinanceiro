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
import { useVariableIncomeStocks } from "@/features/variable-income/hooks/queries/useVariableIncomeStocks";
import { MarketTable } from "../components/market-table";

type Filter = "ALL" | "HELD" | "STOCK" | "FII" | "ETF";
const ALL_SECTORS = "__all__";

export default function VariableIncomePage() {
  const { data: quotes, isLoading, error, refetch } = useVariableIncomeStocks();
  const { data: portfolio } = usePortfolio();
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<Filter>("ALL");
  const [sector, setSector] = useState(ALL_SECTORS);

  const holdings = new Map((portfolio?.variable_income ?? []).map((p) => [p.ticker, p.size]));
  const all = quotes ?? [];
  const sectors = [...new Set(all.map((q) => q.sector).filter((s): s is string => !!s))].sort();
  const sectorItems = [{ value: ALL_SECTORS, label: "Setor: todos" }, ...sectors.map((s) => ({ value: s, label: s }))];

  const term = search.trim().toLowerCase();
  const visible = all.filter(
    (q) =>
      (!term || q.ticker.toLowerCase().includes(term) || q.name.toLowerCase().includes(term)) &&
      (filter === "ALL" || (filter === "HELD" ? holdings.has(q.ticker) : q.asset_class === filter)) &&
      (sector === ALL_SECTORS || q.sector === sector),
  );
  const clearFilters = () => {
    setSearch("");
    setFilter("ALL");
    setSector(ALL_SECTORS);
  };

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
    if (error) {
      return (
        <CardContent>
          <ErrorState
            title="Não deu pra carregar os ativos"
            description="A partida continua; tente de novo."
            error={error}
            onRetry={() => void refetch()}
          />
        </CardContent>
      );
    }
    if (all.length === 0) {
      return (
        <CardContent>
          <Empty>
            <EmptyHeader>
              <EmptyTitle>Nenhum ativo na base</EmptyTitle>
              <EmptyDescription>O host importa ações na Central de dados, fora da partida.</EmptyDescription>
            </EmptyHeader>
          </Empty>
        </CardContent>
      );
    }
    if (visible.length === 0) {
      return (
        <CardContent>
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
        </CardContent>
      );
    }
    return <MarketTable quotes={visible} holdings={holdings} />;
  };

  return (
    <Card className="overflow-hidden">
      {/* Filtros */}
      <CardHeader>
        <div className="flex flex-wrap items-center gap-3">
          <InputGroup className="w-64">
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
            aria-label="Filtrar ativos"
            value={[filter]}
            onValueChange={(values) => values[0] && setFilter(values[0] as Filter)}
          >
            <ToggleGroupItem value="ALL">Todos · {all.length}</ToggleGroupItem>
            <ToggleGroupItem value="HELD">Na carteira · {holdings.size}</ToggleGroupItem>
            <ToggleGroupItem value="STOCK">Ações</ToggleGroupItem>
            <ToggleGroupItem value="FII">FII</ToggleGroupItem>
            <ToggleGroupItem value="ETF">ETF</ToggleGroupItem>
          </ToggleGroup>
          {sectors.length > 0 && (
            <Select items={sectorItems} value={sector} onValueChange={(value) => setSector(value ?? ALL_SECTORS)}>
              <SelectTrigger size="sm" aria-label="Filtrar por setor">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {sectorItems.map((item) => (
                  <SelectItem key={item.value} value={item.value}>
                    {item.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        </div>
      </CardHeader>
      {renderBody()}
    </Card>
  );
}
