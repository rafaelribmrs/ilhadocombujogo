# Ilha do Combu — A Semente do Cacau

Jogo educativo **top-down em pixel art** (estilo anos 90: *Pokemon FireRed*,
*Zelda: The Minish Cap*, *Chrono Trigger*) ambientado na **Ilha do Combu**, no
Para. O jogador controla uma crianca paraense que aprende a **plantar e cultivar
o cacau** e descobre curiosidades sobre as plantas nativas da Amazonia.

Projeto da disciplina **Projetos III — UFPA**, baseado nas diretrizes do grupo
(plataforma de ensino gamificada para comunidades locais, inspirada na fabrica
de chocolate da Dona Nena, na Ilha do Combu).

## Como rodar

1. Pré-requisitos
Antes de começar, certifique-se de ter instalado:

Python (versão 3.10 ou superior)

Git (para clonar o repositório)

O gerenciador de pacotes uv (recomendado para gerenciar as dependências do projeto)

2. Clonando o Repositório
Abra o seu terminal (Prompt de Comando, PowerShell ou o terminal do VS Code) e execute os comandos abaixo:

```bash
git clone https://github.com/seu-usuario/ilha-do-combu.git
cd ilha-do-combu
```
3. Executando o Jogo
O projeto utiliza o uv para gerenciar os pacotes (como o pygame-ce) de forma integrada. Você pode rodar o jogo diretamente com um único comando:

```bash
uv run python src/ilha_do_combu/__main__.py
```
Nota: O uv criará o ambiente virtual e instalará o pygame-ce automaticamente na primeira execução.

## Controles

| Tecla            | Acao                          |
| ---------------- | ----------------------------- |
| Setas / WASD     | Andar                         |
| Z / Espaco / E   | Interagir / avancar dialogo   |
| Esc              | Sair                          |

## Estrutura

```
src/ilha_do_combu/
  game.py        # loop principal + gerenciador de cenas
  settings.py    # resolucao (240x160, estilo GBA), paleta, constantes
  art.py         # geracao procedural dos sprites em pixel art
  camera.py      # camera que segue o jogador
  tilemap.py     # mapa em tiles + colisoes
  player.py      # jogador (movimento 4 direcoes + animacao)
  prop.py        # objeto de cenario (colisor + interacao)
  dialogue.py    # caixa de dialogo (estilo Pokemon Emerald)
  transition.py  # fade entre cenas (warp)
  scenes/        # titulo, casa-palafita (interior), quintal (overworld)
```

O jogo comeca na **casa-palafita** (interior) e, pela porta, leva ao **quintal**
(overworld estilo *Pokemon Emerald*: grama, mato alto, trilha, rio e pes de
cacau), com transicao em fade.

> Titulo provisorio — o nome final do jogo ainda esta em aberto nas diretrizes.

## Creditos

- Fonte **Jersey 10** (Sarah Cadigan-Fried), sob licenca SIL Open Font License
  (`src/ilha_do_combu/assets/fonts/OFL.txt`).
- Toda a demais arte (sprites, tiles, cenarios) e gerada por codigo em `art.py`.
