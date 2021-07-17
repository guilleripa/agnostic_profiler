import csv
import datetime
import threading
from time import sleep, time

import psutil

from neo4j_pathfinder import Neo4jPathFinder
from pgsql_pathfinder import PgSQLPathFinder


class DisplayMem(threading.Thread):
    def run(self):

        self.running = True

        self.mems = []
        while self.running:
            mem = psutil.virtual_memory().used >> 20
            print(f"Total memory in use: {mem}MB")
            self.mems.append(mem)
            sleep(5)

    def stop(self):
        self.running = False
        if self.mems:
            print(f"Max mem used: {max(self.mems)}MB")


class Profiler:
    def __init__(self, measure_mem=True):
        self._load_node_pairs()
        self.pathfinder = None
        self.mem_tracker = DisplayMem() if measure_mem else None

    def _load_node_pairs(self):
        self.node_pairs = []
        with open("node_pairs.csv") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=",")
            for source_gid, target_gid in csv_reader:
                self.node_pairs.append((int(source_gid), int(target_gid)))

    def _load_pathfinder(self, pathfinder):
        if pathfinder == "neo4j":
            self.pathfinder = Neo4jPathFinder()
        else:
            # self.pathfinder = PgSQLPathFinder(database="osm")
            self.pathfinder = PgSQLPathFinder()

    def _run_pathfinder(self, algorithm, save_results=True, experiment_name=None):
        start_time = time()

        results = []
        for source_gid, target_gid in self.node_pairs:

            path_start_time = time()
            result = self.pathfinder.get_path(
                source_gid, target_gid, algorithm=algorithm
            )
            path_elapsed_time = time() - path_start_time

            res_dict = {
                "source_gid": source_gid,
                "target_gid": target_gid,
                "time": path_elapsed_time,
            }
            if save_results:
                res_dict["result"] = result
            results.append(res_dict)

        elapsed_time = time() - start_time
        if save_results:
            self._save_results(results, experiment_name)

        print(f"Finished running {experiment_name}. Test took: {elapsed_time:.2f}s")

        return elapsed_time, results

    def _save_results(self, results, experiment_name):
        csv_columns = results[0].keys()
        try:
            with open(f"{experiment_name}.csv", "w+") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
                writer.writeheader()
                for path in results:
                    writer.writerow(path)
        except IOError:
            print(f"Error while saving csv file for experiment={experiment_name}")

    def run_experiments(self, pathfinder, experiment_name=None, algorithm="dijkstra"):
        """
        arguments:
        - pathfinder (str): Must be one of ['neo4j', 'pgsql'].
        - experiment_name (str): experiment identifier for csv files.
        - algorithm (str): Which algorithm to run on the pathfinder.
                Must be one of ['dijkstra', 'astar']
        """

        if not experiment_name:
            experiment_name = (
                f"{datetime.datetime.now():%y-%m-%d-%H%M}_{pathfinder}_{algorithm}"
            )

        if self.pathfinder:
            print("Path finder already loaded :)")
        else:
            print(f"Loading pathfinder {pathfinder}")
            self._load_pathfinder(pathfinder)

        print("Start experiments")

        if self.mem_tracker:
            self.mem_tracker.start()

        print("Run cold start queries")
        self._run_pathfinder(algorithm, experiment_name=f"{experiment_name}_cold")

        print("Run hot start queries")
        self._run_pathfinder(algorithm, experiment_name=f"{experiment_name}_hot")

        if self.mem_tracker:
            self.mem_tracker.stop()
