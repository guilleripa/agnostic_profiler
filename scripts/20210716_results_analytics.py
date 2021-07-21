# %%
import ast
import math
from pathlib import Path

import neo4j
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

# %%
df_pgsql = pd.read_csv("tests/1 thread/pgsql/dijkstra/pgsql_dijkstra_thread0_cold.csv")
df_neo4j = pd.read_csv(
    "tests/1 thread/Neo4j/dijkstra/21-07-18-0423_neo4j_dijkstra_thread0_thread0_cold_old.csv"
)
# %%
df_pgsql["result"] = df_pgsql["result"].apply(ast.literal_eval)
# %%
# Paths with no route
(df_pgsql["result"].str.len() == 0).sum()

# %%
# Mock Neo4j para evaluar el str a un dict.
class POINT:
    def __init__(self, *args):
        self.args = args


# %%
def custom_eval(source):
    tree = ast.parse(source, mode="eval")

    # compile the ast into a code object
    clause = compile(tree, "<AST>", "eval")

    # make the globals contain only the POINT class,
    # and eval the compiled object
    result = eval(clause)
    return result["j"] if "j" in result.keys() else result


# %%
df_neo4j["result"] = df_neo4j["result"].apply(custom_eval)
# %%
neo4j_pathless = set(df_neo4j["result"][df_neo4j["result"].apply(type) == dict].index)
pgsql_pathless = set(df_pgsql["result"][df_pgsql["result"].str.len() == 0].index)
# %%
neo4j_pathless.intersection(pgsql_pathless) == neo4j_pathless
# %% [markdown]
# Conclusión, los caminos sin path de neo son un subconjunto de los de pgsql (usando node_pairs.csv)
# %%
df_pgsql["num_nodes"] = df_pgsql["result"].str.len()
# %%
interval = 100
bins = math.floor(df_pgsql["num_nodes"].max() / interval)
bins = range(0, (bins + 1) * interval, interval)
ax = df_pgsql["num_nodes"].plot.hist(bins=bins)
ax.xaxis.set_ticks(bins)
ax.set_xlabel("Cantidad de nodos en el camino")
ax.set_ylabel("Frecuencia")
ax.grid(axis="x")
ax.set_xticklabels(bins, rotation=45, ha="right")


# %%
set(np.array(df_pgsql["result"][0], dtype=int).T[3].tolist())
# %%
# %%
todo = []
for lista in df_pgsql["result"]:
    todo += lista
chan = set(np.array(todo, dtype=int).T[3].tolist())
# %%
tuple(chan)
# %%
from pgsql_pathfinder import PgSQLPathFinder

pgsql = PgSQLPathFinder()
# %%
with pgsql.conn.cursor() as cur:
    cur.execute(f"select gid, length_m from ways where gid in {tuple(chan)}")
    rs = cur.fetchall()
# %%
edge_distance = {}
for edge, distance in rs:
    edge_distance[edge] = distance
# %%
all_distances = df_pgsql["result"].apply(
    lambda x: sum([edge_distance.get(y[3], 0) for y in x]) if len(x) > 0 else 0
)
# %%
km_distances = all_distances[all_distances > 0] / 1000
interval = 50
bins = math.floor(km_distances.max() / interval)
bins = range(0, (bins + 1) * interval, interval)
ax = km_distances.plot.hist(bins=bins)
ax.xaxis.set_ticks(bins)
ax.set_xlabel("Largo (Km) del camino")
ax.set_ylabel("Frecuencia")
ax.grid(axis="x")
ax.set_xticklabels(bins, rotation=45, ha="right")
# %%
df_pgsql["distance"] = all_distances
# %%
df_pgsql.plot.scatter(x="distance", y="time")
plt.xlabel("Distancia del camino (m)")
plt.ylabel("Tiempo de resolución camino más corto (s)")
# %%
df_pgsql.plot.scatter(x="num_nodes", y="time")
# %%
df_pgsql.plot.scatter(x="num_nodes", y="distance")
plt.ylabel("Distancia del camino (km)")
plt.xlabel("Cantidad de nodos del camino (N)")
# %%
import pyarrow as pa

schema = pa.schema([pa.field("result", pa.list_(pa.tuple()))])
df_pgsql.to_parquet("results/df_pgsql_processed.pq", schema=schema)
# %%

# %%
dijkstra_neo_hot = pd.read_csv(
    next(Path("tests/1 thread/Neo4j/dijkstra").glob("*_hot.csv"))
)
dijkstra_pgsql_hot = pd.read_csv(
    next(Path("tests/1 thread/pgsql/dijkstra").glob("*_hot.csv"))
)
astar_neo_hot = pd.read_csv(next(Path("tests/1 thread/Neo4j/astar").glob("*_hot.csv")))
astar_pgsql_hot = pd.read_csv(
    next(Path("tests/1 thread/pgsql/astar").glob("*_hot.csv"))
)
# %%
dijkstra_neo_hot["result"] = dijkstra_neo_hot["result"].apply(custom_eval)
dijkstra_pgsql_hot["result"] = dijkstra_pgsql_hot["result"].apply(ast.literal_eval)
astar_pgsql_hot["result"] = astar_pgsql_hot["result"].apply(ast.literal_eval)
astar_neo_hot["result"] = astar_neo_hot["result"].apply(custom_eval)

# %%
dijkstra_neo_hot["num_nodes"] = dijkstra_neo_hot["result"].str.len()
dijkstra_pgsql_hot["num_nodes"] = dijkstra_pgsql_hot["result"].str.len()
astar_pgsql_hot["num_nodes"] = astar_pgsql_hot["result"].str.len()
astar_neo_hot["num_nodes"] = astar_neo_hot["result"].str.len()

# %%
