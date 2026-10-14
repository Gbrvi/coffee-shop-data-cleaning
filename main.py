# %% 
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# -----------------LIMPEZA DE DADOS--------------------------
# %% 1- Leitura dos dados 
df = pd.read_csv("archive/dirty_cafe_sales.csv")


# %% 2-=--=-=-=- Padronização dados -=-=-=--=-=-=
# Substitui ERROR e UNKNOWN por NAN
df = df.replace(["UNKNOWN", "ERROR"], np.nan)

# Converter colunas numericas
numeric_columns = ["Quantity", "Price Per Unit", "Total Spent"]
df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors="coerce")

# Converter coluna de datas

df["Transaction Date"] = pd.to_datetime(df["Transaction Date"], errors="coerce")

# %% Lógica de preços e itens

price_catalog = {
    "Cookie": 1.0,
    "Tea": 1.5,
    "Coffee": 2.0,
    "Cake": 3.0,
    "Juice": 3.0,
    "Sandwich": 4.0,
    "Smoothie": 4.0,
    "Salad": 5.0,
}

df["Price Per Unit"] = df['Price Per Unit'].fillna(df['Item'].map(price_catalog))

# Dedução reversa - preços unívocos permitem recuperar o Item
reverse_item_catalog = {1.0: "Cookie", 1.5: "Tea", 2.0: "Coffee", 5.0: "Salad"}
mask_item_na = df["Item"].isna()
df.loc[mask_item_na, "Item"] = df.loc[mask_item_na, "Price Per Unit"].map(
    reverse_item_catalog
)

df["Price Per Unit"] = df["Price Per Unit"].fillna(df['Total Spent'] / df['Quantity'])

df["Item"] = df["Item"].fillna("UNKNOWN")

df['Quantity'] = df['Quantity'].fillna(df['Total Spent'] / df['Price Per Unit'])

df['Total Spent'] = df['Total Spent'].fillna(df['Quantity'] * df['Price Per Unit'])

# %% 4- Tratamento Location e Payment NULLOS para UNKNOWN

df['Payment Method'] = df['Payment Method'].fillna("UNKNOWN")

df['Location'] = df['Location'].fillna("UNKNOWN")
# %%

df.isna().sum()

# Analise temporal 

df_tempo = df.dropna(subset=["Transaction Date"]).copy()

df_tempo['Mes'] = df_tempo['Transaction Date'].dt.month

# TOTAL GANHO NO MES
vendas_mensal = (
    df_tempo.groupby("Mes", as_index=False)['Total Spent']
    .sum()
)


# -----------------------------------ANALISE DOS DADOS----------------------------------
# 

#%% VISUALIZAÇÃO DOS DADOS 

#1-LUCRO MENSAL
#
plt.figure(figsize=(10,6))

plt.bar(
    vendas_mensal['Mes'],
    vendas_mensal['Total Spent'],
    color='#8B4513',
    edgecolor="black",
)

plt.title("Faturamento Mensal 2023", fontsize=14, fontweight="bold")
plt.xlabel("Meses")
plt.ylabel("Faturamento")
plt.xticks(ticks=range(1,13))
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.show()
# %%

#2 - ITENS MAIS VENDIDOS

# QUAIS ITENS MAIS VENDIDOS ANO INTEIRO
itens_mais_vendidos = (
    df_tempo.groupby("Item", as_index=False)['Quantity']
    .sum()
)
# %%

plt.barh(
    itens_mais_vendidos['Item'],
    itens_mais_vendidos['Quantity'],
    color='red',
    edgecolor="black",
)

plt.title("ITENS MAIS VENDIDOS EM 2023", fontsize=14, fontweight='bold')
plt.xlabel("Itens")
plt.ylabel("Quantidade")
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()


# %%

# QUANTIDADE VS RECEITA 

df_produtos = df[df["Item"] != "UNKNOWN"].copy()

curva_abc = (
df_produtos.groupby("Item", as_index=False).agg(
        Quantidade=("Quantity", "sum"),
        Receita=("Total Spent", "sum")
    )
)


curva_abc = curva_abc.sort_values(by="Receita", ascending=False).reset_index(drop=True)

total_receita = curva_abc['Receita'].sum()

curva_abc['% Receita'] = (curva_abc["Receita"] / total_receita) * 100
curva_abc["% Acumulado"] = curva_abc["% Receita"].cumsum()

def definir_classe(acumulado):
    if(acumulado <= 70):
        return "A"
    elif acumulado <= 90:
        return "B"
    return "C"

curva_abc["Classe"] = curva_abc["% Acumulado"].apply(definir_classe)

curva_abc

fig, ax1 = plt.subplots(figsize=(10, 6))

cor_barras = "#4A708B"
ax1.bar(curva_abc["Item"], curva_abc["Receita"], color=cor_barras, edgecolor="black", alpha=0.85, label="Receita ($)")
ax1.set_xlabel("Item do Menu", fontsize=12, labelpad=10)
ax1.set_ylabel("Receita Total ($)", fontsize=12, color=cor_barras)
ax1.tick_params(axis="y", labelcolor=cor_barras)

# Eixo secundário partilhado
ax2 = ax1.twinx()
ax2.plot(curva_abc["Item"], curva_abc["% Acumulado"], color="#CD3333", marker="o", linewidth=2.5, label="% Acumulado")
ax2.set_ylabel("Percentagem Acumulada (%)", fontsize=12, color="#CD3333")
ax2.tick_params(axis="y", labelcolor="#CD3333")
ax2.set_ylim(0, 105)
ax2.axhline(80, color="gray", linestyle="--", alpha=0.7)

plt.title("Curva de Pareto / Análise ABC de Produtos", fontsize=14, fontweight="bold", pad=15)
fig.tight_layout()
plt.show()
# %%


# ------------------------- %% COMPORTAMENTO SAZONALIDADE DIARIA
df_tempo['Dia'] = df_tempo['Transaction Date'].dt.day_name()
df_tempo['Dia_num'] = df_tempo['Transaction Date'].dt.dayofweek


df_diario = (
        df_tempo.groupby(['Dia', 'Dia_num'], as_index=False).agg(
            Pedidos=("Transaction ID", "count"),
            Quantidade=("Quantity", "sum"),
            Faturamento=("Total Spent", "sum"),
            Ticket_medio=("Total Spent", "mean")
        ).sort_values(by="Dia_num")
        .reset_index(drop=True)
)

# 4. Gráfico de Faturamento vs. Ticket Médio
fig, ax1 = plt.subplots(figsize=(10, 5))

cor_barra = "#2E8B57"
ax1.bar(
    df_diario["Dia"],
    df_diario["Faturamento"],
    color=cor_barra,
    alpha=0.8,
    edgecolor="black",
    width=0.55,
)
ax1.set_ylabel("Faturamento Total ($)", fontsize=11, color=cor_barra)
ax1.tick_params(axis="y", labelcolor=cor_barra)
ax1.set_ylim(10000, 13500)
plt.xticks(rotation=20)

# Eixo secundário para o Ticket Médio
ax2 = ax1.twinx()
cor_linha = "#E65100"
ax2.plot(
    df_diario["Dia"],
    df_diario["Ticket_medio"],
    color=cor_linha,
    marker="o",
    linewidth=2.5,
)
ax2.set_ylabel("Ticket Médio ($)", fontsize=11, color=cor_linha)
ax2.tick_params(axis="y", labelcolor=cor_linha)
ax2.set_ylim(8.0, 9.8)

plt.title(
    "Comportamento Semanal: Faturamento vs. Ticket Médio",
    fontsize=13,
    fontweight="bold",
    pad=12,
)
fig.tight_layout()
plt.show()

# %%
