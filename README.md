# Candy Crush Bot

Bot para jogar Candy Crush Saga automaticamente: visão computacional para ler o
tabuleiro + um solver guloso para decidir a melhor jogada + automação de mouse
para executá-la.

## Plano do projeto

- **Fase 0 — Setup** ✅
  Estrutura do projeto, dependências, repositório git.

- **Fase 1 — Modelo de dados**
  `Peca` (tipo, posição no grid, coordenadas de pixel) e `Tabuleiro`
  (array 2D de `Peca` + utilitários: vizinhos, troca, cópia de estado).

- **Fase 2 — Solver guloso (sem tela)**
  Avalia todas as jogadas adjacentes válidas num tabuleiro simulado,
  pontua cada uma (match 3 / 4 listrado / L-T embrulhado / 5 bomba de cor /
  combo de especiais) e escolhe a melhor. Sem lookahead.

- **Fase 2.1 — Cascata completa** ✅
  Após a troca, o solver simula remoção, gravidade, reenchimento e novas
  cascatas até o tabuleiro estabilizar.

- **Fase 3 — Leitura da tela**
  Captura de tela (`mss`) + template matching (`opencv`) para reconstruir
  o `Tabuleiro` real a partir da tela do jogo, incluindo coordenadas de
  pixel de cada célula.

- **Fase 4 — Integração solver + tela**
  Capturar → reconstruir tabuleiro → rodar solver → imprimir a jogada
  escolhida (ainda sem executar).

- **Fase 5 — Automação de input**
  Traduzir a jogada em clique/arraste com `pyautogui`, com espera para
  animações e cascatas.

- **Fase 6 — Loop completo**
  Capturar → ler → avaliar → executar → esperar estabilizar → repetir,
  até detectar fim de jogo.

- **Fase 7 — Refinamentos (opcional)**
  Doces especiais existentes, lookahead raso (2 jogadas), calibração
  automática de grade, logging/estatísticas.

## Setup

```bash
pip install opencv-python numpy mss pyautogui pillow
```

## Estrutura

```
src/    código fonte
tests/  testes com tabuleiros simulados
```
