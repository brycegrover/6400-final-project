# discrete event courier simulation engine, importable so worker processes survive macOS spawn
import time

import numpy as np

PREP_S = 600.0
DROP_SERVICE_S = 120.0
BATCH_WINDOW_S = 120.0
MAX_WAITING_POOL = 400
DAY_S = 86400.0


# greedy cheapest pair matching
def _greedy_match(cost):
    n_c, n_o = cost.shape
    flat_order = np.argsort(cost, axis=None)
    used_c = np.zeros(n_c, dtype=bool)
    used_o = np.zeros(n_o, dtype=bool)
    pairs = []
    limit = min(n_c, n_o)
    for flat in flat_order:
        ci, oi = divmod(int(flat), n_o)
        if used_c[ci] or used_o[oi]:
            continue
        used_c[ci] = True
        used_o[oi] = True
        pairs.append((ci, oi))
        if len(pairs) == limit:
            break
    return pairs

TT_M = None
ORD = None


# worker initializer, memory maps the shared travel time matrix and loads the order arrays
def init_worker(tt_path, ord_path):
    global TT_M, ORD
    TT_M = np.load(tt_path, mmap_mode="r")
    ORD = dict(np.load(ord_path))


# courier fleet starts idle at restaurant nodes, deterministic per fleet size
def _start_positions(fleet, seed):
    rng = np.random.default_rng(seed)
    return rng.choice(ORD["rest_pool"], size=fleet, replace=True)


# nearest available courier, greedy dispatch at order arrival
def _simulate_nac(fleet, seed):
    t_arr, pu, do = ORD["t"], ORD["pu"], ORD["do"]
    n_orders = len(t_arr)
    avail = np.zeros(fleet)
    pos = _start_positions(fleet, seed)
    t_assign = np.empty(n_orders)
    t_pickup = np.empty(n_orders)
    t_deliver = np.empty(n_orders)
    courier = np.empty(n_orders, dtype=np.int64)
    busy = 0.0
    for o in range(n_orders):
        t = t_arr[o]
        tt_c = TT_M[pos, pu[o]]
        free = avail <= t
        if free.any():
            cand = np.flatnonzero(free)
            c = cand[np.argmin(tt_c[cand])]
        else:
            c = np.argmin(np.maximum(avail, t) + tt_c)
        depart = max(avail[c], t)
        arrive = depart + tt_c[c]
        pick = max(arrive, t + PREP_S)
        deliver = pick + TT_M[pu[o], do[o]] + DROP_SERVICE_S
        busy += deliver - depart
        avail[c] = deliver
        pos[c] = do[o]
        t_assign[o] = t
        t_pickup[o] = pick
        t_deliver[o] = deliver
        courier[o] = c
    return t_assign, t_pickup, t_deliver, courier, busy


# system-wide batching, every window solves a global matching of all couriers to waiting orders
# cost is time until the courier can reach the restaurant, so busy couriers compete with dispatch ahead
def _simulate_swb(fleet, seed):
    t_arr, pu, do = ORD["t"], ORD["pu"], ORD["do"]
    n_orders = len(t_arr)
    avail = np.zeros(fleet)
    pos = _start_positions(fleet, seed)
    t_assign = np.empty(n_orders)
    t_pickup = np.empty(n_orders)
    t_deliver = np.empty(n_orders)
    courier = np.empty(n_orders, dtype=np.int64)
    busy = 0.0
    waiting = []
    next_order = 0
    assigned = 0
    T = BATCH_WINDOW_S
    while assigned < n_orders:
        while next_order < n_orders and t_arr[next_order] <= T:
            waiting.append(next_order)
            next_order += 1
        if len(waiting):
            pool = waiting[:MAX_WAITING_POOL]
            drive = TT_M[pos[:, None], pu[np.array(pool)]]
            cost = np.maximum(avail[:, None] - T, 0.0) + drive
            matched = set()
            for ri, ci in _greedy_match(cost):
                o = pool[ci]
                c = ri
                depart = max(avail[c], T)
                arrive = depart + drive[ri, ci]
                pick = max(arrive, t_arr[o] + PREP_S)
                deliver = pick + TT_M[pu[o], do[o]] + DROP_SERVICE_S
                busy += deliver - depart
                avail[c] = deliver
                pos[c] = do[o]
                t_assign[o] = T
                t_pickup[o] = pick
                t_deliver[o] = deliver
                courier[o] = c
                matched.add(o)
                assigned += 1
            waiting = [o for o in waiting if o not in matched]
        T += BATCH_WINDOW_S
    return t_assign, t_pickup, t_deliver, courier, busy


# run one configuration and return the summary plus the per order event arrays
def run_config(strategy, fleet):
    t0 = time.time()
    sim = _simulate_nac if strategy == "nac" else _simulate_swb
    t_assign, t_pickup, t_deliver, courier, busy = sim(fleet, seed=1000 + fleet)
    t_arr = ORD["t"]
    ctd = (t_deliver - t_arr) / 60
    hours = (t_arr // 3600).astype(int)
    makespan = max(float(t_deliver.max()), DAY_S)
    summary = {
        "strategy": strategy,
        "fleet": fleet,
        "mean_min": round(float(ctd.mean()), 2),
        "median_min": round(float(np.median(ctd)), 2),
        "p95_min": round(float(np.quantile(ctd, 0.95)), 2),
        "ontime45_pct": round(float((ctd <= 45).mean() * 100), 1),
        "peak19_mean_min": round(float(ctd[hours == 19].mean()), 2),
        "mean_cycle_min": round(float(busy / len(t_arr) / 60), 2),
        "utilization_pct": round(float(100 * busy / (fleet * makespan)), 1),
        "runtime_s": round(time.time() - t0, 1),
    }
    events = {
        "t_order_s": t_arr, "t_assign_s": t_assign, "t_pickup_s": t_pickup,
        "t_deliver_s": t_deliver, "courier_id": courier,
    }
    return summary, events
