import csv
import datetime
import math
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
            self.mems.append(mem)
            sleep(5)

    def stop(self):
        self.running = False
        if self.mems:
            print(f"Max mem used: {max(self.mems)}MB")


class Profiler:
    def __init__(self, measure_mem=True, num_threads=1):
        self._load_node_pairs()
        self.pathfinder = None
        self.mem_tracker = DisplayMem() if measure_mem else None
        self.num_threads = num_threads

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
            self.pathfinder = PgSQLPathFinder(database="osm")
            # self.pathfinder = PgSQLPathFinder()

    def _run_pathfinder(
        self, algorithm, node_pairs, save_results=True, experiment_name=None
    ):
        start_time = time()

        results = []
        for source_gid, target_gid in node_pairs:

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

    def run_experiments(
        self, thread_id, pathfinder, experiment_name, algorithm, node_pairs
    ):
        """
        arguments:
        - pathfinder (str): Must be one of ['neo4j', 'pgsql'].
        - experiment_name (str): experiment identifier for csv files.
        - algorithm (str): Which algorithm to run on the pathfinder.
                Must be one of ['dijkstra', 'astar']
        """

        if self.pathfinder:
            print("Path finder already loaded :)")
        else:
            print(f"Loading pathfinder {pathfinder}")
            self._load_pathfinder(pathfinder)

        print(f"Thread {thread_id}: Start experiments")

        print(f"Thread {thread_id}: Run cold start queries")
        self._run_pathfinder(
            algorithm,
            node_pairs,
            experiment_name=f"{experiment_name}_thread{thread_id}_cold",
        )

        print(f"Thread {thread_id}: Run hot start queries")
        self._run_pathfinder(
            algorithm,
            node_pairs,
            experiment_name=f"{experiment_name}_thread{thread_id}_hot",
        )

    def run_threaded_experiment(
        self, pathfinder, experiment_name=None, algorithm="dijkstra"
    ):
        if not experiment_name:
            experiment_name = (
                f"{datetime.datetime.now():%y-%m-%d-%H%M}_{pathfinder}_{algorithm}"
            )

        if self.mem_tracker:
            self.mem_tracker.start()

        if self.num_threads == 1:
            self.run_experiments(
                0, pathfinder, f"{experiment_name}_thread0", algorithm, self.node_pairs
            )
        else:
            start_time = time()
            threads = []
            node_interval = math.ceil(len(self.node_pairs) / self.num_threads)
            for index in range(self.num_threads):
                print(f"Main    : create and start thread {index}.")
                thread_node_pairs = self.node_pairs[
                    node_interval * index : node_interval * (index + 1)
                ]
                x = threading.Thread(
                    target=self.run_experiments,
                    args=(
                        index,
                        pathfinder,
                        experiment_name,
                        algorithm,
                        thread_node_pairs,
                    ),
                )
                threads.append(x)
                x.start()

            for index, thread in enumerate(threads):
                print(f"Main    : before joining thread {index}.")
                thread.join()
                print(f"Main    : thread {index} done")

            elapsed_time = time() - start_time
            print(f"Finished running main thread. All tests took: {elapsed_time:.2f}s")

        if self.mem_tracker:
            self.mem_tracker.stop()
