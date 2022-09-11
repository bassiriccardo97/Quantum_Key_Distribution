import datetime
from datetime import timedelta
from os import environ
from statistics import mean


def get_timedelta(string: str) -> timedelta:
    temp = string.split(",")
    temp1 = temp[0].split(":") + [temp[1]]
    return timedelta(hours=int(temp1[0]), minutes=int(temp1[1]), seconds=int(temp1[2]), milliseconds=int(temp1[3]))


def avg_start_connection() -> tuple[float, float]:
    waiting_diff = []
    response_diff = []
    for i, c in connections.items():
        w_f = get_timedelta(c["finish open_key_session"][0]).total_seconds()
        w_i = get_timedelta(c["start open_key_session"][0]).total_seconds()
        waiting_diff.append(w_f - w_i)
        if len(c["finish open_key_session"]) > 1:
            r_f = get_timedelta(c["finish open_key_session"][1]).total_seconds()
            r_i = get_timedelta(c["start open_key_session"][1]).total_seconds()
            response_diff.append(r_f - r_i)
    return mean(waiting_diff) if len(waiting_diff) > 0 else 0, mean(response_diff) if len(response_diff) > 0 else 0


def avg_ctr_times() -> tuple[float, float]:
    waiting_diff = []
    response_diff = []
    for i, c in connections.items():
        w_f = get_timedelta(c["finish new_app"][0]).total_seconds()
        w_i = get_timedelta(c["start new_app"][0]).total_seconds()
        waiting_diff.append(w_f - w_i)
        if len(c["finish new_app"]) > 1:
            r_f = get_timedelta(c["finish new_app"][1]).total_seconds()
            r_i = get_timedelta(c["start new_app"][1]).total_seconds()
            response_diff.append(r_f - r_i)
    return mean(waiting_diff) if len(waiting_diff) > 0 else 0, mean(response_diff) if len(response_diff) > 0 else 0


def avg_keys() -> tuple[float, float]:
    single_hop_times = []
    multi_hop_times = []
    for k, c in connections.items():
        if "finish enc_keys" in c.keys() and "start enc_keys" in c.keys():
            for j in range(len(c["finish enc_keys"])):
                f = get_timedelta(c["finish enc_keys"][j]).total_seconds()
                i = get_timedelta(c["start enc_keys"][j]).total_seconds()
                multi_hop_times.append(f - i) if c["relay"] else single_hop_times.append(f - i)
    return mean(single_hop_times) if len(single_hop_times) > 0 else 0, mean(multi_hop_times) if len(multi_hop_times) > 0 else 0


def count_connections_per_type() -> tuple[int, int, int, int]:
    relay = 0
    relay_no_key = 0
    basic_no_key = 0
    for k, c in connections.items():
        if c["relay"]:
            relay += 1
            if "start enc_keys" in c.keys():
                if len(c["start enc_keys"]) == 0:
                    relay_no_key += 1
            else:
                relay_no_key += 1
        else:
            if "start enc_keys" in c.keys():
                if len(c["start enc_keys"]) == 0:
                    basic_no_key += 1
            else:
                basic_no_key += 1
    return len(connections) - relay, basic_no_key, relay, relay_no_key


def check_relay(string: str) -> bool:
    src = saes[string[:14]]
    dst = saes[string[18:]]
    return not ((src, dst) in adjacent_kmes or (dst, src) in adjacent_kmes)


file_name = "logs.log"
file = open(file=file_name, mode="r")
connections: dict[str: dict[str: list[str]]] = {}
launch_time = []
adjacent_kmes = [(5000, 5001), (5001, 5002), (5002, 5003), (5003, 5004), (5004, 5000)]
saes = {}
n_relay = 0
total_keys = 0
key_errors = 0
connections_with_errors: set[str] = set()
refused_connections = 0

for line in file:
    if "Started SAE" in line:
        saes[f'...{line.split("...")[1].split(":")[0]}'] = int(line[-5:-1])
    elif "open_key_session" in line:
        conn = f"{line.split('[[')[1].split(']]')[0]}"
        if "start" in line:
            if conn not in connections.keys():
                connections[conn] = {}
            if "start open_key_session" not in connections[conn].keys():
                connections[conn]["relay"] = check_relay(conn)
                if check_relay(conn):
                    n_relay += 1
                connections[conn]["start open_key_session"] = [line.split(" ")[1]]
            else:
                connections[conn]["start open_key_session"].append(line.split(" ")[1])
        if "finish" in line:
            if "finish open_key_session" not in connections[conn].keys():
                connections[conn]["finish open_key_session"] = [line.split(" ")[1]]
            else:
                connections[conn]["finish open_key_session"].append(line.split(" ")[1])
    elif "new_app" in line:
        conn = f"{line.split('[[')[1].split(']]')[0]}"
        if "start" in line:
            if "start new_app" not in connections[conn].keys():
                connections[conn]["start new_app"] = [line.split(" ")[1]]
            else:
                connections[conn]["start new_app"].append(line.split(" ")[1])
        if "finish" in line:
            if "finish new_app" not in connections[conn].keys():
                connections[conn]["finish new_app"] = [line.split(" ")[1]]
            else:
                connections[conn]["finish new_app"].append(line.split(" ")[1])
    elif "enc_keys" in line:
        conn = f"{line.split('[[')[1].split(']]')[0]}"
        if "start" in line:
            if "start enc_keys" not in connections[conn].keys():
                connections[conn]["start enc_keys"] = [line.split(" ")[1]]
            else:
                connections[conn]["start enc_keys"].append(line.split(" ")[1])
            total_keys += 1
        if "finish" in line:
            if "finish enc_keys" not in connections[conn].keys():
                connections[conn]["finish enc_keys"] = [line.split(" ")[1]]
            else:
                connections[conn]["finish enc_keys"].append(line.split(" ")[1])
    elif "Block not found" in line:
        conn = f"{line.split('[[')[1].split(']]')[0]}"
        connections[conn]["start enc_keys"].pop()
        key_errors += 1
        connections_with_errors.add(conn)
    elif "Insufficient" in line:
        conn = f"{line.split('[[')[1].split(']]')[0]}"
        refused_connections += 1
        connections[conn]["start open_key_session"].pop()
        connections[conn]["start new_app"].pop()

avg_waiting_conn_node, avg_response_conn_node = avg_start_connection()
avg_waiting_conn_ctr, avg_response_conn_ctr = avg_ctr_times()
avg_single_hop_key, avg_multi_hop_key = avg_keys()
single_hop, single_hop_no_keys, multi_hop, multi_hop_no_keys = count_connections_per_type()

print(f"\nQKP: {environ.get('qkp')}")
print(f"Active refusing: {environ.get('ref')}")
print("\nAverage times:")
print(f"\n\tNODE time to evaluate first connection request: {round(avg_waiting_conn_node, 2)}s")
print(f"\tCTR time to evaluate first connection request: {round(avg_waiting_conn_ctr, 2)}s")
print(f"\n\n\tNODE time to evaluate second connection request: {round(avg_response_conn_node, 2)}s")
print(f"\tCTR time to evaluate second connection request: {round(avg_response_conn_ctr, 2)}s")
print(f"\n\tTotal connections: {len(connections)} [SH: {single_hop}, MH: {multi_hop}]")
print(f"\tRefused connections: {round((refused_connections / len(connections)) * 100, 2)}%")
print(f"\tConnections with errors: {round((len(connections_with_errors) / (len(connections) - refused_connections)) * 100, 2)}%")
print(f"\n\tTime to generate single-hop keys: {round(avg_single_hop_key, 2)}s [{single_hop - single_hop_no_keys} connections]")
print(f"\tTime to generate multi-hop keys: {round(avg_multi_hop_key, 2)}s [{multi_hop - multi_hop_no_keys} connections]")
print(f"\n\tTotal delivered keys: {total_keys}")
print(f"\tKey errors: {round(key_errors / total_keys, 4) * 100}%\n")
