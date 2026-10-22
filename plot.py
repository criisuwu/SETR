"""
Genera los histogramas de latencia de la Práctica 2 a partir de los CSV.
Uso:  python3 plot_histograms.py            (los CSV deben estar en la misma carpeta)
Salida: fase1.png, fase2.png, fase3.png  + tabla de estadísticas por consola.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------- CONFIGURACIÓN (edita los nombres si los tuyos son distintos) ----------------
FIGURAS = {
    "fase1": ("Latencia - Fase 1 (No RT)", {
        "Idle":      "latencies.csv",
        "Stress":    "latencies_stress.csv",
        "Hackbench": "latencies_hackbench.csv",
        "Bonnie":    "latencies_boonie.csv",
    }),
    "fase2": ("Latencia - Fase 2 (RT, SCHED_FIFO)", {
        "Idle":      "latencies_rt.csv",
        "Stress":    "latencies_rt_stress.csv",
        "Hackbench": "latencies_rt_hackbench.csv",
        "Bonnie":    "latencies_rt_boonie.csv",
    }),
    "fase3": ("Latencia - Fase 3 (con perturbaciones)", {
        "Stress No-RT":    "latencies_perturb_stress.csv",
        "Hackbench No-RT": "latencies_perturb_hackbench.csv",
        "Stress RT":       "latencies_perturb_stress_rt.csv",
        "Hackbench RT":    "latencies_perturb_hackbench_rt.csv",
    }),
}
N_BINS = 60            # mismo nº de bins para TODAS las gráficas
PERCENTIL_X = 99.9     # el eje X llega hasta este percentil global (evita que un outlier aplaste todo)
# -----------------------------------------------------------------------------------------------

plt.rcParams.update({
    "font.size": 16, "axes.titlesize": 20, "axes.labelsize": 18,
    "xtick.labelsize": 15, "ytick.labelsize": 15, "legend.fontsize": 14,
})
COLORES = ["#377eb8", "#2ecc71", "#e67e22", "#9b59b6"]


def cargar(path):
    df = pd.read_csv(path, skipinitialspace=True)
    return df["latency(ns)"].to_numpy() / 1000.0   # ns -> µs


# 1) Cargar todo lo que exista
datos = {}
for fig_id, (_, series) in FIGURAS.items():
    for etiqueta, fichero in series.items():
        if os.path.exists(fichero):
            datos[fichero] = cargar(fichero)
        else:
            print(f"[aviso] no existe {fichero}, se omite")

if not datos:
    raise SystemExit("No se ha encontrado ningún CSV.")

# 2) Rango X y bins comunes a todas las figuras
todos = np.concatenate(list(datos.values()))
x_max = np.percentile(todos, PERCENTIL_X)
x_min = min(0.0, todos.min())
bins = np.linspace(x_min, x_max, N_BINS + 1)

# 3) Rango Y común (frecuencia máxima en escala log)
y_max = 1
for v in datos.values():
    h, _ = np.histogram(np.clip(v, x_min, x_max), bins=bins)
    y_max = max(y_max, h.max())

# 4) Dibujar cada figura
for fig_id, (titulo, series) in FIGURAS.items():
    fig, ax = plt.subplots(figsize=(11, 6.5))
    hay = False
    for (etiqueta, fichero), color in zip(series.items(), COLORES):
        if fichero not in datos:
            continue
        v = datos[fichero]
        ax.hist(np.clip(v, x_min, x_max), bins=bins, color=color, alpha=0.65,
                edgecolor="black", linewidth=0.4,
                label=f"{etiqueta} (n={len(v)}, máx={v.max():.0f} µs)")
        hay = True
    if not hay:
        plt.close(fig)
        continue
    ax.set_yscale("log")
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(0.8, y_max * 3)
    ax.set_title(titulo)
    ax.set_xlabel("Latencia (µs)")
    ax.set_ylabel("Frecuencia (nº de ciclos, escala log)")
    ax.grid(True, alpha=0.4)
    # Leyenda fuera de la caja para no tapar datos
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), frameon=True)
    fig.tight_layout()
    fig.savefig(f"{fig_id}.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"[ok] {fig_id}.png")

# 5) Estadísticas para la memoria
print(f"\n{'Fichero':28s} {'n':>7s} {'media':>9s} {'p99':>9s} {'p99.9':>9s} {'máx':>10s}  (µs)")
for fichero, v in datos.items():
    print(f"{fichero:28s} {len(v):7d} {v.mean():9.1f} {np.percentile(v,99):9.1f} "
          f"{np.percentile(v,99.9):9.1f} {v.max():10.1f}")