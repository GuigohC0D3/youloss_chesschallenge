# Pacote offline (Stockfish 19 + interface)

Substitui a especificação anterior do candidato YoulossTM, que está no histórico do git.

## Conteúdo de `dist/stockfish-chess-challenge.tar.gz`

- `bin/stockfish`: Stockfish 19 sem modificações, build PGO `apple-silicon`, NNUE embutida
- `controller/`: interface web e CLI, sem testes
- `vendor/`: python-chess 1.11.2, com licença
- `engine/`: código-fonte, GPLv3 e `ORIGIN.md`
- `launch_stockfish.sh`, `LEIA-ME.md`
- `RELEASE_MANIFEST.json`: hash de cada arquivo, commit e versões

## O que `verify_offline_release.py` confere

Segurança do arquivo, hash de cada arquivo, `python3` + chess embutido, handshake UCI,
bench 2497913, uma jogada real pela interface com o engine e o lançador.

## Em aberto

- Rodar `./launch_stockfish.sh --dry-run` no próprio M4. O pacote foi testado no M5.
- Ensaio com tabuleiro e relógio físicos, para medir o desconto de `--clock-latency`.
- Resposta da organização: ver `docs/organizer-clarification-draft.md`.
