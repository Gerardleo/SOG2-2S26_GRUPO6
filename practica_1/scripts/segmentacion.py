import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # backend sin interfaz gráfica: no abre ventanas
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 110

DIR_GRAFICAS = "../salida/graficas"
os.makedirs(DIR_GRAFICAS, exist_ok=True)

def ruta(nombre_archivo):
    return os.path.join(DIR_GRAFICAS, nombre_archivo)

df = pd.read_csv("../salida/venta_online_limpio.csv", parse_dates=["fecha_compra"])

df["genero_lbl"] = df["genero"].map({0: "Masculino", 1: "Femenino"})
df["metodo_pago_lbl"] = df["metodo_pago"].map({0: "Efectivo", 1: "Tarjeta de Crédito", 2: "Tarjeta de Débito"})
df["navegador_lbl"] = df["navegador"].map({0: "Tienda Física", 1: "Navegador 1", 2: "Navegador 2", 3: "Navegador 3", 4: "Navegador 4"})
df["boletin_lbl"] = df["boletin"].map({0: "No", 1: "Sí"})
df["vale_lbl"] = df["vale"].map({0: "No", 1: "Sí"})

print("Dimensiones del dataset:", df.shape)

# Segmentación por edad

bins = [18, 25, 35, 45, 60, 80]
labels = ["18-25", "26-35", "36-45", "46-60", "61-79"]
df["rango_edad"] = pd.cut(df["edad"], bins=bins, labels=labels, right=True, include_lowest=True)

resumen_edad = df.groupby("rango_edad", observed=True).agg(
    clientes=("id_cliente", "count"),
    venta_total_prom=("venta_total", "mean"),
    n_compras_prom=("n_compras", "mean"),
    monto_compra_prom=("monto_compra", "mean"),
).round(2)
print("\n--- Resumen por rango de edad ---")
print(resumen_edad)

fig1, ax1 = plt.subplots(figsize=(7, 5))
sns.boxplot(data=df, x="rango_edad", y="venta_total", order=labels, ax=ax1,
            hue="rango_edad", palette="Blues", legend=False)
ax1.set_title("Distribución de venta total por rango de edad")
ax1.set_xlabel("Rango de edad")
ax1.set_ylabel("Venta total")
plt.tight_layout()
plt.savefig(ruta("g1_segmentacion_edad_venta.png"), bbox_inches="tight")
plt.close(fig1)

fig2, ax2 = plt.subplots(figsize=(7, 5))
sns.barplot(data=resumen_edad.reset_index(), x="rango_edad", y="n_compras_prom", order=labels, ax=ax2,
            hue="rango_edad", palette="Greens", legend=False)
ax2.set_title("Número promedio de compras por rango de edad")
ax2.set_xlabel("Rango de edad")
ax2.set_ylabel("N° compras promedio")
plt.tight_layout()
plt.savefig(ruta("g2_segmentacion_edad_compras.png"), bbox_inches="tight")
plt.close(fig2)

# ## 4.b Comparación de comportamiento de compra entre géneros

resumen_genero = df.groupby("genero_lbl").agg(
    clientes=("id_cliente", "count"),
    venta_total_prom=("venta_total", "mean"),
    n_compras_prom=("n_compras", "mean"),
    monto_compra_prom=("monto_compra", "mean"),
    tiempo_prom_seg=("tiempo", "mean"),
).round(2)
print("\n--- Resumen por género ---")
print(resumen_genero)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

sns.barplot(data=resumen_genero.reset_index(), x="genero_lbl", y="venta_total_prom", ax=axes[0],
            hue="genero_lbl", palette="magma", legend=False)
axes[0].set_title("Venta total promedio por género")
axes[0].set_xlabel("")
axes[0].set_ylabel("Venta total promedio")

metodo_genero = pd.crosstab(df["genero_lbl"], df["metodo_pago_lbl"], normalize="index") * 100
metodo_genero.plot(kind="bar", stacked=True, ax=axes[1], colormap="viridis")
axes[1].set_title("Método de pago preferido por género (%)")
axes[1].set_xlabel("")
axes[1].set_ylabel("% de clientes")
axes[1].legend(title="Método de pago", bbox_to_anchor=(1.02, 1), loc="upper left")
axes[1].tick_params(axis="x", rotation=0)

plt.tight_layout()
plt.savefig(ruta("g3_segmentacion_genero.png"), bbox_inches="tight")
plt.close(fig)

# Segmentación por boletín y vale

resumen_boletin_vale = df.groupby(["boletin_lbl", "vale_lbl"]).agg(
    clientes=("id_cliente", "count"),
    venta_total_prom=("venta_total", "mean"),
    n_compras_prom=("n_compras", "mean"),
    monto_compra_prom=("monto_compra", "mean"),
).round(2)
print("\n--- Resumen por boletín y vale ---")
print(resumen_boletin_vale)

fig, ax = plt.subplots(figsize=(8, 5))
tabla_plot = resumen_boletin_vale.reset_index()
tabla_plot["segmento"] = tabla_plot["boletin_lbl"] + " boletín / " + tabla_plot["vale_lbl"] + " vale"

sns.barplot(data=tabla_plot, x="segmento", y="venta_total_prom", ax=ax,
            hue="segmento", palette="crest", legend=False)
ax.set_title("Venta total promedio por combinación de boletín y vale")
ax.set_xlabel("")
ax.set_ylabel("Venta total promedio")
plt.xticks(rotation=20, ha="right")
plt.tight_layout()
plt.savefig(ruta("g4_segmentacion_boletin_vale.png"), bbox_inches="tight")
plt.close(fig)

# Correlación entre venta total y edad del cliente

corr_edad, p_edad = stats.pearsonr(df["edad"], df["venta_total"])
print(f"Coeficiente de correlación de Pearson (edad vs venta_total): {corr_edad:.4f}")
print(f"Valor p: {p_edad:.4f}")

fig, ax = plt.subplots(figsize=(7, 5))
sns.regplot(data=df, x="edad", y="venta_total", scatter_kws={"alpha": 0.3, "s": 15}, line_kws={"color": "red"}, ax=ax)
ax.set_title(f"Relación entre edad y venta total (r = {corr_edad:.3f})")
ax.set_xlabel("Edad")
ax.set_ylabel("Venta total")
plt.tight_layout()
plt.savefig(ruta("g5_correlacion_edad_venta.png"), bbox_inches="tight")
plt.close(fig)

# Correlación entre género y método de pago preferido

tabla_contingencia_1 = pd.crosstab(df["genero_lbl"], df["metodo_pago_lbl"])
chi2_1, p_1, dof_1, expected_1 = stats.chi2_contingency(tabla_contingencia_1)

print("Tabla de contingencia (género vs método de pago):")
print(tabla_contingencia_1)
print(f"\nChi2 = {chi2_1:.4f} | grados de libertad = {dof_1} | valor p = {p_1:.4f}")

fig, ax = plt.subplots(figsize=(7, 5))
sns.heatmap(tabla_contingencia_1, annot=True, fmt="d", cmap="Purples", ax=ax)
ax.set_title("Género vs Método de pago (frecuencias observadas)")
plt.tight_layout()
plt.savefig(ruta("g6_correlacion_genero_metodopago.png"), bbox_inches="tight")
plt.close(fig)

# Correlación entre uso de boletín y uso de vale

tabla_contingencia_2 = pd.crosstab(df["boletin_lbl"], df["vale_lbl"])
chi2_2, p_2, dof_2, expected_2 = stats.chi2_contingency(tabla_contingencia_2)

print("Tabla de contingencia (boletín vs vale):")
print(tabla_contingencia_2)
print(f"\nChi2 = {chi2_2:.4f} | grados de libertad = {dof_2} | valor p = {p_2:.4f}")

fig, ax = plt.subplots(figsize=(6, 5))
sns.heatmap(tabla_contingencia_2, annot=True, fmt="d", cmap="Oranges", ax=ax)
ax.set_title("Boletín vs Vale (frecuencias observadas)")
plt.tight_layout()
plt.savefig(ruta("g7_correlacion_boletin_vale.png"), bbox_inches="tight")
plt.close(fig)

print(f"\nListo. Las 7 gráficas se guardaron en: {os.path.abspath(DIR_GRAFICAS)}")