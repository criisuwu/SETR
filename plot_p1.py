import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SERIES = {
        "Idle":      "latencies.csv",
        "Stress":    "latencies_stress.csv",
        "Hackbench": "latencies_hackbench.csv",
        "Bonnie":    "latencies_boonie.csv",
}
N_BINS = 60            # mismo nº de bins para TODAS las gráficas
PERCENTIL_X = 99.9

plt.rcParams.update({
    "font.size": 16, "axes.titlesize": 20, "axes.labelsize": 18,
    "xtick.labelsize": 15, "ytick.labelsize": 15, "legend.fontsize": 14,
})

COLORES = ["#377eb8", "#2ecc71", "#e67e22", "#9b59b6"]

datos = {}
for etiqueta, fichero in SERIES.items():
    if os.path.exists(fichero):
        df = pd.read_csv(fichero, skipinitialspace=True)
        datos[etiqueta] = df["latency(ns)"].to_numpy() / 1000.0
    else:
        print(f"[aviso] no existe {fichero}, se omite")
 
if not datos:
    raise SystemExit("No se ha encontrado ningún CSV.")


todos = np.concatenate(list(datos.values()))
x_min, x_max = min(0.0, todos.min()), np.percentile(todos, PERCENTIL_X)
bins = np.linspace(x_min, x_max, N_BINS + 1)


fig, ax = plt.subplots(figsize=(11, 6.5))
for (etiqueta, v), color in zip(datos.items(), COLORES):
    ax.hist(np.clip(v, x_min, x_max), bins=bins, color=color, alpha=0.65,
            edgecolor="black", linewidth=0.4,
            label=f"{etiqueta} (n={len(v)}, máx={v.max():.0f} µs)")
 
ax.set_yscale("log")   # quítalo si prefieres escala lineal
ax.set_xlim(x_min, x_max)
ax.set_title("Latencia - Fase 1 (No RT)")
ax.set_xlabel("Latencia (µs)")
ax.set_ylabel("Frecuencia (nº de ciclos)")
ax.grid(True, alpha=0.4)
ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0))   # leyenda fuera de la caja
fig.tight_layout()
fig.savefig("fase1.png", dpi=200, bbox_inches="tight")
print("[ok] fase1.png")
 
# Estadísticas para la memoria
print(f"\n{'Escenario':12s} {'n':>7s} {'media':>9s} {'p99':>9s} {'p99.9':>9s} {'máx':>10s}  (µs)")
for etiqueta, v in datos.items():
    print(f"{etiqueta:12s} {len(v):7d} {v.mean():9.1f} {np.percentile(v,99):9.1f} "
          f"{np.percentile(v,99.9):9.1f} {v.max():10.1f}")
