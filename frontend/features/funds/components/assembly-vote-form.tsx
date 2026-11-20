import { useState } from "react";
import { Button } from "@/shared/components/ui/button";
import { Field, FieldContent, FieldDescription, FieldLabel, FieldTitle } from "@/shared/components/ui/field";
import { RadioGroup, RadioGroupItem } from "@/shared/components/ui/radio-group";
import { Spinner } from "@/shared/components/ui/spinner";
import { displayQuantity } from "@/shared/lib/utils/display";
import { useCastAssemblyVote } from "../hooks/mutations/useCastAssemblyVote";
import type { AssemblyCurrent } from "../lib/fund-assembly";
import { mergeChoices } from "../lib/fund-merge";

type Choice = "favor" | "against";

type ChoiceText = Record<Choice, { title: string; hint: string }>;

/** O que cada lado do voto significa na pauta; a fusão diz o nome das gestoras. */
function choicesOf(assembly: AssemblyCurrent): ChoiceText {
  if (assembly.agenda === "MERGE" && assembly.merge !== null) {
    const hints = mergeChoices(assembly.merge);
    return { favor: { title: "A favor", hint: hints.favor }, against: { title: "Contra", hint: hints.against } };
  }
  if (assembly.agenda === "FEE_INCREASE") {
    return {
      favor: { title: "A favor", hint: "A taxa sobe" },
      against: { title: "Contra", hint: "A taxa fica como está" },
    };
  }
  return {
    favor: { title: "A favor", hint: "A gestão passa ao candidato" },
    against: { title: "Contra", hint: "O gestor atual fica" },
  };
}

const toChoice = (vote: boolean | null): Choice | null => (vote === null ? null : vote ? "favor" : "against");

type AssemblyVoteFormProps = { fundId: number; assembly: AssemblyCurrent; myQuotas: string };

/** O voto de quem tem cotas: a escolha é um rascunho até confirmar, e o voto salvo vale até o fim da votação. */
export function AssemblyVoteForm({ fundId, assembly, myQuotas }: AssemblyVoteFormProps) {
  const vote = useCastAssemblyVote(fundId);
  const [draft, setDraft] = useState<Choice | null>(null);
  const saved = toChoice(assembly.my_vote);
  const choice = draft ?? saved;
  const options = choicesOf(assembly);

  const confirm = () => {
    if (choice === null) return;
    vote.mutate({ agenda: assembly.agenda, in_favor: choice === "favor" }, { onSuccess: () => setDraft(null) });
  };

  return (
    <div className="grid gap-3">
      <span className="text-[13px] font-medium">Seu voto, que você muda até o fim:</span>
      <RadioGroup
        value={choice ?? ""}
        onValueChange={(value) => setDraft(value as Choice)}
        className="sm:grid-cols-2"
        aria-label="Seu voto"
      >
        {(["favor", "against"] as const).map((key) => (
          <FieldLabel key={key} variant="fund" htmlFor={`vote-${assembly.id}-${key}`}>
            <Field orientation="horizontal">
              <RadioGroupItem variant="fund" value={key} id={`vote-${assembly.id}-${key}`} />
              <FieldContent>
                <FieldTitle>
                  <b className="font-bold">{options[key].title}</b>
                </FieldTitle>
                <FieldDescription>{options[key].hint}</FieldDescription>
              </FieldContent>
            </Field>
          </FieldLabel>
        ))}
      </RadioGroup>
      <div className="flex flex-wrap items-center justify-between gap-3">
        <span className="text-xs text-muted-foreground">
          Você tem {displayQuantity(myQuotas)} cotas: o peso do seu voto é o das cotas no fechamento do pregão.
        </span>
        <Button
          variant="fund"
          size="sm"
          disabled={vote.isPending || draft === null || draft === saved}
          onClick={confirm}
        >
          {vote.isPending && <Spinner />}
          Confirmar voto
        </Button>
      </div>
    </div>
  );
}
