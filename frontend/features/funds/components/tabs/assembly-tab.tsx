import { Gavel } from "lucide-react";
import { FundSection } from "@/shared/components/fund-section";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import type { FundDetails } from "@/types";
import type { FundTabActions } from "../../lib/fund-tabs";
import { FundAssembly } from "../fund-assembly";

type AssemblyTabProps = { fund: FundDetails; actions: Pick<FundTabActions, "open"> };

/** A assembleia: a votação em curso, o último resultado e, ao gestor, a defesa durante a votação. */
export function AssemblyTab({ fund, actions }: AssemblyTabProps) {
  const manager = fund.my_role === "manager";
  const voting = fund.assembly.current?.status === "VOTING";
  const buybackOpen = fund.buyback?.state === "open";
  const quotas = Number(fund.quotas);

  return (
    <div className="grid gap-5 pt-3">
      {/* Defesa do gestor durante a votação */}
      {voting && manager && (
        <Alert variant="destructive">
          <Gavel />
          <AlertTitle>Há uma assembleia para trocar você da gestão</AlertTitle>
          <AlertDescription>
            <div className="grid gap-3">
              <p>
                O voto pesa pelas cotas no fechamento do último pregão, e você conta contra com as suas. Recomprar cotas
                dos outros cotistas tira o peso deles do placar.
              </p>
              <div>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={quotas === 0 || buybackOpen}
                  onClick={() => actions.open("buyback")}
                >
                  Recomprar
                </Button>
              </div>
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* Votação, resultado e convocação */}
      <FundAssembly fund={fund} />
      {fund.assembly.current === null &&
        fund.assembly.last_result === null &&
        (fund.assembly.block === "unlisted" || fund.assembly.block === "manager") && (
          <FundSection title="Assembleia">
            <p className="text-[13px] text-muted-foreground">
              {fund.assembly.block === "unlisted"
                ? "A assembleia nasce com a oferta pública: antes dela, ninguém além do gestor tem cotas para votar."
                : "Nenhum cotista convocou assembleia para trocar você da gestão."}
            </p>
          </FundSection>
        )}
    </div>
  );
}
