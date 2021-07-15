# %%
import csv
import random

with open("total_nodes.csv") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=",")
    nodes = list(csv_reader)[1:]
# %%
nodes
# %%
selected_nodes = random.sample(nodes, 190 * 2)
sources = selected_nodes[:190]
targets = selected_nodes[190:]
print(len(sources), len(targets), len(nodes))
# %%
node_pairs = zip(sources, targets)
# %%
final_node_pairs = []
for source, target in node_pairs:
    final_node_pairs.append({"source": source[0], "target": target[0]})
# %%
print(final_node_pairs)
# %%
with open(f"node_pairs.csv", "w+") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=["source", "target"])
    for path in final_node_pairs:
        writer.writerow(path)

# %%
