import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('Venta_online_c.csv', sep=';')
df['FechaCompra'] = pd.to_datetime(df['FechaCompra'], format='%d.%m.%y', errors='coerce')
df['Mes'] = df['FechaCompra'].dt.month

numeric_cols = ['Edad', 'Venta_total', 'N_Compras', 'MontoCompra', 'Tiempo']
stats = df[numeric_cols].agg(['mean', 'median', lambda x: x.mode()[0]]).T
stats.columns = ['Media', 'Mediana', 'Moda']
print("--- Estadísticas Descriptivas ---")
print(stats.round(2))

fig, axes = plt.subplots(2, 2, figsize=(12, 10))

df.groupby('Mes').size().plot(kind='bar', ax=axes[0, 0], color='skyblue')
axes[0, 0].set_title('Ventas por Mes')
axes[0, 0].set_ylabel('Cantidad')

df['MetodoPago'].value_counts().plot(kind='pie', ax=axes[0, 1], autopct='%1.1f%%')
axes[0, 1].set_title('Distribución por Método de Pago')
axes[0, 1].set_ylabel('')

df['Navegador'].value_counts().sort_index().plot(kind='bar', ax=axes[1, 0], color='lightgreen')
axes[1, 0].set_title('Uso por Navegador / Tienda Física')

df[['Boletin', 'Vale']].sum().plot(kind='bar', ax=axes[1, 1], color=['orange', 'purple'])
axes[1, 1].set_title('Total de Boletines y Vales Usados')

plt.tight_layout()
plt.savefig('graficos_tendencias.png')
print("\nGráficos generados exitosamente en 'graficos_tendencias.png'")