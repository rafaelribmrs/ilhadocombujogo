# Diretrizes do Projeto

Resumo das diretrizes do grupo (apresentacao de **Projetos III — UFPA**) e de
como o desenvolvimento atual as atende.

## Conceito (do PDF)

- **Plataforma de ensino gamificada para comunidades locais.**
- Jogo educativo voltado a **cultura amazonica**, pensado para **criancas
  ribeirinhas**.
- Inspiracao: a **fabrica de chocolate da Dona Nena**, na **Ilha do Combu**.
- **Historia:** o jogo se passa na Ilha do Combu; o protagonista e uma crianca
  paraense (nome/historia em aberto); a missao e **aprender a plantar e cultivar
  o cacau**. Ao longo do jogo, o jogador conhece **plantas nativas da Amazonia**
  e suas tecnicas de plantio (ex.: acai).
- **Inicio:** na casa do protagonista — uma **palafita**, moradia tradicional.
- **Estetica:** jogos dos anos 90 — *Pokemon FireRed*, *Zelda: The Minish Cap*,
  *Chrono Trigger*. Simples, cativante e com **estetica paraense**.

## Decisoes tecnicas deste desenvolvimento

| Tema | Diretriz original | Aqui |
| --- | --- | --- |
| Estilo | Top-down pixel art anos 90 | **Mantido** (resolucao nativa 240x160, estilo GBA) |
| Engine | GDevelop (no-code) | **Python + pygame-ce** (codigo versionado em git) |
| Arte | Sprites via IA (ChatGPT/Gemini) | **Pixel art procedural** (em `art.py`); sprites de IA podem substituir depois |

## O que ja existe (fatia vertical)

- Engine: loop principal, gerenciador de cenas, escala pixel-perfect, **fade**
  entre cenas (warp estilo Pokemon).
- Tela de titulo com cenario da ilha.
- **Casa-palafita** jogavel: andar nas 4 direcoes com animacao, colisoes,
  camera, e objetos interativos com conteudo educativo (muda de cacau, rede,
  fogao a lenha, cesto de acai, bilhete da mae).
- **Quintal (overworld estilo Pokemon Emerald):** grama, mato alto, trilha de
  terra, rio, pes de cacau frutificando e placa, alcancado pela porta da casa.
- UI **estilo Pokemon Emerald** (caixa de texto clara com borda azul-marinho) e
  sistema de dialogo com efeito maquina-de-escrever.

## Proximos passos sugeridos

1. **Mini-game de plantio do cacau:** preparar a terra, plantar a muda, regar,
   esperar crescer, colher (nucleo educativo da missao).
2. **Travessia de canoa / mapa da Ilha do Combu:** exploracao com pontos de
   interesse (acai, outras plantas nativas) e curiosidades.
3. **Audio:** trilha e efeitos (ponto levantado como pendencia no PDF).
4. **Roteiro e nome do protagonista** (em aberto nas diretrizes).
5. **Export web** (pygbag) para rodar no navegador, facilitando o acesso das
   comunidades.
