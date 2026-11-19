import { Gavel, Info } from "lucide-react";
import { useState } from "react";
import { Alert, AlertDescription, AlertTitle } from "@/shared/components/ui/alert";
import { Button } from "@/shared/components/ui/button";
import type { FundDetails } from "@/types";
import { currentOf } from "../../lib/fund-assembly";
import type { FundTabActions } from "../../lib/fund-tabs";
import { AssemblyHistoryCard } from "../assembly-history-card";
import { AssemblyInviteCard } from "../assembly-invite-card";
import { AssemblyVoteCard } from "../assembly-vote-card";
import { ConveneCard } from "../convene-card";
import { ConveneDialog } from "../convene-dialog";

type AssemblyTabProps = { fund: FundDetails; actions: Pick<FundTabActions, "open" | "goTo"> };

/** A assembleia: as votações abertas, a convocação de uma pauta e o histórico; ao gestor, a defesa durante a troca. */
export function AssemblyTab({ fund, actions }: AssemblyTabProps) {
  const [conveneOpen, setConveneOpen] = useState(false);
  const panel = fund.assembly;
  const manager = fund.my_role === "manager";
  const swap = currentOf(panel, "REPLACE_MANAGER");
  const buybackOpen = fund.buyback?.state === "open";
  const quotas = Number(fund.quotas);
  const open = panel.current.length > 0;

  return (
    <div className="grid gap-5 pt-3">
      {/* Regra da assembleia */}
      <Alert variant="info">
        <Info />
        <AlertDescription>
          <b className="font-semibold">Como a assembleia decide:</b> com 10% das cotas, qualquer cotista convoca; a
          votação dura 5 pregões e vence a maioria das cotas que votaram. Empate, ou nenhum voto, mantém tudo como está.
        </AlertDescription>
      </Alert>

      {/* Defesa do gestor durante a votação */}
      {swap?.status === "VOTING" && manager && (
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

      {/* Votações abertas e convocação */}
      <div className={open ? "grid items-start gap-5 xl:grid-cols-[2fr_1fr]" : "grid gap-5"}>
        {open && (
          <div className="grid gap-5">
            {swap?.status === "INVITED" && <AssemblyInviteCard fundId={fund.id} assembly={swap} />}
            {panel.current
              .filter((assembly) => assembly.status === "VOTING")
              .map((assembly) => (
                <AssemblyVoteCard key={assembly.id} fund={fund} assembly={assembly} />
              ))}
          </div>
        )}
        <ConveneCard
          fund={fund}
          onConveneSwap={() => setConveneOpen(true)}
          onProposeFee={() => actions.goTo("settings")}
        />
      </div>

      {panel.history.length > 0 && <AssemblyHistoryCard history={panel.history} />}

      <ConveneDialog
        open={conveneOpen}
        onOpenChange={setConveneOpen}
        fundId={fund.id}
        fundName={fund.name}
        managerNickname={fund.manager_nickname}
      />
    </div>
  );
}
