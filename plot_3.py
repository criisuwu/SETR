import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---- CONFIG ----
F1_REF = "latencies_stress.csv"       # Fase 1 sin perturbaciones (referencia)
F2_REF = "latencies_rt_stress.csv"       # Fase 2 RT sin perturbaciones (referencia)
F3_NORT = "latencies_w_rt_perturb_stress.csv"      # Fase 3 planificador estándar + perturbaciones
F3_RT = "latencies_perturb_stress.csv"     # Fase 3 con --rt + perturbaciones
XMAX_US = None                    # None = automático. Mismo valor que en Fase 1 y 2
N_BINS = 50
LOG_Y = False
PERTURB_PERIOD_S = 5.0
# ----------------

# ---- ESTILO (tipo paper, como el ejemplo) ----
plt.rcParams.update({
    "font.family": ["cmr10", "DejaVu Serif"],
    "mathtext.fontset": "cm", "axes.formatter.use_mathtext": True, "axes.unicode_minus": False,
    "font.size": 16, "axes.titlesize": 22, "axes.labelsize": 18,
    "xtick.labelsize": 15, "ytick.labelsize": 15, "legend.fontsize": 14,
    "xtick.direction": "in", "ytick.direction": "in", "xtick.top": True, "ytick.right": True,
    "xtick.minor.visible": True, "ytick.minor.visible": True,
    "axes.grid": True, "grid.alpha": 0.5, "axes.axisbelow": True,
    "legend.frameon": True, "legend.fancybox": True, "legend.edgecolor": "black", "legend.framealpha": 1,
})
XLABEL = r"Latencia ($\mu$s)"
YLABEL = "Frecuencia"

C_NORT, C_RT, C_REF = "#d62728", "#377eb8", "#7f7f7f"

df = {k: pd.read_csv(f, skipinitialspace=True)
      for k, f in [("f1", F1_REF), ("f2", F2_REF), ("f3n", F3_NORT), ("f3r", F3_RT)]}
lat = {k: d["latency(ns)"].to_numpy(float) / 1e3 for k, d in df.items()}

nombres = {"f1": "Fase1 No RT (sin pert.)", "f3n": "Fase3 No RT (con pert.)",
           "f2": "Fase2 RT (sin pert.)", "f3r": "Fase3 RT (con pert.)"}
for k in ["f1", "f3n", "f2", "f3r"]:
    v = lat[k]
    print(f"{nombres[k]:25s} n={len(v)} media={v.mean():.1f} p50={np.percentile(v,50):.1f} "
          f"p99={np.percentile(v,99):.1f} p99.9={np.percentile(v,99.9):.1f} max={v.max():.1f} (µs)")

xmax = XMAX_US or max(v.max() for v in lat.values()) * 1.02
bins = np.linspace(0, xmax, N_BINS + 1)
ymax = max(np.histogram(v, bins)[0].max() for v in lat.values()) * 1.15


def comparar(fichero, titulo, series):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.hist([v for _, v, _ in series], bins=bins, color=[c for _, _, c in series],
            edgecolor="black", linewidth=0.6,
            label=[f"{l} (n={len(v)})" for l, v, _ in series])
    if LOG_Y:
        ax.set_yscale("log")
    else:
        ax.set_ylim(0, ymax)
    ax.set_xlim(0, xmax)
    ax.set_xlabel(XLABEL)
    ax.set_ylabel(YLABEL)
    ax.set_title(titulo)
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(fichero, dpi=200)


comparar("fase3_nort_vs_fase1.png", "Latencia (No RT)",
         [("Fase 1 sin pert.", lat["f1"], C_REF), ("Fase 3 con pert.", lat["f3n"], C_NORT)])
comparar("fase3_rt_vs_fase2.png", "Latencia (RT)",
         [("Fase 2 sin pert.", lat["f2"], C_REF), ("Fase 3 con pert.", lat["f3r"], C_RT)])
comparar("fase3_nort_vs_rt.png", "Latencia con perturbaciones",
         [("No RT", lat["f3n"], C_NORT), ("RT", lat["f3r"], C_RT)])

# Ángulo del péndulo en el tiempo
fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
for ax, (label, d, c) in zip(axes, [("No RT + pert.", df["f3n"], C_NORT), ("RT + pert.", df["f3r"], C_RT)]):
    t = d["epoch"].to_numpy(float)
    t = t - t[0]
    ax.plot(t, d["angle"].to_numpy(float), color=c, lw=1.0, label=label)
    for tp in np.arange(PERTURB_PERIOD_S, t[-1], PERTURB_PERIOD_S):
        ax.axvline(tp, color="black", ls=":", lw=0.8, alpha=0.6)
    ax.plot([], [], color="black", ls=":", label=f"Perturbación (cada {PERTURB_PERIOD_S:.0f} s)")
    ax.set_ylabel("Ángulo (rad)")
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0))
axes[-1].set_xlabel("Tiempo (s)")
axes[0].set_title("Ángulo del péndulo")
fig.tight_layout()
fig.savefig("fase3_angulo.png", dpi=200, bbox_inches="tight")
print("Guardado: fase3_nort_vs_fase1.png, fase3_rt_vs_fase2.png, fase3_nort_vs_rt.png, fase3_angulo.png")