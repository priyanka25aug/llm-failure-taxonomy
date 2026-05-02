import csv
import os
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_PATH = REPO_ROOT / "data" / "public_incidents" / "incidents.csv"
CHARTS_DIR = REPO_ROOT / "outputs" / "charts"

CLASS_ORDER = [
    "CLASS_1_MODEL_DRIFT",
    "CLASS_2_INFRASTRUCTURE",
    "CLASS_3_INTEGRATION",
    "CLASS_4_EVALUATION",
    "CLASS_5_SAFETY_COMPLIANCE",
    "CLASS_6_OPERATIONAL",
]

CLASS_SHORT = {
    "CLASS_1_MODEL_DRIFT": "C1 Model Drift",
    "CLASS_2_INFRASTRUCTURE": "C2 Infrastructure",
    "CLASS_3_INTEGRATION": "C3 Integration",
    "CLASS_4_EVALUATION": "C4 Evaluation",
    "CLASS_5_SAFETY_COMPLIANCE": "C5 Safety",
    "CLASS_6_OPERATIONAL": "C6 Operational",
}

SEVERITY_ORDER = ["critical", "high", "medium", "low"]
DETECTABILITY_ORDER = ["immediate", "delayed", "silent"]


class TaxonomyAnalyzer:
    def __init__(self, data_path: str = str(DATA_PATH)):
        self.data_path = data_path
        self.records: List[Dict] = []
        self._load()

    def _load(self):
        with open(self.data_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            self.records = [row for row in reader]

    def _save(self, fig, name: str):
        CHARTS_DIR.mkdir(parents=True, exist_ok=True)
        path = CHARTS_DIR / name
        fig.savefig(str(path), dpi=120, bbox_inches="tight")
        plt.close(fig)
        print(f"  Saved: {path}")

    def fig1_class_distribution(self):
        counts = Counter(r["failure_class"] for r in self.records)
        classes = [CLASS_SHORT.get(c, c) for c in CLASS_ORDER]
        values = [counts.get(c, 0) for c in CLASS_ORDER]

        fig, ax = plt.subplots(figsize=(10, 5))
        bars = ax.bar(classes, values, color="#4C72B0", edgecolor="white", linewidth=0.8)
        ax.bar_label(bars, padding=3, fontsize=10)
        ax.set_title("Figure 1 — LLM Failure Class Distribution (n=50)", fontsize=13, fontweight="bold")
        ax.set_ylabel("Incident Count")
        ax.set_ylim(0, max(values) + 4)
        ax.tick_params(axis="x", rotation=15)
        fig.tight_layout()
        self._save(fig, "fig1_class_distribution.png")

    def fig2_severity_heatmap(self):
        matrix = np.zeros((len(SEVERITY_ORDER), len(CLASS_ORDER)), dtype=int)
        for r in self.records:
            si = SEVERITY_ORDER.index(r["severity"]) if r["severity"] in SEVERITY_ORDER else -1
            ci = CLASS_ORDER.index(r["failure_class"]) if r["failure_class"] in CLASS_ORDER else -1
            if si >= 0 and ci >= 0:
                matrix[si, ci] += 1

        fig, ax = plt.subplots(figsize=(11, 4))
        im = ax.imshow(matrix, cmap="YlOrRd", aspect="auto")
        ax.set_xticks(range(len(CLASS_ORDER)))
        ax.set_xticklabels([CLASS_SHORT[c] for c in CLASS_ORDER], rotation=20, ha="right", fontsize=9)
        ax.set_yticks(range(len(SEVERITY_ORDER)))
        ax.set_yticklabels(SEVERITY_ORDER, fontsize=10)
        ax.set_title("Figure 2 — Severity × Failure Class Heatmap", fontsize=13, fontweight="bold")
        plt.colorbar(im, ax=ax, label="Incident Count")
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                ax.text(j, i, str(matrix[i, j]), ha="center", va="center", fontsize=10, color="black")
        fig.tight_layout()
        self._save(fig, "fig2_severity_heatmap.png")

    def fig3_detectability(self):
        data = {d: [0] * len(CLASS_ORDER) for d in DETECTABILITY_ORDER}
        for r in self.records:
            det = r["detectability"]
            ci = CLASS_ORDER.index(r["failure_class"]) if r["failure_class"] in CLASS_ORDER else -1
            if det in DETECTABILITY_ORDER and ci >= 0:
                data[det][ci] += 1

        fig, ax = plt.subplots(figsize=(11, 5))
        x = np.arange(len(CLASS_ORDER))
        width = 0.25
        colors = ["#4C72B0", "#DD8452", "#55A868"]
        bottoms = np.zeros(len(CLASS_ORDER))
        for i, det in enumerate(DETECTABILITY_ORDER):
            vals = np.array(data[det])
            ax.bar(x, vals, width=0.6, bottom=bottoms, label=det, color=colors[i], edgecolor="white")
            bottoms += vals

        ax.set_xticks(x)
        ax.set_xticklabels([CLASS_SHORT[c] for c in CLASS_ORDER], rotation=15, ha="right", fontsize=9)
        ax.set_title("Figure 3 — Detectability by Failure Class", fontsize=13, fontweight="bold")
        ax.set_ylabel("Incident Count")
        ax.legend(title="Detectability")
        fig.tight_layout()
        self._save(fig, "fig3_detectability.png")

    def fig4_blast_radius(self):
        counts = Counter(r["blast_radius"] for r in self.records)
        labels = list(counts.keys())
        values = list(counts.values())
        colors = plt.cm.Set2(np.linspace(0, 1, len(labels)))

        fig, ax = plt.subplots(figsize=(8, 6))
        wedges, texts, autotexts = ax.pie(
            values, labels=labels, autopct="%1.1f%%", colors=colors,
            startangle=140, pctdistance=0.82
        )
        ax.set_title("Figure 4 — Blast Radius Distribution", fontsize=13, fontweight="bold")
        fig.tight_layout()
        self._save(fig, "fig4_blast_radius.png")

    def fig5_domain_breakdown(self):
        counts = Counter(r["domain"] for r in self.records)
        domains = sorted(counts, key=lambda k: counts[k])
        values = [counts[d] for d in domains]

        fig, ax = plt.subplots(figsize=(9, 5))
        ax.barh(domains, values, color="#4C72B0", edgecolor="white")
        ax.set_title("Figure 5 — Incident Count by Domain", fontsize=13, fontweight="bold")
        ax.set_xlabel("Incident Count")
        for i, v in enumerate(values):
            ax.text(v + 0.1, i, str(v), va="center", fontsize=9)
        fig.tight_layout()
        self._save(fig, "fig5_domain_breakdown.png")

    def fig6_mttd_boxplot(self):
        class_mttd: Dict[str, List[float]] = {c: [] for c in CLASS_ORDER}
        for r in self.records:
            cls = r["failure_class"]
            try:
                mttd = float(r["mttd_hours"])
            except (ValueError, KeyError):
                continue
            if cls in class_mttd and mttd >= 0:
                class_mttd[cls].append(mttd + 1)

        data = [class_mttd[c] for c in CLASS_ORDER]
        labels = [CLASS_SHORT[c] for c in CLASS_ORDER]

        fig, ax = plt.subplots(figsize=(11, 5))
        bp = ax.boxplot(data, tick_labels=labels, patch_artist=True, notch=False)
        colors = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2", "#937860"]
        for patch, color in zip(bp["boxes"], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        ax.set_yscale("log")
        ax.set_ylabel("MTTD (hours, log scale)")
        ax.set_title("Figure 6 — Mean Time to Detect by Failure Class (log scale)", fontsize=13, fontweight="bold")
        ax.tick_params(axis="x", rotation=15)
        fig.tight_layout()
        self._save(fig, "fig6_mttd_boxplot.png")

    def fig7_failure_budget_class(self):
        counts = Counter(r["failure_budget_class"] for r in self.records)
        fc_order = ["FC_A", "FC_B", "FC_C", "FC_D"]
        values = [counts.get(fc, 0) for fc in fc_order]
        colors = ["#C44E52", "#DD8452", "#4C72B0", "#55A868"]

        fig, ax = plt.subplots(figsize=(7, 4))
        bars = ax.bar(fc_order, values, color=colors, edgecolor="white", linewidth=0.8)
        ax.bar_label(bars, padding=3, fontsize=11)
        ax.set_title("Figure 7 — Failure Budget Risk Class Distribution", fontsize=13, fontweight="bold")
        ax.set_ylabel("Incident Count")
        ax.set_ylim(0, max(values) + 4)
        labels_full = ["FC_A\n(Decision-Critical)", "FC_B\n(Customer-Facing)",
                       "FC_C\n(Internal)", "FC_D\n(Experimental)"]
        ax.set_xticks(range(len(fc_order)))
        ax.set_xticklabels(labels_full)
        fig.tight_layout()
        self._save(fig, "fig7_failure_budget_class.png")

    def print_summary_stats(self):
        n = len(self.records)
        class_counts = Counter(r["failure_class"] for r in self.records)
        severity_counts = Counter(r["severity"] for r in self.records)
        detect_counts = Counter(r["detectability"] for r in self.records)
        domain_counts = Counter(r["domain"] for r in self.records)
        fc_counts = Counter(r["failure_budget_class"] for r in self.records)

        print(f"\n{'='*60}")
        print(f"DATASET SUMMARY  (n={n} incidents)")
        print(f"{'='*60}")
        print("\nBy Failure Class:")
        for c in CLASS_ORDER:
            print(f"  {CLASS_SHORT[c]:25s}: {class_counts.get(c, 0):3d}")
        print("\nBy Severity:")
        for s in SEVERITY_ORDER:
            print(f"  {s:10s}: {severity_counts.get(s, 0):3d}")
        print("\nBy Detectability:")
        for d in DETECTABILITY_ORDER:
            pct = 100 * detect_counts.get(d, 0) / n
            print(f"  {d:10s}: {detect_counts.get(d, 0):3d}  ({pct:.0f}%)")
        print("\nTop Domains:")
        for dom, cnt in domain_counts.most_common(5):
            print(f"  {dom:25s}: {cnt}")
        print("\nBy Failure Budget Class:")
        for fc in ["FC_A", "FC_B", "FC_C", "FC_D"]:
            print(f"  {fc}: {fc_counts.get(fc, 0)}")
        print(f"{'='*60}\n")

    def run_all(self):
        print("\nGenerating figures...")
        self.fig1_class_distribution()
        self.fig2_severity_heatmap()
        self.fig3_detectability()
        self.fig4_blast_radius()
        self.fig5_domain_breakdown()
        self.fig6_mttd_boxplot()
        self.fig7_failure_budget_class()
        self.print_summary_stats()
        print("Done. Charts saved to outputs/charts/")


if __name__ == "__main__":
    analyzer = TaxonomyAnalyzer()
    analyzer.run_all()
