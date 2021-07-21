# %%
# Cargar todos los resultados de la carpeta + los de postgres.
# Cargar la tabla desde el doc
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

import scripts  # noqa

# %%
tests_dir = Path("tests")
neo_tuning_test = tests_dir / "performance tuning neo4j"
pgsql_tests = tests_dir / "1 thread" / "pgsql" / "dijkstra"

# %%
all_tuning = list(neo_tuning_test.iterdir()) + list(pgsql_tests.iterdir())
all_tuning.sort()
all_tuning = all_tuning[3:] + all_tuning[:2]  # postgres para el final
# %%
all_dfs = [pd.read_csv(dir_) for dir_ in all_tuning if dir_.suffix == ".csv"]
# %%
times = [df["time"].sum() * 1000 for df in all_dfs]
# %%
# Tiempos por tipo de cache
# %%
labels = [
    "Neo4j (1h cache update)",
    "Neo4j (Strong)",
    "Neo4j (Big heap)",
    "Neo4j (Medium Heap)",
    "Neo4j (default)",
    "PostgreSQL",
]
cold_times = times[::2]
hot_times = times[1::2]

x = np.arange(len(labels))  # the label locations
width = 0.35  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - width / 2, cold_times, width, label="cold")
rects2 = ax.bar(x + width / 2, hot_times, width, label="hot")

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel("Tiempo (ms)")
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=45, ha="right")
ax.set_yticks(range(0, 350000, 50000))
ax.grid(axis="y")
ax.legend()
fig.tight_layout()
# %%
# Get all mems
algorithm = "astar"
mems = []
for i in tests_dir.glob("**/*.txt"):
    if algorithm in i.parent.name:
        with open(i, "r") as file:
            lines = file.readlines()
            tests, threads, infra, algo = str(i.parent).split("/")
            mems.append(
                (
                    int(threads.split()[0]),
                    infra,
                    int(lines[-1][lines[-1].find(": ") + 2 : -3]),
                )
            )

mems.sort()

# %%
# Memoria por threads

# %%
labels = [1, 2, 4, 8, 16]
neo_mems = [mem[-1] for mem in mems[::2]]
pgsql_mems = [mem[-1] for mem in mems[1::2]]

x = np.arange(len(labels))  # the label locations
width = 0.35  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - width / 2, neo_mems, width, label="Neo4j")
rects2 = ax.bar(x + width / 2, pgsql_mems, width, label="PostgreSQL")

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel("Memoria (MB)")
ax.set_xlabel("Cantidad de hilos concurrentes (N)")
ax.set_xticks(x)
ax.set_yticks(range(0, 7000, 500))
ax.set_xticklabels(labels)
ax.grid(axis="y")
ax.legend()
fig.tight_layout()
# %%
# Get all times
algorithm_name = "astar"
neo_cold = []
neo_hot = []
pg_cold = []
pg_hot = []
for threads in tests_dir.iterdir():
    if "thread" in threads.name:
        num_t = int(threads.name.split()[0])
        for infra in threads.iterdir():
            for algorithm in infra.iterdir():
                if algorithm.name == algorithm_name:
                    cold_times1 = [
                        pd.read_csv(dir_)["time"].sum()
                        for dir_ in algorithm.iterdir()
                        if dir_.suffix == ".csv" and "_cold" in dir_.name
                    ]
                    hot_times1 = [
                        pd.read_csv(dir_)["time"].sum()
                        for dir_ in algorithm.iterdir()
                        if dir_.suffix == ".csv" and "_hot" in dir_.name
                    ]
                    max_cold_time = max(cold_times1)
                    max_hot_time = max(hot_times1)
                    # print(cold_times, hot_times, infra.name, num_t)
                    neo_cold.append(
                        (num_t, max_cold_time)
                    ) if infra.name == "Neo4j" else pg_cold.append(
                        (num_t, max_cold_time)
                    )
                    neo_hot.append(
                        (num_t, max_hot_time)
                    ) if infra.name == "Neo4j" else pg_hot.append((num_t, max_hot_time))
# %%
neo_cold.sort()
neo_hot.sort()
pg_cold.sort()
pg_hot.sort()

# to millis
neo_cold = [time * 1000 for _, time in neo_cold]
neo_hot = [time * 1000 for _, time in neo_hot]
pg_cold = [time * 1000 for _, time in pg_cold]
pg_hot = [time * 1000 for _, time in pg_hot]
# %%
grid = [x for x in range(5)]
xticks = [2 ** i for i in range(len(grid))]
graphs = [
    ("Neo4j(cold)", neo_cold),
    ("Neo4j(hot)", neo_hot),
    ("PostgreSQL(cold)", pg_cold),
    ("PostgreSQL(hot)", pg_hot),
]

for gg, (label, graph) in enumerate(graphs):
    plt.plot(grid, graph, label=label)
plt.ylabel("Tiempo (ms)")
plt.xlabel("Cantidad de hilos concurrentes (N)")
plt.xticks(grid, labels=xticks)
plt.legend()
plt.yticks(range(30000, 300000, 50000))
plt.grid(axis="y")

# %%
