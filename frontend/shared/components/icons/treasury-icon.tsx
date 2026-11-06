import { forwardRef, useId } from "react";
import type { LucideProps } from "lucide-react";

/**
 * A marca do Tesouro Direto numa cor só (`currentColor`), no mesmo contrato dos ícones do lucide:
 * entra em qualquer lugar que espera um `LucideIcon`.
 */
export const TreasuryIcon = forwardRef<SVGSVGElement, LucideProps>(function TreasuryIcon(
  { size = 24, nonScalingStroke: _nonScalingStroke, ...props },
  ref,
) {
  // A máscara recorta, em branco e preto, o espaço em volta da gota: branco mantém o arco, preto abre o vazio.
  // Cada instância tem a própria máscara: o id é único na página
  const maskId = useId();
  const dropPath =
    "M14.2291 23.0947C12.7896 22.9459 9.99846 21.1274 9.65589 17.3445C9.16824 13.3314 10.6986 6.88191 10.9176 5.92103C11.1984 4.66638 11.263 4.64648 10.6462 4.64648C9.32642 4.64648 6.89284 5.66043 6.75432 6.21668C6.63826 6.67343 5.50945 12.4226 6.15528 16.7513C6.33855 18.2448 6.8496 19.6779 7.651 20.9455C8.33601 22.0232 9.36738 22.8286 10.5709 23.2257C11.7745 23.6227 13.0765 23.5872 14.2572 23.125Z";

  return (
    <svg
      ref={ref}
      xmlns="http://www.w3.org/2000/svg"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
      {...props}
    >
      <defs>
        <mask id={maskId} maskUnits="userSpaceOnUse" x="0" y="0" width="24" height="24">
          <rect width="24" height="24" className="fill-white" />
          <path d={dropPath} className="fill-black stroke-black" strokeWidth="2.4" strokeLinejoin="round" />
        </mask>
      </defs>
      {/* Os dois arcos, recortados em volta da gota */}
      <g mask={`url(#${maskId})`}>
        <path
          d="M0.443686 7.51655C1.13351 7.36399 8.08043 3.10446 15.9867 3.00211C16.5186 2.99803 17.0502 3.02968 17.5779 3.09688C22.124 3.63512 22.1839 5.62985 22.4451 5.56068C22.8353 5.40291 23.1759 5.1409 23.4307 4.80258C23.4503 4.68224 22.8185 2.13031 17.987 0.882297C12.9541 -0.41025 1.98433 1.92562 0.930401 2.70361C0.071162 3.26081 -0.400577 7.86907 0.443686 7.51655Z"
          fill="currentColor"
          stroke="none"
        />
        <path
          d="M16.0265 22.3698C22.4961 19.0295 24.0676 11.3614 23.901 9.62535C23.7943 9.02361 22.965 8.15749 22.7778 8.41903C22.0829 11.0907 20.7876 13.5636 18.9928 15.6446C17.198 17.7257 14.9524 19.3586 12.4314 20.4158C11.8529 20.7712 14.0338 22.8228 15.4892 22.6029C15.675 22.5436 15.8543 22.4655 16.0246 22.3698Z"
          fill="currentColor"
          stroke="none"
        />
      </g>
      {/* A gota */}
      <path d={dropPath} fill="currentColor" stroke="none" />
    </svg>
  );
});
