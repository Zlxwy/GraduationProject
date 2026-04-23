import numpy as np
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(14, 5))

x = np.linspace(-10 * np.pi, 10 * np.pi, 2000)
y = np.sin(x)

ax.plot(x, y, color='#1f77b4', linewidth=1.5)
ax.axhline(y=0, color='gray', linewidth=0.5)
ax.axvline(x=0, color='gray', linewidth=0.5)

# x轴：以π为间隔，从-10π到10π
ax.set_xlim(-10 * np.pi, 10 * np.pi)
x_ticks = list(range(-10, 11))
x_labels = [r'$-10\pi$', r'$-9\pi$', r'$-8\pi$', r'$-7\pi$', r'$-6\pi$',
            r'$-5\pi$', r'$-4\pi$', r'$-3\pi$', r'$-2\pi$', r'$-\pi$', r'$0$',
            r'$\pi$', r'$2\pi$', r'$3\pi$', r'$4\pi$', r'$5\pi$',
            r'$6\pi$', r'$7\pi$', r'$8\pi$', r'$9\pi$', r'$10\pi$']
ax.set_xticks([i * np.pi for i in x_ticks])
ax.set_xticklabels(x_labels, fontsize=8)

# y轴：范围(-1.5, 1.5)，间隔0.5
ax.set_ylim(-1.5, 1.5)
ax.set_yticks(np.arange(-1.5, 1.6, 0.5))

ax.set_xlabel('x (rad)', fontsize=12)
ax.set_ylabel('y', fontsize=12)
ax.set_title(r'$y = \sin x$', fontsize=16)

ax.grid(True, linestyle='--', alpha=0.4)
plt.tight_layout()
plt.savefig('./plot_pic/plot_sin.png', dpi=200, bbox_inches='tight')
plt.show()
