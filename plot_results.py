from pathlib import Path
import matplotlib.pyplot as plt

Path('results').mkdir(exist_ok=True)
agents = [0, 1, 2, 3, 4, 5]
received = [76, 80, 74, 78, 75, 77]
missing = [4, 0, 6, 2, 5, 3]
fig, ax = plt.subplots(figsize=(7.2, 3.8))
ax.bar(agents, received, label='received packets', color='#2878b5')
ax.bar(agents, missing, bottom=received, label='missing packets', color='#e07a5f')
ax.set(xlabel='UAV ID', ylabel='Packets in 8 s', title='Telemetry delivery summary')
ax.legend(frameon=False, ncol=2); ax.grid(axis='y', alpha=.25); fig.tight_layout()
fig.savefig('results/telemetry_summary.png', dpi=160); plt.close(fig)
