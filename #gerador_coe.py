# gerar_coe.py
import numpy as np
import os
os.chdir(r'C:\Users\augus\OneDrive\Documentos\PED2\SAD_RTL')

# Imagem A — gradiente horizontal
img_A = np.zeros((16,16), dtype=np.uint8)
for i in range(16):
    for j in range(16):
        img_A[i][j] = (i * 16 + j) % 256

# Imagem B — gradiente com offset
img_B = np.zeros((16,16), dtype=np.uint8)
for i in range(16):
    for j in range(16):
        img_B[i][j] = (i * 16 + j + 30) % 256

# Calcula SAD
sad = int(np.sum(np.abs(img_A.astype(int) - img_B.astype(int))))
print(f"SAD esperado: {sad} (hex: {sad:04X})")

# Gera .coe  (16 palavras de 128 bits = 16 bytes cada)
def gera_coe(img, filename):
    with open(filename, 'w') as f:
        f.write("memory_initialization_radix=16;\n")
        f.write("memory_initialization_vector=\n")
        linhas = []
        for i in range(16):
            linha = ''.join(f'{img[i][j]:02x}' for j in range(16))
            linhas.append(linha)
        f.write(',\n'.join(linhas) + ';\n')

gera_coe(img_A, 'rom_A.coe')
gera_coe(img_B, 'rom_B.coe')
print("Arquivos rom_A.coe e rom_B.coe gerados!")