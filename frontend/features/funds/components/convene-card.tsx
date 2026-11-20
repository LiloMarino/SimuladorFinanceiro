import { Lock } from "lucide-react";
import { useState } from "react";
import { Badge } from "@/shared/components/ui/badge";
import { Button } from "@/shared/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/shared/components/ui/card";
import { Field, FieldContent, FieldDescription, FieldLabel, FieldTitle } from "@/shared/components/ui/field";
import { RadioGroup, RadioGroupItem } from "@/shared/components/ui/radio-group";
import { displayPercent } from "@/shared/lib/utils/display";
import type { FundAssemblyAgenda, FundDetails } from "@/types";
import { AGENDA_LABEL, AGENDA_SUMMARY, AGENDAS, blockReason, optionOf } from "../lib/fund-assembly";

type ConveneCardProps = {
  fund: FundDetails;
  /** Abre o diálogo da troca de gestor */
  onConveneSwap: () => void;
  /** Leva o gestor às Configurações, onde o aumento de taxa é proposto */
  onProposeFee: () => void;
  /** Abre o diálogo da fusão com outra gestora do mesmo gestor */
  onProposeMerge: () => void;
};

/** Convocar uma votação: as pautas que a assembleia aceita, cada uma com o motivo de quem não pode pô-la em votação. */
export function ConveneCard({ fund, onConveneSwap, onProposeFee, onProposeMerge }: ConveneCardProps) {
  const panel = fund.assembly;
  const firstOpen = AGENDAS.find((agenda) => optionOf(panel, agenda)?.can_convene === true) ?? null;
  const [draft, setDraft] = useState<FundAssemblyAgenda | null>(null);
  const selected = draft ?? firstOpen;

  const share = Number(fund.quotas) > 0 ? Number(panel.my_quotas) / Number(fund.quotas) : 0;
  const convene = () => {
    if (selected === "FEE_INCREASE") onProposeFee();
    else if (selected === "MERGE") onProposeMerge();
    else onConveneSwap();
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Convocar uma votação</CardTitle>
        <CardDescription>Com 10% das cotas, qualquer cotista põe uma pauta em votação</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-4">
          <RadioGroup
            value={selected ?? ""}
            onValueChange={(value) => setDraft(value as FundAssemblyAgenda)}
            aria-label="Pauta da votação"
          >
            {AGENDAS.map((agenda) => {
              const reason = blockReason(optionOf(panel, agenda), panel);
              return (
                <FieldLabel key={agenda} variant="fund" htmlFor={`convene-${agenda}`}>
                  <Field orientation="horizontal">
                    <RadioGroupItem
                      variant="fund"
                      value={agenda}
                      id={`convene-${agenda}`}
                      disabled={optionOf(panel, agenda)?.can_convene !== true}
                    />
                    <FieldContent>
                      <FieldTitle>
                        <b className="font-bold">{AGENDA_LABEL[agenda]}</b>
                      </FieldTitle>
                      <FieldDescription>{AGENDA_SUMMARY[agenda]}</FieldDescription>
                      {reason !== null && (
                        <Badge variant="note" size="note">
                          <Lock aria-hidden />
                          {reason}
                        </Badge>
                      )}
                    </FieldContent>
                  </Field>
                </FieldLabel>
              );
            })}
          </RadioGroup>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <span className="text-xs text-muted-foreground">
              {selected === null
                ? "Nenhuma pauta pode ser convocada agora."
                : selected === "FEE_INCREASE"
                  ? "O gestor propõe o aumento nas Configurações."
                  : selected === "MERGE"
                    ? "O gestor propõe a fusão às duas assembleias."
                    : `Você tem ${displayPercent(share, 1)} das cotas; precisa de 10%.`}
            </span>
            <Button variant="fund" size="sm" disabled={selected === null} onClick={convene}>
              Convocar
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
