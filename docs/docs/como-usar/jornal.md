---
sidebar_position: 8.8
---

# Jornal

O **Jornal** conta o que acontece no mercado e no país: movimento de ações, decisões do Copom, eleição, medidas do governo, vida dos partidos. Cada manchete tem um **tipo**, e você escolhe, por tipo, como ela chega até você, em **Configurações**, no cartão **Jornal**:

| Nível | O que faz |
| --- | --- |
| **Janela** | A manchete abre no centro da tela, sem pausar a partida, e fecha sozinha (cerca de 8 segundos). No máximo uma janela por pregão; as outras do mesmo dia vão para o cartão. |
| **Jornal** | Aparece no cartão do canto ou na faixa. |
| **Só histórico** | Não aparece na hora, mas fica guardada na lista do Jornal. |
| **Desligado** | Não aparece em lugar nenhum. |

## Eventos raros abrem a janela

Quatro tipos de notícia são raros e por isso abrem a **janela central por padrão**:

- **Ação de campanha em destaque:** uma ação que viraliza ou dá errado, e todo ataque entre partidos.
- **Programa de governo com nome:** o auxílio ou as obras ganham nome, são rebatizados ou acabam.
- **Ruptura de partido:** expulsão, federação formada ou desfeita, acordo de apoio rompido ou deixado.
- **Abertura de oferta pública:** uma gestora abre a venda de cotas a qualquer investidor. A janela traz o botão **Comprar cotas**, que leva ao detalhe da cota na renda variável. A emissão de cotas novas não abre janela: ela segue no cartão do canto, com o botão **Ver**, que leva à página Ofertas públicas. Em Configurações, o tipo oferece **Só ativos da minha carteira**, desligado por padrão: ligado, a emissão só aparece (no canto e no Jornal) para quem tem cotas da gestora.

Quem já salvou as preferências do Jornal antes dessas notícias existirem tem o mapa completo gravado e precisa subir esses quatro tipos para **Janela** à mão; quem nunca mexeu recebe o padrão novo.

## Movimento forte e máxima de 52 semanas

Duas regras de empresa produzem a maior parte das manchetes de mercado, e as duas foram calibradas para não afogar os eventos raros.

### Movimento forte

Uma ação só vira manchete quando se mexe **muito mais do que ela costuma se mexer**. O jogo mede a **oscilação normal** do ativo: a média do tamanho da variação diária (sem sinal) nos últimos 126 pregões, cerca de seis meses.

- O limite é **4 vezes a oscilação normal**, com piso de **3%**. Exemplo: uma ação calma, que costuma mexer 2% por dia, só entra com uma alta ou queda de 8% ou mais; uma ação agitada, que costuma mexer 4% por dia, só entra a partir de 16%. Um fundo imobiliário que costuma mexer 0,2% por dia entra a 3% (o piso), e não a 0,8%.
- Com **menos de 63 pregões** de histórico (cerca de três meses), a média ainda não é confiável e vale o limite fixo de **5%**.
- No máximo **3 por pregão**, na ordem de quantas vezes o movimento superou a oscilação normal: 6% numa ação que costuma mexer 0,5% (12 vezes) vem antes de 15% numa que costuma mexer 3% (5 vezes).

### Máxima de 52 semanas

A manchete só sai no **rompimento**: o preço fecha acima da máxima do último ano **e** essa máxima tem pelo menos 63 pregões (cerca de três meses). Uma ação que sobe todo dia renova a máxima todo dia, mas a máxima de ontem tem idade zero e não conta; assim o mesmo ativo gera no máximo 4 manchetes por ano.

## O Fundo Soberano no jornal

Quatro tipos de manchete contam o fundo do governo: o **aporte** que chegou ao caixa dele, cada **compra**, cada **venda** (que devolve o dinheiro ao Tesouro) e o **favorecimento**, quando o fundo compra uma gestora de aliado do governo. Cada uma leva a sigla do partido do presidente. As compras e vendas de um mesmo ativo no dia viram uma manchete só, no fim do pregão. Veja [O Fundo Soberano](governo.md#o-fundo-soberano).

## Textos que variam

As manchetes do governo e da campanha têm **três redações** cada, e o jogo escolhe uma delas pela partida, pelo dia e pelo fato. O mesmo fato lido de novo traz sempre o mesmo texto, e dois fatos parecidos não saem com a mesma frase.
