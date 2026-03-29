import numpy as np
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 6))

x = np.linspace(-1, 1, 1000)
y = np.arccos(x)

ax.plot(x, y, color='#d62728', linewidth=2)
ax.axhline(y=0, color='gray', linewidth=0.5)
ax.axvline(x=0, color='gray', linewidth=0.5)

# x轴：-1到1，间隔0.5
ax.set_xlim(-1.3, 1.3)
ax.set_xticks([-1, -0.5, 0, 0.5, 1])
ax.set_xticklabels([r'$-1$', r'$-0.5$', r'$0$', r'$0.5$', r'$1$'])

# y轴：0到π，以π/4为间隔
ax.set_ylim(-0.3, 3.8)
y_ticks = [0, np.pi / 4, np.pi / 2, 3 * np.pi / 4, np.pi]
y_labels = [r'$0$', r'$\frac{\pi}{4}$', r'$\frac{\pi}{2}$', r'$\frac{3\pi}{4}$', r'$\pi$']
ax.set_yticks(y_ticks)
ax.set_yticklabels(y_labels)

ax.set_xlabel('x', fontsize=12)
ax.set_ylabel('y (rad)', fontsize=12)
ax.set_title(r'$y = \arccos x$', fontsize=16)

ax.grid(True, linestyle='--', alpha=0.4)
plt.tight_layout()
plt.savefig('./plot_pic/plot_arccos.png', dpi=200, bbox_inches='tight')
plt.show()
