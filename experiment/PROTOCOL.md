# Experiência Wyckoff · protocolo

Escrito a 2026-10-06, antes de haver resultados. Não muda até ao fim.

## Pergunta

Os sinais do scanner Wyckoff dão melhor resultado do que comprar o SPY no mesmo dia?

## Período

Sinais de 2026-10-06 a 2026-12-31.
Veredicto na primeira semana de janeiro de 2027.

## O que conta como sinal

Cada linha do CSV diário é um sinal.
Se o mesmo ticker volta a aparecer no mesmo prazo, só conta como novo sinal depois de o anterior expirar ou fechar.

## Regras de execução

Entrada acima do fecho do dia do sinal. Ordem buy-stop.
Entrada abaixo do fecho. Ordem limite.
Entrada igual ao fecho. Compra na abertura seguinte.
Prazo para execução. 10 sessões no curto prazo. 20 sessões no médio e longo prazo.
Metade da posição sai no TP1. O stop passa para o preço de entrada.
A outra metade sai no TP2 ou no novo stop.
Se o stop e um alvo tocam na mesma sessão, conta o stop.
Duração máxima. 63 sessões no curto prazo. 252 no médio. 504 no longo.
O que estiver aberto no fim é avaliado ao último fecho.

## Medidas

R por trade. Ganho ou perda em múltiplos do risco até ao stop.
Retorno da trade menos o retorno do SPY no mesmo período.
Retorno de fecho a fecho a 5, 10, 20 e 40 sessões, contra o SPY. Não depende das regras de execução.

## Critérios de sucesso

O teste principal é o curto prazo. É o único que pode fechar trades até ao fim do ano.

1. Pelo menos 30 trades fechadas no curto prazo.
2. R médio das trades fechadas acima de 0. O intervalo de confiança de 95% não pode incluir o 0.
3. Retorno a 20 sessões acima do SPY em média. Mais de metade dos sinais bate o SPY.
4. O terço com score mais alto bate o terço com score mais baixo a 20 sessões.

Os critérios 2 e 3 têm de passar para dizer que o método tem vantagem.
O critério 4 diz se o score serve para ordenar os sinais.

O médio e o longo prazo não têm veredicto em 2026. Só se olha para os retornos a 20 e 40 sessões contra o SPY.

## Cortes extra

Por setup. Por notícia negativa no news_check. Por earnings dentro da janela.
Servem para gerar ideias. Não servem para declarar vitória.

## Regras de disciplina

Não mudar parâmetros do scanner até ao fim da experiência.
Se for preciso corrigir um bug, registar a data e o motivo aqui em baixo.

## Alterações

Nenhuma.
