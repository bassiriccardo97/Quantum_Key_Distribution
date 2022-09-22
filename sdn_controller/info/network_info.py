import logging
from os import environ
from uuid import UUID

import networkx as nx
from fastapi import HTTPException
from networkx import NetworkXNoPath

from sdn_controller.configs import Config

G = nx.Graph()
all_paths = dict()


def add_kme_in_network(kme_id: UUID) -> None:
    """Adds a KME as a node in the network graph."""
    G.add_node(kme_id)


def add_link_in_network(kme1: UUID, kme2: UUID, rate: float) -> None:
    """Adds a link between two KMEs as an edge in the network graph."""
    global all_paths
    spare_bytes = []
    for _ in range(Config.TTL - 1):
        spare_bytes.append(0)
    spare_bytes.append(rate)
    G.add_edge(kme1, kme2, rate=round(rate, 2), used_rate=0.0, spare_bytes=spare_bytes)
    if len(G.edges) == Config.N_KME:
        all_paths = dict(nx.all_pairs_shortest_path(G))
        # print_graph()


def get_shortest_path(kme_src: UUID, kme_dst: UUID) -> list[UUID]:
    """Gets the shortest path between two KMEs in the network graph."""
    global all_paths
    try:
        l: list[UUID] = all_paths[kme_src][kme_dst]
    except KeyError:  # NetworkXNoPath:
        raise HTTPException(
            status_code=400,
            detail="No path for the connection required"
        )
    return l


def get_path(kme_src: UUID, kme_dst: UUID, req_rate: float) -> list[UUID]:
    """Gets the shortest path that satisfies the requested rate in the network graph."""
    path: list[UUID] = get_shortest_path(kme_src, kme_dst)
    for i in range(0, len(path) - 1):
        spare_bytes = sum(G[path[i]][path[i + 1]]["spare_bytes"])
        # rate = G[path[i]][path[i + 1]]["rate"]
        used_rate = G[path[i]][path[i + 1]]["used_rate"]
        temp_rate: float = req_rate
        if len(path) > 2 and i == 0:
            if environ.get("qkp") == "yes":
                # the first KME generates FUTURE_KEYS + 1 keys, while the others only one encryption key
                temp_rate += req_rate / Config.KEYS_AHEAD
            else:
                temp_rate += req_rate
        if environ.get("ref") == "yes" and not __satisfiable_request(req_rate=round(temp_rate, 2), rate=spare_bytes, used_rate=used_rate):
            # print_graph()
            return []
    return path


def __satisfiable_request(req_rate: float, rate: float, used_rate: float) -> bool:
    """Checks if the free rate on a link is sufficient for the requested rate."""
    available_rate = rate - used_rate
    # logging.getLogger().warning(f"QC rate = {rate}, Used rate = {used_rate}, Req rate = {req_rate} [{available_rate >= req_rate}]")
    return available_rate >= req_rate


def use_rate_in_path(nodes: list[UUID], rate: float) -> None:
    """Adds the new requested rate to the used rate of a link."""
    for i in range(0, len(nodes) - 1):
        temp_rate = round(rate, 2)
        if i == 0:
            if environ.get("qkp") == "yes":
                # the first KME generates FUTURE_KEYS + 1 keys, while the others only one encryption key
                temp_rate += rate / Config.KEYS_AHEAD
            else:
                temp_rate += rate
        G[nodes[i]][nodes[i + 1]]["used_rate"] += round(temp_rate, 2)
        G[nodes[i]][nodes[i + 1]]["used_rate"] = round(G[nodes[i]][nodes[i + 1]]["used_rate"], 2)
    # print_graph()


def free_rate_in_path(nodes: list[UUID], rate: float) -> None:
    """Subtracts the freed rate from the used rate of a link."""
    for i in range(0, len(nodes) - 1):
        temp_rate = rate
        if i == 0:
            if environ.get("qkp") == "yes":
                temp_rate += rate / Config.KEYS_AHEAD
            else:
                temp_rate += rate
        if G[nodes[i]][nodes[i + 1]]["used_rate"] - temp_rate < 0:
            G[nodes[i]][nodes[i + 1]]["used_rate"] = 0.0
        else:
            G[nodes[i]][nodes[i + 1]]["used_rate"] -= temp_rate
        G[nodes[i]][nodes[i + 1]]["used_rate"] = round(G[nodes[i]][nodes[i + 1]]["used_rate"], 2)
    # print_graph()


def update_rate(kmes: tuple[UUID, UUID], new_rate: float) -> None:
    G[kmes[0]][kmes[1]]["rate"] = round(new_rate, 2)
    G[kmes[0]][kmes[1]]["spare_bytes"].pop(0)
    G[kmes[0]][kmes[1]]["spare_bytes"].append(new_rate)
    used_rate = G[kmes[0]][kmes[1]]["used_rate"]
    stop = False
    while not stop:
        for i in range(Config.TTL):
            spare = G[kmes[0]][kmes[1]]["spare_bytes"][-i + 1]
            if spare >= used_rate:
                G[kmes[0]][kmes[1]]["spare_bytes"][-i + 1] -= used_rate
                used_rate -= used_rate
            else:
                G[kmes[0]][kmes[1]]["spare_bytes"][-i + 1] = 0
                used_rate -= spare
            if used_rate == 0 or i == Config.TTL - 1:
                stop = True
    # print_graph()


def print_graph() -> None:
    for e in G.edges:
        logging.getLogger().warning(
            f"\n{e}"
            f"\n\tRate = {G[e[0]][e[1]]['rate']}, Used Rate = {G[e[0]][e[1]]['used_rate']}"
            f"\n\t\tRate = {G[e[1]][e[0]]['rate']}, Used Rate = {G[e[1]][e[0]]['used_rate']}"
        )
