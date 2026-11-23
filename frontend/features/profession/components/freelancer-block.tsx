import type { ReactNode } from "react";
import { Controller, useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { TriangleAlert } from "lucide-react";
import { z } from "zod";
import { MetricHint } from "@/shared/components/metric-hint";
import { Alert, AlertDescription } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import { Field, FieldError, FieldLabel } from "@/shared/components/ui/field";
import { Input } from "@/shared/components/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/shared/components/ui/table";
import { displayMoney, displayPercent, displayShortDate } from "@/shared/lib/utils/display";
import { formatMoney } from "@/shared/lib/utils/format";
import { moneyToBody, moneyToField } from "@/shared/lib/utils/money-field";
import type { ProfessionMechanic } from "@/types";
import { useSetPrice } from "../hooks/mutations/useSetPrice";
import { MARKET_REFERENCE, SERVICE_PRICE } from "../lib/profession-metrics";
import { MechanicBlock } from "./mechanic-block";
import { PROFESSION_HISTORY_ID } from "./profession-history";

type FreelancerMechanic = Extract<ProfessionMechanic, { kind: "freelancer" }>;
type FreelancerBlockProps = { mechanic: FreelancerMechanic };

const clientsText = (value: string) =>
  new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 1 }).format(Number(value));

/** "Sua mecânica: tabela de preços" do Autônomo: o preço contra a referência do mercado e o que cada preço renderia. */
export function FreelancerBlock({ mechanic }: FreelancerBlockProps) {
  const behind = displayPercent(Math.abs(Number(mechanic.deviation)), 0);

  return (
    <MechanicBlock
      title="Sua mecânica: tabela de preços"
      description={
        mechanic.stale
          ? `O preço está parado há ${mechanic.stalled_months} meses.`
          : "Você define o preço uma vez por mês. Mais caro rende mais por cliente e perde clientes."
      }
      status={mechanic.status}
      links={[{ label: "Histórico da profissão", anchor: PROFESSION_HISTORY_ID }]}
    >
      {/* Os números do preço */}
      <div className="grid gap-3 md:grid-cols-3">
        <FigureCard
          label={
            <span className="inline-flex items-center gap-1">
              Seu preço <MetricHint metric={SERVICE_PRICE} />
            </span>
          }
          value={displayMoney(mechanic.price)}
          note={`por atendimento, desde ${displayShortDate(mechanic.price_since)}`}
        />
        <FigureCard
          label={
            <span className="inline-flex items-center gap-1">
              Referência do mercado <MetricHint metric={MARKET_REFERENCE} />
            </span>
          }
          value={displayMoney(mechanic.reference)}
          note={
            mechanic.stale
              ? `subiu ${displayPercent(mechanic.reference_rise, 0)} desde o seu último ajuste`
              : "sobe com o IPCA todo mês"
          }
        />
        <FigureCard
          label="Renda do mês"
          value={displayMoney(mechanic.month_income)}
          note={`${displayMoney(mechanic.price)} × ${clientsText(mechanic.clients)} clientes`}
        />
      </div>
      {/* O preço parado contra a referência */}
      {mechanic.stale && (
        <Alert variant="warning">
          <TriangleAlert />
          <AlertDescription>
            <b className="font-semibold">A inflação está comendo a sua renda.</b> O preço ficou {behind} atrás da
            referência: o cliente paga menos do que o mercado cobra e a renda não acompanha o custo de vida. Reajustar
            para {displayMoney(mechanic.reference)} devolve a renda ao nível da inflação.
          </AlertDescription>
        </Alert>
      )}
      <PriceForm mechanic={mechanic} />
      <PriceTable mechanic={mechanic} />
    </MechanicBlock>
  );
}

/** O formulário do novo preço, que nasce com o preço salvo e valida a faixa que o servidor aceita. */
function PriceForm({ mechanic }: FreelancerBlockProps) {
  const setPrice = useSetPrice();
  const low = Number(mechanic.min_price);
  const high = Number(mechanic.max_price);
  const schema = z.object({
    price: z.string().refine(
      (text) => {
        const value = Number(moneyToBody(text));
        return value >= low && value <= high;
      },
      `O preço vai de ${displayMoney(mechanic.min_price)} a ${displayMoney(mechanic.max_price)}.`,
    ),
  });
  const form = useForm<z.infer<typeof schema>>({
    resolver: zodResolver(schema),
    values: { price: moneyToField(mechanic.price) },
  });
  const submit = form.handleSubmit((fields) => setPrice.mutate({ price: moneyToBody(fields.price) }));

  return (
    <form
      onSubmit={(event) => void submit(event)}
      className="grid items-end gap-x-4 gap-y-2 border-y py-3 md:grid-cols-[auto_1fr_auto]"
    >
      <Controller
        control={form.control}
        name="price"
        render={({ field, fieldState }) => (
          <Field data-invalid={fieldState.invalid} className="md:w-60">
            <FieldLabel htmlFor="freelancer-new-price">
              Novo preço <MetricHint metric={SERVICE_PRICE} />
            </FieldLabel>
            <Input
              id="freelancer-new-price"
              numeric
              inputMode="decimal"
              autoComplete="off"
              aria-invalid={fieldState.invalid}
              disabled={!mechanic.can_change_price}
              {...field}
              onChange={(event) => field.onChange(formatMoney(event.target.value))}
            />
            {fieldState.error && <FieldError errors={[fieldState.error]} />}
          </Field>
        )}
      />
      <p className="text-xs text-muted-foreground">{mechanic.unemployment_note}</p>
      <div className="grid justify-items-start gap-1 md:justify-items-end">
        <Button
          type="submit"
          variant={mechanic.stale ? "default" : "outline"}
          disabled={!mechanic.can_change_price || setPrice.isPending}
        >
          Salvar o preço
        </Button>
        <span className="text-xs text-muted-foreground">
          {mechanic.next_price_change
            ? `próximo ajuste em ${displayShortDate(mechanic.next_price_change)}`
            : "uma mudança por mês"}
        </span>
      </div>
    </form>
  );
}

function PriceTable({ mechanic }: FreelancerBlockProps) {
  return (
    <div className="grid gap-2">
      <span className="text-[13px] font-semibold">Quanto cada preço daria este mês</span>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Preço</TableHead>
            <TableHead numeric>Clientes no mês</TableHead>
            <TableHead numeric>Renda esperada</TableHead>
            <TableHead numeric>Chance de mês sem clientes</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {mechanic.rows.map((row) => {
            const yours = row.price === mechanic.price;
            const gap = Number(row.deviation);
            const label = `${displayMoney(row.price)} · ${gap === 0 ? "igual à referência" : `${displayPercent(gap, 0)} acima`}`;
            return (
              <TableRow key={row.deviation}>
                <TableCell>{yours ? <b className="font-bold">{label}</b> : label}</TableCell>
                <TableCell numeric>{clientsText(row.clients)}</TableCell>
                <TableCell numeric>{displayMoney(row.income)}</TableCell>
                <TableCell numeric>{displayPercent(row.empty_month_chance, 0)}</TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
}

type FigureCardProps = { label: ReactNode; value: string; note: string };

function FigureCard({ label, value, note }: FigureCardProps) {
  return (
    <div className="grid content-start gap-1 rounded-[10px] border p-4">
      <span className="text-[13px] font-semibold">{label}</span>
      <b className="font-mono text-[17px] font-semibold">{value}</b>
      <span className="text-xs text-muted-foreground">{note}</span>
    </div>
  );
}
