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

---

## Lógica do código

O bot funciona como um **pipeline** de etapas bem definidas. Cada etapa é
responsável por uma transformação, e a saída de uma alimenta a entrada da
seguinte:

```
imagem (do tabuleiro)
   │  detector_grade + geometria_grade
   ▼
geometria da grade (posição das 49 células)
   │  extrator_celulas
   ▼
imagem de cada célula (49 imagens)
   │  segmentador_doce + visao (características HSV)
   ▼
características de cor de cada célula
   │  classificador_cor
   ▼
Tabuleiro (modelo de dados: 7x7 de Peca)
   │  solver
   ▼
melhor jogada (par de células adjacentes)
   │  executar_bot (calibração + pyautogui)
   ▼
clique/arraste no mouse
```

### 1. Modelo de dados (`src/modelo.py`)

Define as estruturas que representam o jogo de forma independente da tela:

- **`TipoPeca`** — as cores do jogo (`VERMELHO`, `AMARELO`, `VERDE`, `AZUL`,
  `ROXO`, `LARANJA`) mais `VAZIO` para células sem peça.
- **`Especial`** — modificadores de peça (`LISTRADO_H`, `LISTRADO_V`,
  `EMBRULHADO`, `BOMBA_DE_COR`). Usado nas Fases avançadas.
- **`Peca`** — guarda **duas posições distintas** que nunca devem ser confundidas:
  - posição de **grid** (`linha`, `coluna`): índice lógico no array 2D.
  - posição de **pixel** (`x`, `y`): coordenada na tela, usada só quando vamos
    clicar de verdade (Fase 5). Na simulação fica `None`.
- **`Tabuleiro`** — array 2D de `Peca` com utilitários:
  - `vizinhos()` — peças ortogonais válidas.
  - `trocar()` — troca duas peças de posição no grid.
  - `copiar_estado()` — cópia usada para simular jogadas sem alterar o original.
  - `remover()` — marca células como `VAZIO`.
  - `aplicar_gravidade()` — faz as peças "caírem" para preencher buracos.
  - `preencher_vazios()` — sorteia novas peças nos espaços vazios.

### 2. Detecção da grade (`src/detector_grade.py` + `geometria_grade.py`)

Encontra onde estão as 49 células dentro da imagem do tabuleiro:

1. Converte para **escala de cinza** e aplica um leve desfoque.
2. Calcula o **gradiente** da imagem com `Sobel` nas direções X e Y.
3. Projeta cada gradiente em um **perfil 1D** (média por coluna/linha). Picos
   no perfil marcam as bordas verticais/horizontais das células.
4. Detecta os **picos locais** acima de um limiar e agrupa picos muito próximos.
5. Procura a sequência mais regular de `quantidade` limites (8 para uma grade
   7x7), escolhendo a que minimiza o erro de posição e o desvio do espaçamento.
6. O resultado é um objeto `GeometriaGrade` com `limites_x` e `limites_y`, que
   permite obter `limites(linha, coluna)` e `centro(linha, coluna)` de cada
   célula.

### 3. Extração de células (`src/extrator_celulas.py`)

Usa a geometria detectada para **recortar cada célula** da imagem original,
gerando um dicionário `{(linha, coluna): imagem}`. Os limites são limitados ao
tamanho da imagem para evitar índices fora do alcance.

### 4. Segmentação e visão (`src/segmentador_doce.py` + `visao.py`)

Para cada célula recortada, isola o **doce** (a peça) do fundo antes de medir a
cor:

- **`SegmentadorDoce`** cria uma máscara binária usando filtros de matiz,
  saturação e brilho no espaço HSV, seguido de operações morfológicas
  (`MORPH_OPEN`/`MORPH_CLOSE`) e remoção de componentes pequenos.
- **`Visao.analisar()`** calcula as características de cor da célula usando
  apenas os pixels do doce (se houver): matiz médio, saturação, brilho e o
  **matiz dominante** (o valor de matiz mais frequente no histograma).

### 5. Classificação de cor (`src/classificador_cor.py`)

Converte as características de cor em um `TipoPeca`:

- Mantém uma lista de **categorias de referência** (`CATEGORIAS`), cada uma com
  valores típicos de matiz/saturação/brilho.
- Para cada célula, calcula uma **distância ponderada** até cada categoria
  (distância de matiz é circular, pois matiz vai de 0 a 179).
- A categoria de **menor distância** define a peça; a distância também gera uma
  medida de **confiança**.
- O mapeamento `grupo → TipoPeca` está no atributo `MAPEAMENTO`, onde é fácil
  ajustar se as cores não baterem com o jogo.

### 6. Solver guloso (`src/solver.py`)

Decide a melhor jogada simulando trocas num tabuleiro copiado:

- **`_encontrar_linhas_de_match()`** varre o tabuleiro horizontal e
  verticalmente, agrupando sequências contíguas de 3+ peças do mesmo tipo.
- **`_pontuar_grupos()`** pontua cada grupo conforme o tamanho:
  - match de 3 → pontuação base (`10` pts).
  - match de 4 → cria peça listrada (`40` pts).
  - match em L/T → cria peça embrulhada (`50` pts), detectado quando um grupo
    horizontal e um vertical se cruzam na mesma célula.
  - match de 5 → cria bomba de cor (`100` pts).
- **`avaliar_jogada()`** simula a troca e, em loop (até estabilizar ou 20
  iterações), executa o ciclo completo de cascata: remover matches →
  aplicar gravidade → preencher vazios → procurar novos matches, somando a
  pontuação de todas as cascatas.
- **`gerar_jogadas_possiveis()`** gera todas as trocas adjacentes (direita e
  abaixo, para não duplicar pares) e guarda apenas as que pontuam.
- **`melhor_jogada()`** retorna a jogada de maior pontuação, ou `None` se não
  houver nenhuma.

### 7. Execução do bot (`src/executar_bot.py`)

Integra todas as etapas e executa a jogada no jogo de verdade:

1. **Carrega a imagem base** do tabuleiro.
2. **Detecta a grade** e **extrai as células**.
3. **Classifica as cores** de cada célula e **monta o `Tabuleiro`**.
4. **Roda o solver** para encontrar a melhor jogada.
5. Pega as coordenadas **relativas** (dentro da imagem) dos centros das duas
   peças a trocar.
6. **Calibra a posição na tela**: o usuário clica no canto superior esquerdo e
   no canto inferior direito do tabuleiro. O bot calcula a escala e converte as
   coordenadas relativas em **coordenadas absolutas da tela**.
7. **Executa o arraste** com `pyautogui`: move até a primeira peça, segura o
   botão, arrasta até a segunda peça e solta.

---

### Scripts de apoio e debugging

Também há utilitários para inspecionar o pipeline:

- `src/analisar_grade.py` — gera os perfis de gradiente (`perfil_x.png` /
  `perfil_y.png`) e lista os maiores picos de mudança.
- `src/detector_periodicidade.py` — estima o tamanho/período das células
  comparando a imagem com ela mesma deslocada.
- `src/extrator_caracteristicas.py` — extrai estatísticas HSV detalhadas de
  cada célula.
- `src/analisar_grupos.py` — agrupa as células por cor classificada e mostra a
  média de cada característica.
- `src/segmentador_objeto.py` + `src/testar_segmentacao.py` — segmentam o
  objeto central de cada célula e geram máscaras de debug.
- `src/debug_classificacao.py` — desenha a classificação de cada célula sobre a
  imagem e salva `debug_classificacao.png`.
- `src/debug_segmentacao.py` — salva máscaras/visualizações de segmentação e um
  mosaico.

## Setup

```bash
pip install opencv-python numpy mss pyautogui pillow
```

## Estrutura

```
src/    código fonte
tests/  testes com tabuleiros simulados
imagens_teste/  imagens e saídas de debug
