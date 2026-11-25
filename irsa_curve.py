import numpy as np
import matplotlib.pyplot as plt

def simulate_frame(n_users, n_slots, degrees, probs, rng):
    """模擬一個 frame，回傳解出幾個人"""
    # 第二步:丟副本
    user_slots=[]
    for u in range(n_users):
        d = rng.choice(degrees, p=probs) 
        slots=rng.choice(n_slots,size=d, replace=False)
        user_slots.append(slots.tolist())

    slot_users=[[] for _ in range(n_slots)]
    for u, slots in enumerate(user_slots):
        for s in slots:
            slot_users[s].append(u)

    # 第三步: 剝洋蔥
    decoded = [False] * n_users
    progress = True
    while progress:
        progress=False
        for s in range(n_slots):
            if len(slot_users[s])==1:
                u = slot_users[s][0]
                decoded[u]=True
                for t in user_slots[u]:
                    slot_users[t].remove(u)
                progress =True
    return sum(decoded)

# 第四部:重複很多次，畫曲線
rng= np.random.default_rng(0)
N_SLOTS = 1000    #每個frame 1000個時槽
N_FRAMES = 200   #每種情況跑200個frame取平均
loads = np.arange(0.75, 0.96, 0.02)   # 0.75, 0.77, ..., 0.95

distributions={
    "1 copy(ALOHA)":([1],[1.0]),
    "3 copies":([3],[1.0]),
    "half 2, half 3":([2,3],[0.5,0.5]),
    "50% 2, 28% 3, 22% 8": ([2, 3, 8], [0.5, 0.28, 0.22]),
}
for name,(degrees,probs) in distributions.items():    
    throughputs=[]
    for G in loads:
        n_users=int(round(G*N_SLOTS))   # 負載乘上時槽 算出人數  四捨五入轉成整數 存進n_users
        total_decoded=0
        for _ in range(N_FRAMES):
            total_decoded += simulate_frame(n_users,N_SLOTS,degrees, probs,rng)
        T=total_decoded/(N_FRAMES*N_SLOTS)
        throughputs.append(T)
    plt.plot(loads,throughputs,marker="o",label=name)

plt.plot(loads, loads, "k--", label="ideal T = G")
plt.xlabel("Load G (users per slot)")
plt.ylabel("Throughput T (decoded packets per slot)")
plt.legend()
plt.grid(True)
plt.show()