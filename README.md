# Soma de Diferença Absoluta — SAD

Implementação RTL do algoritmo SAD (Sum of Absolute Differences) em VHDL estrutural para blocos 16×16 pixels em escala de cinza, com FSM de controle de 6 estados e datapath paralelo. Sintetizado e verificado na FPGA Basys3 (Xilinx Artix-7). Resultado validado: SAD = 0x34F8.

---

## Sobre o projeto

O SAD é amplamente utilizado em compressão de vídeo para medir a similaridade entre dois blocos de imagem. Dado que vídeos exploram a redundância temporal entre quadros consecutivos, o SAD permite decidir quando um quadro deve ser transmitido integralmente ou apenas como diferença em relação ao anterior.

A fórmula implementada é:

```
SAD = Σ |A[i] − B[i]|   para i = 0..255
```

Um resultado igual a zero indica imagens idênticas; valores maiores indicam menor similaridade.

---

## Arquitetura

O projeto segue o modelo RTL com separação entre **bloco de controle** e **bloco operacional**.

### FSM do bloco de controle (6 estados)

| Estado | Descrição |
|--------|-----------|
| S0 | Idle — aguarda `comece = 1` |
| S1 | Inicialização — zera `soma` e contador `i` |
| S2 | Decisão — se `i < 16` vai a S3a; senão vai a S4 |
| S3a | Apresenta endereço às ROMs (latência de 1 ciclo) |
| S3b | Dado válido — acumula parcial e incrementa `i` |
| S4 | Armazena resultado final em `sad_reg` |

> O estado S3a foi adicionado para acomodar a latência de 1 ciclo da ROM gerada pelo IP Catalog do Vivado.

### Bloco operacional

A cada iteração, a ROM entrega 16 bytes simultâneos (128 bits), processados em paralelo:

- 16 instâncias de `abs_diff` calculam `|A[k] − B[k]|`
- Árvore binária de somadores (4 níveis) reduz os 16 resultados parciais
- Acumulador `soma` acumula ao longo das 16 iterações
- Após 16 ciclos, o resultado é transferido para `sad_reg`

### Hierarquia de componentes

```
top_basys3
├── blk_mem_gen_0       (ROM A — IP Vivado)
├── blk_mem_gen_1       (ROM B — IP Vivado)
├── sad_top
│   ├── fsm_controle    (6 estados)
│   └── bloco_operacional
│       ├── abs_diff ×16 (via generate)
│       ├── soma_arvore
│       ├── registrador (acumulador soma)
│       ├── registrador (saída sad_reg)
│       └── contador (índice i, 5 bits)
└── seg7                (display 4 dígitos hex)
```

---

## Arquivos do projeto

| Arquivo | Descrição |
|---------|-----------|
| `abs_diff.vhd` | Calcula \|A − B\| para um par de pixels de 8 bits |
| `soma_arvore.vhd` | Soma 16 valores de 8 bits via árvore binária de 4 níveis |
| `registrador.vhd` | Registrador genérico com load e clear síncronos |
| `contador.vhd` | Contador de 5 bits com clear e incremento |
| `fsm_controle.vhd` | FSM com 6 estados; gera os sinais de controle do datapath |
| `bloco_operacional.vhd` | Instancia abs_diff ×16, árvore, registradores e contador |
| `sad_top.vhd` | Conecta a FSM ao bloco operacional |
| `seg7.vhd` | Multiplexador de 4 dígitos hexadecimais para display de 7 segmentos |
| `top_basys3.vhd` | Top level: conecta ROMs, SAD e display à FPGA Basys3 |
| `sad_tb.vhd` | Testbench com modelo interno das ROMs |
| `gera_imagens.py` | Script Python para geração das imagens sintéticas e arquivos `.coe` |
| `rom_A.coe` | Inicialização da ROM A (gradiente `(16i + j) mod 256`) |
| `rom_B.coe` | Inicialização da ROM B (gradiente com offset de 30) |
| `Relatorio_SAD.pdf` | Relatório técnico completo do laboratório |

---

## Imagens de teste

As imagens foram geradas sinteticamente em Python:

- **Imagem A:** `A[i][j] = (16i + j) mod 256` — gradiente crescente
- **Imagem B:** `B[i][j] = (16i + j + 30) mod 256` — mesma imagem deslocada 30 níveis

SAD esperado: **13560₁₀ = 0x34F8**

---

## Resultados

### Desempenho

| Arquitetura | Ciclos | Pixels/ciclo | Aceleração |
|-------------|--------|--------------|------------|
| ROMs 16×16 bytes (este projeto) | 36 | 16 (paralelo) | ~14× mais rápida |
| ROMs 256×1 byte (referência) | 516 | 1 (sequencial) | referência |

### Recursos após implementação (Basys3 — Artix-7)

| Recurso | Utilizado | Disponível | % |
|---------|-----------|------------|---|
| LUT | 370 | 20800 | 1,78% |
| FF | 59 | 41600 | 0,14% |
| BRAM | 4 | 50 | 8,00% |
| IO | 18 | 106 | 16,98% |
| BUFG | 2 | 32 | 6,25% |

**Consumo total on-chip:** 0,083 W

### Verificação na FPGA

| Método | Decimal | Hexadecimal |
|--------|---------|-------------|
| Cálculo em Python | 13560 | 34F8 |
| Display da FPGA | 13560 | 34F8 |

---

## Como usar na FPGA Basys3

1. Abrir o projeto no Vivado e executar síntese + implementação
2. Gravar o bitstream via *Hardware Manager*
3. Pressionar **btnC** (centro) — reset
4. Pressionar **btnU** (cima) — inicia o cálculo
5. Resultado aparece no display de 7 segmentos em hexadecimal

---

## Ferramentas

- **Vivado** 2024.x (síntese, implementação, geração de bitstream)
- **FPGA:** Basys3 — Xilinx Artix-7 XC7A35T
- **Python 3** com NumPy (geração das imagens e cálculo de referência)

---

## Referências

- VAHID, F. *Sistemas Digitais: Projeto, Otimização e HDLs*. Bookman, 2008.
- PEDRONI, V. *Circuit Design with VHDL*. MIT Press, 2004.

---
