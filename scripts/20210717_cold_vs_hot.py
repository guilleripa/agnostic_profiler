# %%
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

# %%
algorithm = "astar"
tests_dir = Path("tests")
neo_tests = tests_dir / "1 thread" / "Neo4j" / algorithm
pgsql_tests = tests_dir / "1 thread" / "pgsql" / algorithm

# %%
df_pg_cold = pd.read_csv(next(pgsql_tests.glob("*_cold.csv")))
df_pg_hot = pd.read_csv(next(pgsql_tests.glob("*_hot.csv")))
df_neo_cold = pd.read_csv(next(neo_tests.glob("*_cold.csv")))
df_neo_hot = pd.read_csv(next(neo_tests.glob("*_hot.csv")))

df_pg_cold["time"] *= 1000
df_pg_hot["time"] *= 1000
df_neo_cold["time"] *= 1000
df_neo_hot["time"] *= 1000
# %%
figure, axes = plt.subplots(1, 2, figsize=(15, 5))

slice_ = slice(0, 20)
df_neo_cold["time"][slice_].plot.line(ax=axes[0], label="Neo4j")
df_pg_cold["time"][slice_].plot.line(ax=axes[0], label="PostgreSQL")
axes[0].set_title("BD en frío")
axes[0].xaxis.set_ticks(range(0, 20))
axes[0].yaxis.set_ticks(range(0, 4600, 500))
axes[0].set_xlabel("Pedidos (N)")
axes[0].set_ylabel("Tiempo (s)")
axes[0].legend(loc="upper right")


df_neo_hot["time"][slice_].plot.line(ax=axes[1], label="Neo4j")
df_pg_hot["time"][slice_].plot.line(ax=axes[1], label="PostgreSQL")
axes[1].set_title("BD en caliente")
axes[1].xaxis.set_ticks(range(0, 20))
axes[1].yaxis.set_ticks(range(0, 4600, 500))
axes[1].set_xlabel("Pedidos (N)")
axes[1].set_ylabel("Tiempo (ms)")
axes[1].legend(loc="upper right")
figure.tight_layout()

# %%
