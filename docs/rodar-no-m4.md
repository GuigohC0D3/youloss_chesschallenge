# Rodar o projeto no M4 (plano B)

O M5 é a máquina principal. O M4 precisa estar pronto **antes do evento**, para assumir se o M5
falhar. Faça tudo abaixo com antecedência, com internet, e repita o passo 4 no dia.

Há dois caminhos. Use o **pacote** (caminho A): é o que foi verificado e não precisa compilar
nada.

## Caminho A: pacote (recomendado)

### 1. No M5: copiar o pacote e as tablebases

Copie para um pendrive (ou mande por AirDrop):

- `dist/stockfish-chess-challenge.tar.gz` (cerca de 80 MB);
- a pasta `assets/syzygy/` inteira (939 MB, 290 arquivos). Ela não vem no pacote nem no git.

Se o pacote ainda não existir no M5, gere a partir de um checkout limpo:

```bash
.venv/bin/python scripts/build_offline_release.py
.venv/bin/python scripts/verify_offline_release.py dist/stockfish-chess-challenge.tar.gz
```

### 2. No M4: extrair numa pasta nova

O arquivo não tem pasta própria dentro dele: extraia numa pasta vazia.

```bash
mkdir -p ~/chess
tar -xzf /caminho/do/stockfish-chess-challenge.tar.gz -C ~/chess
```

Para conferir que o arquivo chegou inteiro, compare o resultado de
`shasum -a 256 /caminho/do/stockfish-chess-challenge.tar.gz` com o mesmo comando rodado no M5.

### 3. No M4: colocar as tablebases

```bash
cp -R /caminho/do/syzygy ~/chess/assets/syzygy
ls ~/chess/assets/syzygy | wc -l      # deve mostrar 290
```

Sem essa pasta o motor joga normalmente, mas sem os finais perfeitos de até 5 peças.

### 4. No M4: conferir o Mac

```bash
cd ~/chess
./launch_stockfish.sh --dry-run
```

O resultado esperado termina assim (threads e memória dependem do modelo do M4):

```text
Perfil: 9 threads, 2048 MiB
Engine: Stockfish 19 + YoulossTM, bench 2497913 correto
Verificação concluída: este Mac pode rodar a partida.
```

Se aparecer `python3 (3.9 ou mais novo) não encontrado`, rode `xcode-select --install`
**com internet** e repita. Se o macOS bloquear o script, use `bash launch_stockfish.sh --dry-run`.
Se o bench der outro número, não jogue com essa cópia: copie o pacote de novo.

### 5. No M4: abrir a interface

```bash
cd ~/chess
./launch_stockfish.sh
```

O navegador abre em `http://127.0.0.1:8765/`. No Terminal, a primeira linha precisa mostrar
**`com tablebases`**, por exemplo:

```text
Stockfish 19 YoulossTM | 9 threads | 2048 MiB | com tablebases
```

Se mostrar `sem tablebases`, refaça o passo 3. Se a porta estiver ocupada, use
`./launch_stockfish.sh --port 8766`. Para encerrar, `Ctrl-C` no Terminal.

## Caminho B: clone do repositório

Precisa de internet, das ferramentas de linha de comando da Apple (`xcode-select --install`) e
de **Python 3.12 ou mais novo**: o `python3` que vem com o macOS é 3.9 e não serve aqui. Instale
pelo python.org se precisar.

```bash
git clone https://github.com/GuigohC0D3/youloss_chesschallenge.git
cd youloss_chesschallenge
bash scripts/setup_mac.sh             # compila, instala e testa; termina com "OK: bench 2497913"
cp -R /caminho/do/syzygy assets/syzygy
.venv/bin/python -m controller.web
```

A mesma regra vale: a primeira linha precisa mostrar `com tablebases`.

## No dia, antes de cada rodada

- Mac na tomada, tampa aberta, numa superfície dura e ventilada.
- Wi-Fi desligado: o regulamento proíbe comunicação online, e o projeto não precisa de rede.
- Feche os outros apps e ative o Não Perturbe.
- Reinicie o Mac antes do evento.
- Confira `com tablebases` e o tempo da partida (`1500+0`, ou o que a organização definir).

## Durante a partida

1. Em **Nova partida**, escolha **Nossa cor**, o **Adversário**, o **Partida nº** e o
   **Tempo (seg + inc)**. Clique **Iniciar partida** junto com o relógio físico.
2. Digite o lance do adversário em **Lance do adversário** e tecle Enter: `e4`, `Nf3`, `Cf3`,
   `O-O` ou `e2e4`.
3. O nosso lance aparece em destaque. Jogue no tabuleiro e aperte o relógio.
4. O relógio da tela é estimativa; o físico manda. Se divergir, corrija em **Nós mm:ss** e
   **Adv mm:ss** e clique **Aplicar**.
5. Digitou errado? **Desfazer último lance dele**.
6. No fim, marque **Ganhamos**, **Empate** ou **Perdemos**.

Os registros ficam em `logs/` dentro da pasta.

## Se o M5 falhar no meio de uma partida

O botão **Retomar** continua uma partida não terminada a partir de `logs/` **da mesma máquina**.
Copiar `logs/` do M5 para o M4 e retomar lá **não foi testado**: se precisar trocar de máquina,
confira o tabuleiro e os relógios na tela antes de seguir.
