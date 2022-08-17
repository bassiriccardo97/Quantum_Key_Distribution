from datetime import timedelta


def get_timedelta(string: str) -> timedelta:
    temp = string.split(",")
    temp1 = temp[0].split(":") + [temp[1]]
    return timedelta(hours=int(temp1[0]), minutes=int(temp1[1]), seconds=int(temp1[2]), milliseconds=int(temp1[3]))


def eval_avg() -> tuple[float, float, float]:
    sum_start_mid = 0
    sum_mid_second = 0
    sum_second_end = 0
    count = 0
    for key, val in connections.items():
        if "mid" in val.keys():
            if "second" in val.keys():
                if "end" in val.keys():
                    first = get_timedelta(val["first"])
                    mid = get_timedelta(val["mid"])
                    second = get_timedelta(val["second"])
                    end = get_timedelta(val["end"])
                    sum_start_mid += mid.total_seconds() - first.total_seconds()
                    sum_mid_second += second.total_seconds() - mid.total_seconds()
                    sum_second_end += end.total_seconds() - second.total_seconds()
                    count += 1
                else:
                    print(f"Missing 'ksid assigned' for connection {key}.")
            else:
                print(f"Connection [{key}] refused.")
        else:
            print(f"Missing 'connection required' for connection {key}")
    return round(sum_start_mid / count, 2), round(sum_mid_second / count, 2), round(sum_second_end / count, 2)


def eval_avg_keys() -> tuple[float, float, float, float, float, float]:
    count = 0
    count_relay = 0
    total = 0.0
    total_relay = 0.0
    maximum_not_relay = 0.0
    maximum_relay = 0.0
    minimum_not_relay = 0.0
    minimum_relay = 0.0
    for key in connections.keys():
        if "enc_key" in connections[key].keys() and "key" in connections[key].keys():
            for req_time, key_time in zip(connections[key]["enc_key"], connections[key]["key"]):
                if key_time is not None:
                    r = get_timedelta(req_time)
                    k = get_timedelta(key_time)
                    t = k.total_seconds() - r.total_seconds()
                    if not connections[key]["relay"]:
                        if t > maximum_not_relay:
                            maximum_not_relay = t
                        elif t < minimum_not_relay:
                            minimum_not_relay = t
                        total += t
                        count += 1
                    else:
                        if t > maximum_relay:
                            maximum_relay = t
                        elif t < minimum_relay:
                            minimum_relay = t
                        total_relay += t
                        count_relay += 1
    return round(total / count, 2) if count != 0 else 0, round(total_relay / count_relay, 2) if count_relay != 0 else 0, round(maximum_not_relay, 2), \
           round(maximum_relay, 2), round(minimum_not_relay, 4), round(minimum_relay, 4)


def eval_launch_delay() -> float:
    sum_delays = 0
    starts = []
    for key, val in connections.items():
        starts.append(get_timedelta(val["first"]))
    assert len(launch_time) == len(connections.keys())
    for i in range(len(launch_time)):
        sum_delays += starts[i].total_seconds() - get_timedelta(launch_time[i]).total_seconds()
    return round(sum_delays / len(launch_time), 2)


def check_relay(string: str) -> bool:
    src = saes[string[:14]]
    dst = saes[string[18:]]
    return not ((src, dst) in adjacent_kmes or (dst, src) in adjacent_kmes)


file_name = "logs.log"
file = open(file=file_name, mode="r")
connections = {}
launch_time = []
adjacent_kmes = [(5000, 5001), (5001, 5002), (5002, 5003), (5003, 5004), (5004, 5000)]
saes = {}

for line in file:
    if "Started SAE" in line:
        saes[f'...{line.split("...")[1].split(":")[0]}'] = int(line[-5:-1])
    elif "open_key_session" in line:
        conn = f'...{line.split("...")[2][:-1]} -> ...{line.split("...")[1].split(":")[0]}'
        connections[conn] = {}
        connections[conn]["relay"] = check_relay(conn)
        connections[conn]["first"] = line.split(" ")[1]
    elif "Connection required" in line:
        conn = line[-33:-1]
        connections[conn]["mid"] = line.split(" ")[1]
    elif "Connection added" in line:
        conn = line[-34:-2]
        connections[conn]["second"] = line.split(" ")[1]
    elif "ksid assigned" in line:
        conn = f'...{line.split("...")[1].split(":")[0]} -> ...{line.split("...")[2][:-1]}'
        connections[conn]["end"] = line.split(" ")[1]
    elif "enc_keys" in line:
        conn = f'...{line.split("...")[1].split(":")[0]} -> ...{line.split("...")[2][:-1]}'
        if conn in connections.keys():
            if "enc_key" in connections[conn].keys():
                connections[conn]["enc_key"].append(line.split(" ")[1])
            else:
                connections[conn]["enc_key"] = [line.split(" ")[1]]
                connections[conn]["key"] = []
    elif "Starting connection" in line:
        launch_time.append(line.split(" ")[1])
    elif "[94mKEY" in line:
        conn = f'...{line.split("...")[1].split(":")[0]} -> ...{line.split("...")[2].split("]")[0]}'
        if conn in connections.keys():
            if "enc_key" in connections[conn].keys():
                if len(connections[conn]["enc_key"]) - len(connections[conn]["key"]) > 1:
                    connections[conn]["key"].append(None)
                    connections[conn]["key"].append(line.split(" ")[1])
                else:
                    connections[conn]["key"].append(line.split(" ")[1])

avg_start_mid, avg_mid_second, avg_second_end = eval_avg()
avg_time_keys, avg_time_keys_relay, maximum, max_relay, minimum, min_relay = eval_avg_keys()
avg_launch_delay = eval_launch_delay()
print("\nAverage times:")
print(f"\tSAE open_key_session --> {avg_start_mid}s --> CTR connection required")
print(f"\tCTR connection required --> {avg_mid_second}s --> CTR connection added")
print(f"\tCTR connection added --> {avg_mid_second}s --> SAE ksid assigned")
print(f"\n\tTotal average time for a complete connection: {round(avg_start_mid + avg_mid_second + avg_mid_second, 2)}s")
print(f"\n\tAverage delay time to start a connection: {avg_launch_delay}s")
print(f"\n\tAverage time request key --> get key: {avg_time_keys}s (max = {maximum}s, min = {minimum}s)")
print(f"\tAverage time request key --> get key: {avg_time_keys_relay}s (max = {max_relay}s, min = {min_relay}s) [Relay]")
print(f"\tTotal average time request key --> get key: {round((avg_time_keys + avg_time_keys_relay) / (2 if avg_time_keys != 0 and avg_time_keys_relay != 0 else 1), 2)}s")
