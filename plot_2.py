import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---- CONFIG ----
FILES_NORT = {   # Fase 1 (referencia, sin RT)
    "idle": "latencies.csv",
    "stress": "latencies_stress.csv",
    "hackbench": "latencies_hackbench.csv",
    "boonie": "latencies_boonie.csv",
}
FILES_RT = {     # Fase 2 (con --rt)
    "idle": "latencies_rt.csv",
    "stress": "latencies_rt_stress.csv",
    "hackbench": "latencies_rt_hackbench.csv",
    "boonie": "latencies_rt_boonie.csv",
}
XMAX_US = None   # límite X en µs para la comparativa (None = automático). Mismo valor que en Fase 1
N_BINS = 60
# ----------------

COLORS = {"idle": "#377eb8", "stress": "#2ecc71", "hackbench": "#e67e22", "boonie": "#9b59b6"}
C_NORT, C_RT = "#d62728", "#1f77b4"
plt.rcParams.update({"font.size": 16, "axes.titlesize": 18, "axes.labelsize": 16,
                     "xtick.labelsize": 14, "ytick.labelsize": 14, "legend.fontsize": 13})


def load(files):
    return {s: pd.read_csv(f, skipinitialspace=True)["latency(ns)"].to_numpy(float) / 1e3
            for s, f in files.items()}


nort, rt = load(FILES_NORT), load(FILES_RT)

for nombre, d in [("No RT (Fase 1)", nort), ("RT (Fase 2)", rt)]:
    print(f"--- {nombre} ---")
    for s, v in d.items():
        print(f"{s:10s} n={len(v)} media={v.mean():.1f} p50={np.percentile(v,50):.1f} "
              f"p99={np.percentile(v,99):.1f} p99.9={np.percentile(v,99.9):.1f} max={v.max():.1f} (µs)")

# Figura 1: No RT vs RT, mismos ejes y bins
allv = list(nort.values()) + list(rt.values())
xmax = XMAX_US or max(v.max() for v in allv) * 1.02
bins = np.linspace(0, xmax, N_BINS + 1)
ymax = max(np.histogram(v, bins)[0].max() for v in allv) * 100

fig, axes = plt.subplots(2, 2, figsize=(14, 10), sharex=True, sharey=True)
for ax, s in zip(axes.flat, rt):
    ax.hist(nort[s], bins=bins, color=C_NORT, alpha=0.55, edgecolor="black", linewidth=0.3,
            label=f"No RT (max={nort[s].max():.0f} µs)")
    ax.hist(rt[s], bins=bins, color=C_RT, alpha=0.75, edgecolor="black", linewidth=0.3,
            label=f"RT (max={rt[s].max():.0f} µs)")
    ax.set_yscale("log")
    ax.set_xlim(0, xmax)
    ax.set_ylim(0.8, ymax)
    ax.set_title(s.capitalize())
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right", framealpha=0.9)
for ax in axes[1]:
    ax.set_xlabel("Latencia (µs)")
for ax in axes[:, 0]:
    ax.set_ylabel("Frecuencia (nº de ciclos)")
fig.suptitle("Fase 2: latencia No RT vs RT", fontsize=20)
fig.tight_layout()
fig.savefig("fase2_nort_vs_rt.png", dpi=200)

# Figura 2: solo RT con su propio rango (zoom)
xmax_rt = max(v.max() for v in rt.values()) * 1.05
bins_rt = np.linspace(0, xmax_rt, N_BINS + 1)
ymax_rt = max(np.histogram(v, bins_rt)[0].max() for v in rt.values()) * 10

fig, axes = plt.subplots(2, 2, figsize=(14, 10), sharex=True, sharey=True)
for ax, (s, v) in zip(axes.flat, rt.items()):
    ax.hist(v, bins=bins_rt, color=COLORS[s], edgecolor="black", linewidth=0.4, label=f"{s} RT (n={len(v)})")
    ax.axvline(v.max(), color="red", ls="--", lw=1.2, label=f"max = {v.max():.0f} µs")
    ax.set_yscale("log")
    ax.set_xlim(0, xmax_rt)
    ax.set_ylim(0.8, ymax_rt)
    ax.set_title(s.capitalize())
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right", framealpha=0.9)
for ax in axes[1]:
    ax.set_xlabel("Latencia (µs)")
for ax in axes[:, 0]:
    ax.set_ylabel("Frecuencia (nº de ciclos)")
fig.suptitle("Fase 2: latencia con política RT (zoom)", fontsize=20)
fig.tight_layout()
fig.savefig("fase2_rt_zoom.png", dpi=200)
print("Guardado: fase2_nort_vs_rt.png, fase2_rt_zoom.png")