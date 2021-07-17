# %%
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

# %%
df_pg_cold = pd.read_csv("results/21-07-16-1901_pgsql_dijkstra_cold.csv")
df_pg_hot = pd.read_csv("results/21-07-16-1901_pgsql_dijkstra_hot.csv")
df_neo_cold = pd.read_csv("results/21-07-16-1849_neo4j_dijkstra_cold.csv")
df_neo_hot = pd.read_csv("results/21-07-16-1849_neo4j_dijkstra_hot.csv")

# %%
figure, axes = plt.subplots(1, 2, figsize=(15, 5))

slice_ = slice(0, 19)
df_pg_cold["time"][slice_].plot.line(ax=axes[0], label="pgsql")
df_neo_cold["time"][slice_].plot.line(ax=axes[0], label="neo4j")
axes[0].xaxis.set_ticks(range(1, 20))
axes[0].yaxis.set_ticks(range(10))
axes[0].set_xlabel("Pedidos (N)")
axes[0].set_ylabel("Tiempo (s)")
axes[0].legend(loc="upper right")


df_pg_hot["time"][slice_].plot.line(ax=axes[1], label="pgsql")
df_neo_hot["time"][slice_].plot.line(ax=axes[1], label="neo4j")
axes[1].xaxis.set_ticks(range(1, 20))
axes[1].yaxis.set_ticks(range(10))
axes[1].set_xlabel("Pedidos (N)")
axes[1].set_ylabel("Tiempo (s)")
axes[1].legend(loc="upper right")

# %%
