import numpy as np
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(14, 5))

x = np.linspace(-10 * np.pi, 10 * np.pi, 2000)
y = np.arctan(x)

ax.plot(x, y, color='#8c564b', linewidth=1.5)
ax.axhline(y=0, color='gray', linewidth=0.5)
ax.axvline(x=0, color='gray', linewidth=0.5)

# 画水平渐近线 y=π/2 和 y=-π/2
ax.axhline(y=np.pi / 2, color='gray', linewidth=0.5, linestyle=':')
ax.axhline(y=-np.pi / 2, color='gray', linewidth=0.5, linestyle=':')

# x轴：以π为间隔，从-10π到10π
ax.set_xlim(-10 * np.pi, 10 * np.pi)
x_ticks = list(range(-10, 11))
x_labels = [r'$-10\pi$', r'$-9\pi$', r'$-8\pi$', r'$-7\pi$', r'$-6\pi$',
            r'$-5\pi$', r'$-4\pi$', r'$-3\pi$', r'$-2\pi$', r'$-\pi$', r'$0$',
            r'$\pi$', r'$2\pi$', r'$3\pi$', r'$4\pi$', r'$5\pi$',
            r'$6\pi$', r'$7\pi$', r'$8\pi$', r'$9\pi$', r'$10\pi$']
ax.set_xticks([i * np.pi for i in x_ticks])
ax.set_xticklabels(x_labels, fontsize=8)

# y轴：范围(-2.5, 2.5)，以π/2为间隔
ax.set_ylim(-2.5, 2.5)
y_ticks = [-np.pi, -np.pi / 2, 0, np.pi / 2, np.pi]
y_labels = [r'$-\pi$', r'$-\frac{\pi}{2}$', r'$0$', r'$\frac{\pi}{2}$', r'$\pi$']
ax.set_yticks(y_ticks)
ax.set_yticklabels(y_labels)

ax.set_xlabel('x (rad)', fontsize=12)
ax.set_ylabel('y (rad)', fontsize=12)
ax.set_title(r'$y = \arctan x$', fontsize=16)

ax.grid(True, linestyle='--', alpha=0.4)
plt.tight_layout()
plt.savefig('./plot_pic/plot_arctan.png', dpi=200, bbox_inches='tight')
plt.show()
