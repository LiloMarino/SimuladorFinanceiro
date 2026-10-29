import { useSearchParams } from "react-router-dom";

const PARAM = "deal";

/** A proposta de acordo aberta ou fechada, guardada no endereço: qualquer página pode abri-la e o link da pendência chega nela. */
export function useDealDialog() {
  const [params, setParams] = useSearchParams();

  const setOpen = (open: boolean) =>
    setParams(
      (current) => {
        const next = new URLSearchParams(current);
        if (open) next.set(PARAM, "answer");
        else next.delete(PARAM);
        return next;
      },
      { replace: true },
    );

  return { open: params.get(PARAM) === "answer", setOpen };
}
