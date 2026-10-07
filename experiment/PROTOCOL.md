# Experiência Wyckoff · protocolo

Versão 2. Escrita a 2026-10-07. Substitui a versão 1 de 2026-10-06.
Nenhum sinal tinha ainda sessões posteriores quando a versão 2 foi escrita.

## Pergunta

Os sinais do scanner comportam-se como o método prevê?
Ou seja, o preço chega ao alvo dentro do prazo esperado sem tocar primeiro no stop?

## Período

Sinais de 2026-10-06 a 2026-12-31.
Veredicto na primeira semana de janeiro de 2027.

## O que conta como sinal

Cada linha do CSV diário é um sinal.
O sinal começa no fecho da sessão que o scanner usou.
Se o mesmo ticker volta a aparecer no mesmo prazo, só conta como novo sinal depois de o anterior estar resolvido.
Não há simulação de entradas nem de gestão de posição.

## Prazo esperado

Curto prazo. 63 sessões.
Médio prazo. 252 sessões.
Longo prazo. 504 sessões.

## Resultado de cada sinal

TP1 primeiro. O preço toca o TP1 dentro do prazo sem ter tocado no stop.
Stop primeiro. O preço toca o stop dentro do prazo antes do TP1.
Prazo esgotado. Nenhum dos dois foi tocado dentro do prazo.
Em curso. Ainda não passou o prazo e nenhum dos dois foi tocado.
Se a mesma sessão toca o TP1 e o stop, conta como stop.
Também se regista se o TP2 foi tocado antes do stop.

## Linha de base

Num passeio aleatório sem tendência, a probabilidade de tocar o TP1 antes do stop é (preço menos stop) a dividir por (TP1 menos stop).
Esta probabilidade é calculada para cada sinal.
A soma dá o número de TP1 esperado por acaso.
O z compara o número observado com o esperado.

## Critérios de sucesso

O teste principal é o curto prazo. É o único com tempo para resolver muitos sinais até ao fim do ano.

1. Pelo menos 30 sinais de curto prazo resolvidos, contando TP1 primeiro e stop primeiro.
2. A taxa de TP1 primeiro é maior do que a taxa esperada por acaso, com z de 2 ou mais.
3. A mediana de sessões até ao TP1 fica dentro das 63 sessões.
4. O terço com score mais alto tem taxa de TP1 primeiro maior do que o terço com score mais baixo.

Os critérios 1 e 2 têm de passar para dizer que os sinais de curto prazo funcionam.
O critério 3 diz se o tempo esperado está certo.
O critério 4 diz se o score serve para ordenar os sinais.

## Médio e longo prazo

Não têm veredicto em 2026. O prazo é longo demais.
Só se olha para os pontos de controlo a 20, 40 e 60 sessões.
Em cada ponto conta a percentagem de sinais que já tocou o TP1 e a que já tocou o stop.
Também se olha para o progresso até cada nível nos sinais em curso.

## Cuidado com sinais por resolver

Os sinais resolvidos cedo não são uma amostra neutra.
Por isso o veredicto também mostra os pontos de controlo a 20 e 40 sessões, que usam todos os sinais com histórico suficiente.

## Cortes extra

Por setup. Por notícia negativa no news_check. Por earnings dentro da janela.
Servem para gerar ideias. Não servem para declarar vitória.

## Regras de disciplina

Não mudar parâmetros do scanner até ao fim da experiência.
Se for preciso corrigir um bug, registar a data e o motivo aqui em baixo.

## Alterações

2026-10-07. Versão 2. A medida passa de resultado de trades simuladas para comportamento do sinal. O sinal começa no fecho do scan e conta o nível tocado primeiro dentro do prazo. Pedido do João antes de haver dados.
2026-10-07. O tracker passa a usar a data da sessão do scan. Corridas tardias gravam o CSV com a data UTC do dia seguinte.
