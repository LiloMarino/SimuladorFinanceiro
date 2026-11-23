import { useState } from "react";
import { Building2 } from "lucide-react";
import { MetricHint } from "@/shared/components/metric-hint";
import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/shared/components/ui/alert-dialog";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableFooter,
  TableHead,
  TableHeader,
  TableRow,
} from "@/shared/components/ui/table";
import {
  displayMoney,
  displayMonthName,
  displayMonthYear,
  displayPercent,
  displayShortDate,
} from "@/shared/lib/utils/display";
import type { ProfessionMechanic } from "@/types";
import { useBuyProperty } from "../hooks/mutations/useBuyProperty";
import { useSellProperty } from "../hooks/mutations/useSellProperty";
import { PROPERTY_INDEXES, RENTAL_YIELD, VACANCY_CHANCE } from "../lib/profession-metrics";
import { FigureCard } from "./figure-card";
import { BlockNote, MechanicBlock } from "./mechanic-block";

type LandlordMechanic = Extract<ProfessionMechanic, { kind: "landlord" }>;
type Property = LandlordMechanic["properties"][number];
type Offer = LandlordMechanic["offers"][number];
type LandlordBlockProps = { mechanic: LandlordMechanic };

const OFFER_TITLES: Record<Offer["size"], string> = {
  STUDIO: "Pequeno · kitnet",
  TWO_BEDROOM: "Médio · 2 quartos",
  HOUSE: "Grande · casa",
};

const BLOCK_TITLE = "Sua mecânica: imóveis";
const PORTFOLIO_LINK = [{ label: "Carteira, linha Imóveis", to: "/portfolio" }];

/** "Sua mecânica: imóveis" do Locador: os imóveis com valor, aluguel e situação, o rendimento contra o CDI, a vacância e as ofertas do mês. */
export function LandlordBlock({ mechanic }: LandlordBlockProps) {
  if (mechanic.total === 0) {
    return (
      <MechanicBlock title={BLOCK_TITLE} description="Você vendeu todos os imóveis." status={mechanic.status}>
        {/* Sem imóveis */}
        <div className="flex items-start gap-3 text-[13px]">
          <Building2 className="mt-0.5 size-4 shrink-0 text-muted-foreground" aria-hidden="true" />
          <div className="grid gap-0.5">
            <span className="font-semibold">Nenhum imóvel agora.</span>
            <span className="text-muted-foreground">
              Sem imóvel, a renda do mês é zero. As 3 ofertas do mês estão abaixo; a de{" "}
              {displayMonthName(mechanic.next_offers_on)} chega em {displayShortDate(mechanic.next_offers_on)}.
            </span>
          </div>
        </div>
        <Offers mechanic={mechanic} />
      </MechanicBlock>
    );
  }

  return (
    <MechanicBlock
      title={BLOCK_TITLE}
      description="Sua renda é o aluguel. O valor dos imóveis segue o IVG-R e o aluguel se reajusta pelo IGP-M a cada 12 meses."
      status={mechanic.status}
      links={PORTFOLIO_LINK}
    >
      <Figures mechanic={mechanic} />
      <Properties mechanic={mechanic} />
      <Offers mechanic={mechanic} />
      {/* Regras da compra e do aluguel */}
      <div className="grid gap-1.5">
        <BlockNote>
          Custo de transação de {displayPercent(mechanic.cost_rate, 0)} na compra e na venda (ITBI e corretagem). A
          venda conclui em até {mechanic.sale_months} {mechanic.sale_months === 1 ? "mês" : "meses"}.
        </BlockNote>
        <BlockNote>
          Aluguel inicial de {displayPercent(mechanic.rent_rate, 1, { trim: true })} do preço ao mês, fixado na
          assinatura.
        </BlockNote>
      </div>
    </MechanicBlock>
  );
}

/** Os três números do bloco: o aluguel do mês, o rendimento contra o CDI e a chance de vacância. */
function Figures({ mechanic }: LandlordBlockProps) {
  const { annual_yield: current, full_yield: full } = mechanic;
  const hasVacancy = current !== null && full !== null && Number(full) > Number(current);
  const yieldNote = [
    "aluguel de 12 meses ÷ valor",
    hasVacancy ? `cheio daria ${displayPercent(full, 1)}` : null,
    `o CDI rende ${displayPercent(mechanic.cdi)}`,
  ]
    .filter(Boolean)
    .join(" · ");

  return (
    <div className="grid gap-3 md:grid-cols-3">
      <FigureCard
        label="Aluguel do mês"
        value={displayMoney(mechanic.income)}
        note={`${mechanic.rented} de ${mechanic.total} ${mechanic.total === 1 ? "imóvel alugado" : "imóveis alugados"}`}
      />
      <FigureCard
        label={
          <span className="inline-flex items-center gap-1">
            Rende ao ano <MetricHint metric={RENTAL_YIELD} />
          </span>
        }
        value={current === null ? "—" : displayPercent(current, 1)}
        note={yieldNote}
      />
      <FigureCard
        label={
          <span className="inline-flex items-center gap-1">
            Chance de vacância <MetricHint metric={VACANCY_CHANCE} />
          </span>
        }
        value={`${displayPercent(mechanic.vacancy_chance, 0)} por imóvel no mês`}
        note="sobe com o desemprego e a queda do PIB"
      />
    </div>
  );
}

/** A situação do imóvel em selo, com a linha que a explica sob ele. */
function Situation({ property }: { property: Property }) {
  if (property.status === "VACANT") {
    const months = property.vacant_months ?? 1;
    return (
      <div className="grid justify-items-start gap-1">
        <Badge variant="warning" size="tag">
          Vago há {months} {months === 1 ? "mês" : "meses"}
        </Badge>
        {property.rerent !== null && (
          <span className="text-xs text-muted-foreground">volta com aluguel de {displayMoney(property.rerent)}</span>
        )}
      </div>
    );
  }
  if (property.status === "SELLING") {
    return (
      <div className="grid justify-items-start gap-1">
        <Badge variant="secondary" size="tag">
          Vendendo
        </Badge>
        {property.sale_due !== null && (
          <span className="text-xs text-muted-foreground">conclui até {displayShortDate(property.sale_due)}</span>
        )}
      </div>
    );
  }
  return (
    <Badge variant="success" size="tag">
      Alugado
    </Badge>
  );
}

/** A tabela "Seus imóveis" com o total e o botão de vender de cada linha. */
function Properties({ mechanic }: LandlordBlockProps) {
  const [selling, setSelling] = useState<Property | null>(null);

  return (
    <div className="grid gap-2">
      <h3 className="flex items-center gap-1.5 text-[13px] font-semibold">
        Seus imóveis <MetricHint metric={PROPERTY_INDEXES} />
      </h3>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Imóvel</TableHead>
            <TableHead numeric>Valor hoje</TableHead>
            <TableHead numeric>Aluguel</TableHead>
            <TableHead>Próximo reajuste</TableHead>
            <TableHead>Situação</TableHead>
            <TableHead />
          </TableRow>
        </TableHeader>
        <TableBody>
          {mechanic.properties.map((property) => (
            <TableRow key={property.id}>
              <TableCell>{property.name}</TableCell>
              <TableCell numeric>{displayMoney(property.value)}</TableCell>
              <TableCell numeric>{property.rent === null ? "—" : displayMoney(property.rent)}</TableCell>
              <TableCell>
                {property.next_readjustment === null ? "—" : `${displayMonthYear(property.next_readjustment)} · IGP-M`}
              </TableCell>
              <TableCell>
                <Situation property={property} />
              </TableCell>
              <TableCell>
                {property.status !== "SELLING" && (
                  <Button variant="outline" size="sm" onClick={() => setSelling(property)}>
                    Vender
                  </Button>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
        <TableFooter>
          <TableRow>
            <TableCell>Total</TableCell>
            <TableCell numeric>{displayMoney(mechanic.total_value)}</TableCell>
            <TableCell numeric>{displayMoney(mechanic.income)}</TableCell>
            <TableCell />
            <TableCell />
            <TableCell />
          </TableRow>
        </TableFooter>
      </Table>
      <SellDialog property={selling} mechanic={mechanic} onClose={() => setSelling(null)} />
    </div>
  );
}

type SellDialogProps = { property: Property | null; mechanic: LandlordMechanic; onClose: () => void };

/** Confirma a venda: o imóvel segue rendendo até a conclusão, que sai pelo valor do dia menos o custo de transação, e não se desfaz. */
function SellDialog({ property, mechanic, onClose }: SellDialogProps) {
  const sell = useSellProperty();
  const cost = displayPercent(mechanic.cost_rate, 0);
  const months = `${mechanic.sale_months} ${mechanic.sale_months === 1 ? "mês" : "meses"}`;

  return (
    <AlertDialog open={property !== null} onOpenChange={(open) => !open && onClose()}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Vender {property?.name}?</AlertDialogTitle>
          <AlertDialogDescription>
            {property && (
              <>
                A venda conclui em até {months}, pelo valor do dia da conclusão menos {cost} de ITBI e corretagem. Hoje
                seriam {displayMoney(Number(property.value) * (1 - Number(mechanic.cost_rate)))} no caixa. O imóvel
                segue rendendo até lá. Não dá para desfazer.
              </>
            )}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Agora não</AlertDialogCancel>
          <Button
            variant="outline"
            disabled={sell.isPending}
            onClick={() => property && sell.mutate({ property_id: property.id }, { onSuccess: onClose })}
          >
            Vender imóvel
          </Button>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}

/** As três ofertas do mês, pelo preço do IVG-R de hoje, cada uma com o botão de comprar. */
function Offers({ mechanic }: LandlordBlockProps) {
  const buy = useBuyProperty();

  return (
    <div className="grid gap-2">
      <h3 className="text-[13px] font-semibold">
        Ofertas de {displayMonthName(mechanic.offers_month)} · pelo preço do IVG-R de hoje
      </h3>
      <div className="grid gap-3 md:grid-cols-3">
        {mechanic.offers.map((offer) => (
          <FigureCard
            key={offer.size}
            label={OFFER_TITLES[offer.size]}
            value={displayMoney(offer.price)}
            note={`aluguel inicial ${displayMoney(offer.rent)}`}
            extraNote={`custo de compra ${displayMoney(offer.cost)}`}
            action={
              <Button
                variant="outline"
                disabled={offer.bought || buy.isPending}
                onClick={() => buy.mutate({ size: offer.size })}
              >
                {offer.bought ? "Comprado este mês" : "Comprar"}
              </Button>
            }
          />
        ))}
      </div>
    </div>
  );
}
