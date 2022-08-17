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
    G.add_edge(kme1, kme2, rate=rate, used_rate=0.0)
    if len(G.edges) == Config.N_LINKS:
        all_paths = dict(nx.all_pairs_shortest_path(G))


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
        rate = G[path[i]][path[i + 1]]["rate"]
        used_rate = G[path[i]][path[i + 1]]["used_rate"]
        temp_rate: float = req_rate
        if environ.get("qkp") == "yes" and len(path) > 2 and i == 0:
            # the first KME generates FUTURE_KEYS + 1 keys, while the others only one encryption key
            temp_rate += req_rate * Config.KEYS_AHEAD
        if not __satisfiable_request(req_rate=temp_rate, rate=rate, used_rate=used_rate):
            raise HTTPException(
                status_code=500,
                detail="Insufficient rate for the connection required"
            )
    return path


def __satisfiable_request(req_rate: float, rate: float, used_rate: float) -> bool:
    """Checks if the free rate on a link is sufficient for the requested rate."""
    available_rate = rate - used_rate
    return available_rate >= req_rate


def use_rate_in_path(nodes: list[UUID], rate: float) -> None:
    """Adds the new requested rate to the used rate of a link."""
    for i in range(0, len(nodes) - 1):
        G[nodes[i]][nodes[i + 1]]["used_rate"] += rate


def free_rate_in_path(nodes: list[UUID], rate: float) -> None:
    """Subtracts the freed rate from the used rate of a link."""
    for i in range(0, len(nodes) - 1):
        G[nodes[i]][nodes[i + 1]]["used_rate"] -= rate


def update_rate(kmes: tuple[UUID, UUID], new_rate: float) -> None:
    G[kmes[0]][kmes[1]]["rate"] = new_rate
