import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---- CONFIG ----
FILES = {
    "idle": "latencies.csv",
    "stress": "latencies_stress.csv",
    "hackbench": "latencies_hackbench.csv",
    "boonie": "latencies_boonie.csv",
}
XMAX_US = None   # límite X en µs (None = automático por percentil)
PCT = 99.5       # percentil para recortar el eje X (sube a 99.9 o 100 para ver más cola)
N_BINS = 60
# ----------------

COLORS = {"idle": "#377eb8", "stress": "#2ecc71", "hackbench": "#e67e22", "boonie": "#9b59b6"}
plt.rcParams.update({"font.size": 16, "axes.titlesize": 18, "axes.labelsize": 16,
                     "xtick.labelsize": 14, "ytick.labelsize": 14, "legend.fontsize": 13})

data = {s: pd.read_csv(f, skipinitialspace=True)["latency(ns)"].to_numpy(float) / 1e3
        for s, f in FILES.items()}

for s, v in data.items():
    print(f"{s:10s} n={len(v)} media={v.mean():.1f} p50={np.percentile(v,50):.1f} "
          f"p99={np.percentile(v,99):.1f} p99.9={np.percentile(v,99.9):.1f} max={v.max():.1f} (µs)")

# Rango común ajustado a los datos (recorta outliers extremos)
allv = list(data.values())
lo = max(0, min(np.percentile(v, 100 - PCT) for v in allv) * 0.9)
hi = XMAX_US or max(np.percentile(v, PCT) for v in allv) * 1.05
bins = np.linspace(lo, hi, N_BINS + 1)
ymax = max(np.histogram(v, bins)[0].max() for v in allv) * 2


def fuera(v):
    return int(np.sum((v < lo) | (v > hi)))


# Figura 1: un histograma por escenario
fig, axes = plt.subplots(2, 2, figsize=(14, 10), sharex=True, sharey=True)
for ax, (s, v) in zip(axes.flat, data.items()):
    ax.hist(v, bins=bins, color=COLORS[s], edgecolor="black", linewidth=0.4,
            label=f"{s} (n={len(v)})\nmax = {v.max():.0f} µs, fuera = {fuera(v)}")
    ax.set_yscale("log")
    ax.set_xlim(lo, hi)
    ax.set_ylim(0.8, ymax)
    ax.set_title(s.capitalize())
    ax.grid(alpha=0.3)
    ax.legend(loc="upper right", framealpha=0.9)
for ax in axes[1]:
    ax.set_xlabel("Latencia (µs)")
for ax in axes[:, 0]:
    ax.set_ylabel("Frecuencia (nº de ciclos)")
fig.suptitle("Fase 1: latencia del hilo de control (No RT)", fontsize=20)
fig.tight_layout()
fig.savefig("fase1_escenarios.png", dpi=200)

# Figura 2: superpuestos
fig, ax = plt.subplots(figsize=(12, 7))
for s, v in data.items():
    ax.hist(v, bins=bins, histtype="stepfilled", alpha=0.45, color=COLORS[s],
            edgecolor=COLORS[s], linewidth=1.5, label=f"{s} (n={len(v)}, fuera={fuera(v)})")
ax.set_yscale("log")
ax.set_xlim(lo, hi)
ax.set_ylim(0.8, ymax)
ax.set_xlabel("Latencia (µs)")
ax.set_ylabel("Frecuencia (nº de ciclos)")
ax.set_title("Fase 1: latencia (No RT) - comparativa")
ax.grid(alpha=0.3)
ax.legend(loc="center left", bbox_to_anchor=(1.01, 0.5))
fig.tight_layout()
fig.savefig("fase1_comparativa.png", dpi=200, bbox_inches="tight")
print("Guardado: fase1_escenarios.png, fase1_comparativa.png")