import pandas as pd
import zipfile
import os

# Dados falsos que imitam a estrutura da Receita Federal
# Coluna 0: Código CNAE (String)
# Coluna 1: Descrição (String)
dados = [
    ["0111301", "Cultivo de arroz"],
    ["0111302", "Cultivo de milho"],
    ["0111303", "Cultivo de trigo"],
    ["6201501", "Desenvolvimento de programas de computador sob encomenda"],
    ["6202300", "Desenvolvimento e licenciamento de programas de computador customizáveis"],
    ["6203100", "Desenvolvimento e licenciamento de programas de computador não-customizáveis"],
    ["6204000", "Consultoria em tecnologia da informação"]
]

# Cria o DataFrame
df = pd.DataFrame(dados)

# Garante que a pasta existe
os.makedirs("data/raw", exist_ok=True)

# 1. Salva como CSV (Formato da Receita: sem header, separador ponto-e-vírgula, encoding latin-1)
csv_path = "data/raw/Cnaes.csv"
df.to_csv(csv_path, sep=";", index=False, header=False, encoding="latin-1")

# 2. Zipa o arquivo (A Receita entrega zipado)
zip_path = "data/raw/Cnaes.zip"
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    zipf.write(csv_path, arcname="Cnaes.csv")

# Remove o CSV solto para deixar só o Zip
os.remove(csv_path)

print(f"✅ Arquivo Mock criado com sucesso: {zip_path}")
print("Agora você pode rodar o pipeline!")
