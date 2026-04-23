import numpy as np
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(14, 5))

x = np.linspace(-10 * np.pi, 10 * np.pi, 20000)
y = np.tan(x)

# 限制y值范围，避免渐近线处连成直线
y = np.where(np.abs(y) > 10, np.nan, y)

ax.plot(x, y, color='#ff7f0e', linewidth=1.5)
ax.axhline(y=0, color='gray', linewidth=0.5)
ax.axvline(x=0, color='gray', linewidth=0.5)

# 在渐近线处画竖直虚线
for k in range(-10, 11):
    ax.axvline(x=(k + 0.5) * np.pi, color='gray', linewidth=0.3, linestyle=':')

# x轴：以π为间隔，从-10π到10π
ax.set_xlim(-10 * np.pi, 10 * np.pi)
x_ticks = list(range(-10, 11))
x_labels = [r'$-10\pi$', r'$-9\pi$', r'$-8\pi$', r'$-7\pi$', r'$-6\pi$',
            r'$-5\pi$', r'$-4\pi$', r'$-3\pi$', r'$-2\pi$', r'$-\pi$', r'$0$',
            r'$\pi$', r'$2\pi$', r'$3\pi$', r'$4\pi$', r'$5\pi$',
            r'$6\pi$', r'$7\pi$', r'$8\pi$', r'$9\pi$', r'$10\pi$']
ax.set_xticks([i * np.pi for i in x_ticks])
ax.set_xticklabels(x_labels, fontsize=8)

# y轴：范围(-10, 10)，间隔2
ax.set_ylim(-10, 10)
ax.set_yticks(np.arange(-10, 11, 2))

ax.set_xlabel('x (rad)', fontsize=12)
ax.set_ylabel('y', fontsize=12)
ax.set_title(r'$y = \tan x$', fontsize=16)

ax.grid(True, linestyle='--', alpha=0.4)
plt.tight_layout()
plt.savefig('./plot_pic/plot_tan.png', dpi=200, bbox_inches='tight')
plt.show()
