"""
生成矢量分解讲解所需的示意图
"""
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# ========== 图1：矢量分解基本概念 ==========
fig, ax = plt.subplots(1, 1, figsize=(8, 6))

# 画矢量
C = np.array([5, 3])
A = np.array([4, 0])
B = np.array([1, 3])

# 矢量 C（从原点出发）
ax.annotate('', xy=C, xytext=(0, 0),
            arrowprops=dict(arrowstyle='->', color='blue', lw=2.5))
# 矢量 A（从原点出发）
ax.annotate('', xy=A, xytext=(0, 0),
            arrowprops=dict(arrowstyle='->', color='red', lw=2.5))
# 矢量 B（从 A 的终点出发，到 C 的终点）—— 修复：xy=C 而非 xy=B
ax.annotate('', xy=C, xytext=A,
            arrowprops=dict(arrowstyle='->', color='green', lw=2.5))

# 虚线辅助（平行四边形法则）
ax.plot([A[0], C[0]], [A[1], C[1]], 'k--', lw=1, alpha=0.4)
# 补齐平行四边形：从B终点到C
ax.plot([B[0], C[0]], [B[1], C[1]], 'k--', lw=1, alpha=0.4)
# B 也从原点画一条淡色辅助
ax.annotate('', xy=B, xytext=(0, 0),
            arrowprops=dict(arrowstyle='->', color='green', lw=1.2, linestyle='dashed', alpha=0.4))

mid_a = A / 2
mid_b = A + B / 2  # 箭头中点 = A + B/2 = (4.5, 1.5)
mid_c = C / 2

ax.text(mid_a[0], mid_a[1] - 0.55, r'$\vec{A}$', fontsize=16, color='red',
        ha='center', fontweight='bold')
ax.text(mid_b[0] + 0.5, mid_b[1], r'$\vec{B}$', fontsize=16, color='green',
        ha='center', fontweight='bold')
ax.text(mid_c[0] - 0.7, mid_c[1] + 0.35, r'$\vec{C}$', fontsize=16, color='blue',
        ha='center', fontweight='bold')

ax.text(5.5, 3.5, r'$\vec{C} = \vec{A} + \vec{B}$', fontsize=15,
        bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', edgecolor='gray'))

# 角度弧
theta_a = math.atan2(A[1], A[0])
theta_c = math.atan2(C[1], C[0])
angle_arc = np.linspace(theta_a, theta_c, 30)
r = 0.9
ax.plot(r * np.cos(angle_arc), r * np.sin(angle_arc), 'purple', lw=1.5)
ax.text(1.1, 0.35, r'$\theta_C$', fontsize=12, color='purple')

ax.set_xlim(-1, 8)
ax.set_ylim(-1.5, 5.5)
ax.set_aspect('equal')
ax.grid(True, alpha=0.3)
ax.set_title('图1：矢量分解基本概念', fontsize=14, fontweight='bold')
ax.set_xlabel('x')
ax.set_ylabel('y')
plt.tight_layout()
plt.savefig('./figures/fig1_basic_concept.png', dpi=150)
plt.close()


# ========== 图2：余弦定理推导三角形 ==========
fig, ax = plt.subplots(1, 1, figsize=(8, 6))

# 画三角形：O -> A_end, A_end -> C, O -> C
C = np.array([6, 3])
# 选一个A使得好看
len_a, len_b, len_c = 5, 4, math.sqrt(36+9)
theta_c = math.atan2(3, 6)
cos_diff = (len_c**2 + len_a**2 - len_b**2) / (2 * len_a * len_c)
angle_diff = math.acos(cos_diff)
theta_a = theta_c - angle_diff
A = np.array([len_a * math.cos(theta_a), len_a * math.sin(theta_a)])

# 三角形
ax.annotate('', xy=A, xytext=(0,0),
            arrowprops=dict(arrowstyle='->', color='red', lw=2.5))
ax.annotate('', xy=C, xytext=A,
            arrowprops=dict(arrowstyle='->', color='green', lw=2.5))
ax.annotate('', xy=C, xytext=(0,0),
            arrowprops=dict(arrowstyle='->', color='blue', lw=2.5))

# 标注边长
mid_OA = A / 2
mid_AC = A + (C - A) / 2
mid_OC = C / 2

ax.text(mid_OA[0]-0.8, mid_OA[1]-0.3, f'|A|={len_a}', fontsize=12, color='red',
        fontweight='bold', rotation=math.degrees(theta_a))
ax.text(mid_AC[0]+0.2, mid_AC[1]+0.3, f'|B|={len_b}', fontsize=12, color='green',
        fontweight='bold')
ax.text(mid_OC[0]+0.1, mid_OC[1]-0.5, f'|C|={len_c:.2f}', fontsize=12, color='blue',
        fontweight='bold')

# 角度标注
r2 = 0.7
arc_a = np.linspace(0, theta_a, 30)
ax.plot(r2*np.cos(arc_a), r2*np.sin(arc_a), 'red', lw=1.5)
ax.text(0.7, -0.4, r'$\theta_A$', fontsize=12, color='red')

arc_c = np.linspace(0, theta_c, 30)
ax.plot(r2*1.3*np.cos(arc_c), r2*1.3*np.sin(arc_c), 'blue', lw=1.5)
ax.text(1.3, -0.15, r'$\theta_C$', fontsize=12, color='blue')

# 角度差标注
r3 = 1.1
arc_diff = np.linspace(theta_a, theta_c, 30)
ax.plot(r3*np.cos(arc_diff), r3*np.sin(arc_diff), 'purple', lw=2, linestyle='--')
ax.text(1.4, 0.6, r'$\alpha = \theta_C - \theta_A$', fontsize=11, color='purple')

ax.set_xlim(-1.5, 8)
ax.set_ylim(-2, 5)
ax.set_aspect('equal')
ax.grid(True, alpha=0.3)
ax.set_title('图2：余弦定理与三角形关系', fontsize=14, fontweight='bold')
ax.set_xlabel('x')
ax.set_ylabel('y')
plt.tight_layout()
plt.savefig('./figures/fig2_law_of_cosines.png', dpi=150)
plt.close()


# ========== 图3：两组解对比 ==========
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# 公共参数
len_a, len_b = 5, 7
c_x, c_y = 6, 8
len_c = math.sqrt(c_x**2 + c_y**2)
C = np.array([c_x, c_y])
theta_c = math.atan2(c_y, c_x)
cos_diff = (len_c**2 + len_a**2 - len_b**2) / (2 * len_a * len_c)
angle_diff = math.acos(cos_diff)

for idx, (sol_label, sign) in enumerate([('解0', -1), ('解1', +1)]):
    ax = axes[idx]
    theta_a = theta_c + sign * angle_diff
    A = np.array([len_a * math.cos(theta_a), len_a * math.sin(theta_a)])
    B = np.array([c_x - A[0], c_y - A[1]])

    ax.annotate('', xy=C, xytext=(0,0),
                arrowprops=dict(arrowstyle='->', color='blue', lw=2.5))
    ax.annotate('', xy=A, xytext=(0,0),
                arrowprops=dict(arrowstyle='->', color='red', lw=2.5))
    ax.annotate('', xy=A + B, xytext=A,
                arrowprops=dict(arrowstyle='->', color='green', lw=2.5))

    ax.text(A[0]/2 - 0.5, A[1]/2, r'$\vec{A}$', fontsize=15, color='red', fontweight='bold')
    mid_b = A + B/2
    ax.text(mid_b[0]+0.3, mid_b[1]+0.2, r'$\vec{B}$', fontsize=15, color='green', fontweight='bold')
    ax.text(C[0]/2 - 0.6, C[1]/2 + 0.3, r'$\vec{C}$', fontsize=15, color='blue', fontweight='bold')

    deg_a = math.degrees(theta_a) % 360
    deg_b = math.degrees(math.atan2(B[1], B[0])) % 360
    ax.set_title(f'{sol_label}: $\\theta_A={deg_a:.1f}°$, $\\theta_B={deg_b:.1f}°$',
                 fontsize=13, fontweight='bold')

    # 画三角形虚线
    triangle = np.array([[0,0], A, C, [0,0]])
    ax.plot(triangle[:,0], triangle[:,1], 'gray', lw=0.8, linestyle='--', alpha=0.5)

    ax.set_xlim(-9, 9)
    ax.set_ylim(-2, 11)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='k', lw=0.5)
    ax.axvline(x=0, color='k', lw=0.5)
    ax.set_xlabel('x')
    ax.set_ylabel('y')

plt.suptitle('图3：两组解对比（同一矢量可有两种分解方式）', fontsize=14, fontweight='bold', y=0.96)
plt.tight_layout()
plt.savefig('./figures/fig3_two_solutions.png', dpi=150)
plt.close()


# ========== 图4：三角形不等式可视化 ==========
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

cases = [
    ('有解：$|A|+|B| > |C|$', 5, 5, 7, True),
    ('临界：$|A|+|B| = |C|$', 3, 4, 7, True),
    ('无解：$|A|+|B| < |C|$', 2, 3, 10, False),
]

for i, (title, la, lb, lc, solvable) in enumerate(cases):
    ax = axes[i]
    # 简单情况：C沿x轴
    c_vec = np.array([lc, 0])
    theta_c = 0

    if solvable:
        cos_d = (lc**2 + la**2 - lb**2) / (2 * la * lc)
        cos_d = max(-1, min(1, cos_d))
        ad = math.acos(cos_d)
        ta = theta_c - ad
        A = np.array([la * math.cos(ta), la * math.sin(ta)])
        B = c_vec - A

        ax.annotate('', xy=c_vec, xytext=(0,0),
                    arrowprops=dict(arrowstyle='->', color='blue', lw=2))
        ax.annotate('', xy=A, xytext=(0,0),
                    arrowprops=dict(arrowstyle='->', color='red', lw=2))
        ax.annotate('', xy=c_vec, xytext=A,
                    arrowprops=dict(arrowstyle='->', color='green', lw=2))
        ax.text(A[0]/2, A[1]/2 + 0.4, f'|A|={la}', fontsize=10, color='red')
        ax.text((A[0]+c_vec[0])/2, (A[1]+c_vec[1])/2 + 0.4, f'|B|={lb}', fontsize=10, color='green')
    else:
            ax.annotate('', xy=c_vec, xytext=(0,0),
                        arrowprops=dict(arrowstyle='->', color='blue', lw=2))
            ax.annotate('', xy=(la, 0), xytext=(0,0),
                        arrowprops=dict(arrowstyle='->', color='red', lw=2))
            ax.text(la/2, 0.5, f'|A|={la}', fontsize=10, color='red')
            # 画圆弧表示B够不到
            circle = plt.Circle((la, 0), lb, fill=False, color='green', linestyle='--', lw=1.5)
            ax.add_patch(circle)
            ax.text(lc + 0.5, -1, f'无法到达\n|A|+|B|={la+lb} < |C|={lc}', fontsize=9, color='gray')

    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xlim(-2, 12)
    ax.set_ylim(-5, 5)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='k', lw=0.5)
    ax.axvline(x=0, color='k', lw=0.5)

plt.suptitle('图4：三角形不等式与可解性', fontsize=14, fontweight='bold', y=0.96)
plt.tight_layout()
plt.savefig('./figures/fig4_triangle_inequality.png', dpi=150)
plt.close()


# ========== 图5：连杆机构应用示例 ==========
fig, ax = plt.subplots(1, 1, figsize=(8, 6))

# 连杆机构
len_a, len_b = 100, 80
c_x, c_y = 120, 50
len_c = math.sqrt(c_x**2 + c_y**2)
theta_c = math.atan2(c_y, c_x)
cos_diff = (len_c**2 + len_a**2 - len_b**2) / (2 * len_a * len_c)
angle_diff = math.acos(cos_diff)

colors_sol = ['#e74c3c', '#3498db']
for idx, sign in enumerate([-1, +1]):
    theta_a = theta_c + sign * angle_diff
    A = np.array([len_a * math.cos(theta_a), len_a * math.sin(theta_a)])
    B = np.array([c_x - A[0], c_y - A[1]])

    lw = 3 if idx == 0 else 1.5
    alpha = 1.0 if idx == 0 else 0.5
    color = colors_sol[idx]

    # 连杆A
    ax.plot([0, A[0]], [0, A[1]], color=color, lw=lw, alpha=alpha, label=f'解{idx}' if idx > 0 else None)
    # 连杆B
    ax.plot([A[0], c_x], [A[1], c_y], color=color, lw=lw, alpha=alpha)
    # 关节点
    ax.plot(0, 0, 'ko', ms=8)
    ax.plot(A[0], A[1], 'o', color=color, ms=8)
    ax.plot(c_x, c_y, 's', color='blue', ms=10)

# 标注
ax.annotate('固定点 O', xy=(0,0), xytext=(-25, -15),
            fontsize=11, arrowprops=dict(arrowstyle='->', color='gray'))
ax.annotate(f'目标点 C({c_x},{c_y})', xy=(c_x, c_y), xytext=(c_x+5, c_y+10),
            fontsize=11, arrowprops=dict(arrowstyle='->', color='gray'))

# 运动轨迹弧
circle_a = plt.Circle((0, 0), len_a, fill=False, color='red', linestyle=':', lw=1, alpha=0.3)
circle_b = plt.Circle((c_x, c_y), len_b, fill=False, color='green', linestyle=':', lw=1, alpha=0.3)
ax.add_patch(circle_a)
ax.add_patch(circle_b)

ax.set_xlim(-30, 160)
ax.set_ylim(-80, 90)
ax.set_aspect('equal')
ax.grid(True, alpha=0.3)
ax.legend(fontsize=11, loc='lower right')
ax.set_title('图5：连杆机构应用（$|A|=100, |B|=80$）', fontsize=14, fontweight='bold')
ax.set_xlabel('x (mm)')
ax.set_ylabel('y (mm)')
plt.tight_layout()
plt.savefig('./figures/fig5_linkage_example.png', dpi=150)
plt.close()


# ========== 图6：特殊几何构型 ==========
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# 6a: 共线（同向）
ax = axes[0]
A1 = np.array([3, 0]); B1 = np.array([4, 0]); C1 = A1 + B1
ax.annotate('', xy=C1, xytext=(0,0), arrowprops=dict(arrowstyle='->', color='blue', lw=2))
ax.annotate('', xy=A1, xytext=(0,0), arrowprops=dict(arrowstyle='->', color='red', lw=2))
ax.annotate('', xy=C1, xytext=A1, arrowprops=dict(arrowstyle='->', color='green', lw=2))
ax.set_title('(a) 共线同向\n$\\theta_A = \\theta_B = \\theta_C$', fontsize=11, fontweight='bold')
ax.set_xlim(-1, 9); ax.set_ylim(-2, 2); ax.set_aspect('equal'); ax.grid(True, alpha=0.3)

# 6b: 共线（反向）- C=0
ax = axes[1]
A2 = np.array([5, 0]); B2 = np.array([-5, 0])
ax.annotate('', xy=A2, xytext=(0,0), arrowprops=dict(arrowstyle='->', color='red', lw=2))
ax.annotate('', xy=A2+B2, xytext=A2, arrowprops=dict(arrowstyle='->', color='green', lw=2))
ax.plot(0, 0, 'bo', ms=8)
ax.text(0.3, 0.5, r'$\vec{C}=\vec{0}$', fontsize=12, color='blue')
ax.set_title('(b) 等长反向\n$\\vec{A} + \\vec{B} = \\vec{0}$', fontsize=11, fontweight='bold')
ax.set_xlim(-7, 7); ax.set_ylim(-2, 2); ax.set_aspect('equal'); ax.grid(True, alpha=0.3)

# 6c: 等腰对称
ax = axes[2]
len_s = 5; cx = 8
ta_s = math.acos(cx / (2 * len_s))  # 对称，向上
A3 = np.array([len_s * math.cos(ta_s), len_s * math.sin(ta_s)])
B3 = np.array([len_s * math.cos(ta_s), -len_s * math.sin(ta_s)])
C3 = A3 + B3
ax.annotate('', xy=C3, xytext=(0,0), arrowprops=dict(arrowstyle='->', color='blue', lw=2))
ax.annotate('', xy=A3, xytext=(0,0), arrowprops=dict(arrowstyle='->', color='red', lw=2))
ax.annotate('', xy=C3, xytext=A3, arrowprops=dict(arrowstyle='->', color='green', lw=2))
ax.set_title('(c) 等腰对称\n$|A|=|B|=5$, $\\vec{C}=(8,0)$', fontsize=11, fontweight='bold')
ax.set_xlim(-1, 10); ax.set_ylim(-4, 4); ax.set_aspect('equal'); ax.grid(True, alpha=0.3)

for ax in axes:
    ax.axhline(y=0, color='k', lw=0.5)
    ax.axvline(x=0, color='k', lw=0.5)

plt.suptitle('图6：特殊几何构型', fontsize=14, fontweight='bold', y=0.96)
plt.tight_layout()
plt.savefig('./figures/fig6_special_cases.png', dpi=150)
plt.close()

print("All figures generated successfully!")