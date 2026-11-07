import type { MetricInfo } from "@/shared/lib/metric-info";

export const PLACE_MARGIN: MetricInfo = {
  label: "Margem de erro do lugar",
  description: "Para mais ou para menos, quanto a pesquisa pode errar naquele estado ou região",
  definition:
    "A pesquisa ouve 4.800 pessoas no país, repartidas pelo tamanho de cada lugar. Lugar pequeno recebe poucas entrevistas e erra mais. A margem é 98 ÷ √(entrevistas do lugar), arredondada e mantida entre ±3 e ±12 pontos.",
  example:
    "Ex.: um estado com 4% do eleitorado recebe 192 entrevistas (4% de 4.800); 98 ÷ √192 ≈ 7, então a margem é ±7.",
  reading:
    "Margem pequena (±3) é pesquisa firme; margem grande (±12) é palpite largo. Um líder com 40% e margem ±7 pode ter de 33% a 47%.",
  format: (value) => `±${value}`,
};

export const TECHNICAL_TIE: MetricInfo = {
  label: "Empate técnico",
  description: "A diferença entre o 1º e o 2º cabe na margem de erro: a pesquisa não diz quem lidera",
  definition:
    "No mapa, o lugar fica listrado quando o 1º está a no máximo a margem do lugar de distância do 2º. Se o 3º também cabe na margem do 1º, o empate é entre três.",
  example:
    "Ex.: PTD com 36% e UPR com 33% num estado de margem ±4: a diferença é 3, menor que 4, então o estado é listrado. Com 41% contra 33%, a diferença é 8 e o PTD lidera.",
  reading:
    "Listrado não quer dizer que os dois têm a mesma votação, e sim que a pesquisa não consegue separá-los. Só a apuração decide.",
  format: (value) => `±${value}`,
};

export const CHANGE_SINCE: MetricInfo = {
  label: "Variação desde a pesquisa anterior",
  description: "Quantos pontos a intenção de voto do partido subiu ou caiu no lugar",
  definition: "A intenção de voto de hoje menos a da pesquisa anterior, em pontos percentuais (p.p.).",
  example: "Ex.: de 28% para 31% é +3 p.p.; de 31% para 29% é −2 p.p.",
  reading:
    "Variação menor que a margem de erro do lugar pode ser só ruído da pesquisa. Verde é subida, vermelho é queda; o centro da escala é zero.",
  format: (value) => `${Number(value) > 0 ? "+" : ""}${value} p.p.`,
};
