import numpy as np
import matplotlib.pyplot as plt

def simulate_frame_collision(n_users, n_slots, degrees, probs, rng):
    """碰撞模型：時槽只剩一個人才解得出來"""
    user_slots = []
    for u in range(n_users):
        d = rng.choice(degrees, p=probs)
        slots = rng.choice(n_slots, size=d, replace=False)
        user_slots.append(slots.tolist())

    slot_users = [[] for _ in range(n_slots)]
    for u, slots in enumerate(user_slots):
        for s in slots:
            slot_users[s].append(u)

    decoded = [False] * n_users
    progress = True
    while progress:
        progress = False
        for s in range(n_slots):
            if len(slot_users[s]) == 1:
                u = slot_users[s][0]
                decoded[u] = True
                for t in user_slots[u]:
                    slot_users[t].remove(u)
                progress = True
    return sum(decoded)

def simulate_frame_sinr(n_users, n_slots, degrees, probs, rng, snr, gamma):
    """SINR 模型：時槽裡最強的人 SINR >= gamma 就解得出來"""
    NOISE = 1.0
    user_slots = []
    slot_users = [[] for _ in range(n_slots)]   # 每格存 (使用者, 收到的功率)
    for u in range(n_users):
        d = rng.choice(degrees, p=probs)
        slots = rng.choice(n_slots, size=d, replace=False)
        user_slots.append(slots.tolist())
        for s in slots:
            power = snr * rng.exponential(1.0)  # 衰落：每份副本的強度都隨機
            slot_users[s].append((u, power))

    decoded = [False] * n_users
    progress = True
    while progress:
        progress = False
        for s in range(n_slots):
            if len(slot_users[s]) == 0:
                continue
            total = sum(p for _, p in slot_users[s])          # 這格所有訊號的總功率
            u, p = max(slot_users[s], key=lambda pair: pair[1])  # 最強的那個人
            sinr = p / (total - p + NOISE)
            if sinr >= gamma:
                decoded[u] = True
                for t in user_slots[u]:                       # SIC：把他的副本全部扣掉
                    slot_users[t] = [(v, q) for v, q in slot_users[t] if v != u]
                progress = True
    return sum(decoded)

# ===== 參數 =====
rng = np.random.default_rng(0)
N_SLOTS = 100
N_FRAMES = 200
SNR = 10.0      # 平均訊號強度是雜訊的 10 倍
GAMMA = 2.0     # SINR 門檻
loads = np.arange(0.1, 1.51, 0.1)

dist = ([3], [1.0])   # 每人 3 份副本

for label, model in [("collision model", "collision"), ("SINR model", "sinr")]:
    throughputs = []
    for G in loads:
        n_users = int(round(G * N_SLOTS))
        total = 0
        for _ in range(N_FRAMES):
            if model == "collision":
                total += simulate_frame_collision(n_users, N_SLOTS, *dist, rng)
            else:
                total += simulate_frame_sinr(n_users, N_SLOTS, *dist, rng, SNR, GAMMA)
        throughputs.append(total / (N_FRAMES * N_SLOTS))
    print(label, [round(t, 3) for t in throughputs])
    plt.plot(loads, throughputs, marker="o", label=label)

plt.plot(loads, loads, "k--", label="ideal T = G")
plt.xlabel("Load G (users per slot)")
plt.ylabel("Throughput T (decoded packets per slot)")
plt.title("3 copies: collision vs SINR (SNR=10, gamma=2)")
plt.legend(); plt.grid(True)
plt.savefig("figures/sinr_vs_collision.png", dpi=110)
plt.show()
