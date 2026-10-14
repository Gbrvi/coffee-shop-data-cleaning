# coffee-shop-data-cleaning

Este repositório documenta o processo de auditoria, limpeza avançada, reconstrução lógica de dados e análise exploratória do dataset dirty_cafe_sales.csv.

O objetivo do projeto foi transformar uma base corrompida por falhas de registro de sistema em um conjunto de dados íntegro e extrair métricas de negócio para a gestão da cafeteria.

A estratégia adotada priorizou **regras de negócio determinísticas** e **deduções cruzadas**:

### 1. Padronização de Sentinelas e Tipagem
* Substituição global de strings sentinelas (`"UNKNOWN"`, `"ERROR"`) por `np.nan`.
* Conversão segura via `pd.to_numeric(..., errors='coerce')` para `Quantity`, `Price Per Unit` e `Total Spent`.
* Conversão temporal via `pd.to_datetime(..., errors='coerce')`.

### 2. Catálogo Fixo de Preços & Recuperação Reversa
Identificou-se que cada produto possui preço de tabela constante:
* `Cookie`: $1.00 | `Tea`: $1.50 | `Coffee`: $2.00 | `Cake`: $3.00 | `Juice`: $3.00 | `Sandwich`: $4.00 | `Smoothie`: $4.00 | `Salad`: $5.00.
* **Preenchimento direto:** Preços nulos com `Item` conhecido receberam o valor do catálogo.
* **Recuperação Reversa:** Registros com `Item` nulo, mas com preços unívocos ($1.0, $1.5, $2.0 e $5.0), tiveram o nome do produto reconstruído com precisão matemática (mais de 480 registros recuperados).

### 4. Particionamento Temporal
* Linhas sem data foram preservadas para cálculos de faturamento global, mas descartadas na criação do subset temporal (`df_tempo`), garantindo séries temporais limpas e sem sazonalidade artificial.

---

## 📊 Análises Exploratórias & Insights de Negócio

### 1. Curva ABC / Princípio de Pareto
Categorização dos produtos de acordo com o impacto financeiro:
* **Classe A (até 70% da receita):** `Salad` (22,74%), `Sandwich` (16,34%), `Smoothie` (15,89%), `Juice` (12,52%).
* **Classe B (70% a 90% da receita):** `Cake` (12,39%), `Coffee` (9,30%).
* **Classe C (90% a 100% da receita):** `Tea` (6,52%), `Cookie` (4,29%).

> **Insight:** O café é o item mais vendido em volume (3.904 unidades), mas ocupa apenas o 6º lugar em receita ($7.808,00). O carro chefe da cafeteria é a salada ($19.095,00).  
> **Recomendação:** Implementação de estratégias de *cross-selling* com combos promocionais (ex.: Café + Sanduíche) para alavancar produtos de maior margem a partir do alto giro do café.

---

### 2. Sazonalidade & Comportamento Semanal
Análise da distribuição de pedidos e ticket médio por dia da semana (ordenados cronologicamente de segunda a domingo):

| Dia da Semana | Pedidos | Faturamento Total ($) | Ticket Médio ($) |
| :--- | :---: | :---: | :---: |
| Segunda-feira | 1.382 | 12.140,00 | 8,80 |
| Terça-feira | 1.311 | 12.039,50 | **9,20** |
| Quarta-feira | 1.341 | 11.680,50 | 8,72 |
| Quinta-feira | 1.380 | 12.401,50 | 9,01 |
| Sexta-feira | 1.388 | 12.334,00 | 8,92 |
| Sábado | 1.358 | 12.039,50 | 8,89 |
| Domingo | 1.380 | 12.287,50 | 8,92 |

> **Insight:** Volume de transações ao longo de toda a semana (~1.350 pedidos/dia). A terça-feira registrou o menor volume de pedidos, porém o maior ticket médio ($9,20). A quarta-feira representa o ponto de menor performance semanal em receita e ticket médio.

---

## 💻 Tecnologias Utilizadas

* **Python 3.10+**
* **Pandas:** Limpeza, transformação, interpolação lógica e agregações relacionais.
* **NumPy:** Vetorização e manipulação de valores nulos.
* **Matplotlib:** Construção de gráficos de Pareto (eixo duplo), séries temporais e boxplots analíticos.
