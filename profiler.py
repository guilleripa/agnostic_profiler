# Que queremos hacer???
# mirar laos experimentos del paper
# 1. [x] cargar los 190 pares de puntos
# 2. [x] correr las queries y guardar los datos en formato csv.
#   2.1. se corren dos veces, la primera se guardan como cold times y la segunda como hot
# 3. Había algunos experimentos de Neo4j weak-strong-heavy algo así, ver que son esas para dejar esas opciones

import csv
import time

from neo4j_pathfinder import Neo4jPathFinder
from pgsql_pathfinder import PgSQLPathFinder


class Profiler:
    def __init__(
        self,
    ):
        self._load_node_pairs()
        self.pathfinder = None

    def _load_node_pairs(self):
        with open("node_pairs.csv") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            self.node_pairs = list(csv_reader)

    def _load_pathfinder(self, pathfinder):
        if pathfinder == "neo4j":
            self.pathfinder = Neo4jPathFinder()
        else:
            self.pathfinder = PgSQLPathFinder(database="osm")

    def _run_pathfinder(self, save_results=True):
        start_time = time()

        results = {}
        for source_gid, target_gid in self.node_pairs:
            result_name = f"{source_gid}-{target_gid}"

            path_start_time = time()
            result = self.pathfinder.get_path(source_gid, target_gid)
            path_elapsed_time = time() - path_start_time
            results[result_name] = (
                (path_elapsed_time, result) if save_results else path_elapsed_time
            )

        elapsed_time = time() - start_time

        return elapsed_time, results

    def run_experiments(self, pathfinder):
        """
        arguments:
        - pathfinder (str): Must be one of ['neo4j', 'pgsql'].
        """

        if self.pathfinder:
            print("Path finder already loaded :)")
        else:
            print(f"Loading pathfinder {pathfinder}")
            self._load_pathfinder(pathfinder)

        print("Start experiments")

        print("Run cold start queries")
        cold_elapsed_time, cold_results = self._run_pathfinder()
        print(f"Finished running cold start tests: {cold_elapsed_time:.2f}s")

        print("Run hot start queries")
        hot_elapsed_time, hot_results = self._run_pathfinder()
        print(f"Finished running hot start tests: {hot_elapsed_time:.2f}s")

        # Falta:
        # 1. guardar los resultados a un csv
        # 2. Agregar las opciones para los diferentes tipos de experimentos
        # 3. trackear el uso de memoria
        # 4. guardar todos los resultados de los exprimentos a otro csv
