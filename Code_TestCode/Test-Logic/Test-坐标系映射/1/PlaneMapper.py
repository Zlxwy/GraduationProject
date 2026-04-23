import numpy as np

def compute_homography(pts_src: np.ndarray, pts_dst: np.ndarray) -> np.ndarray:
    """
    计算单应矩阵 H，满足 pts_dst ≈ H @ pts_src
    pts_src, pts_dst: shape (4, 2)
    返回 H: (3,3)
    """
    A = []
    for (x1, y1), (x2, y2) in zip(pts_src, pts_dst):
        A.append([-x1, -y1, -1, 0, 0, 0, x1*x2, y1*x2, x2])
        A.append([0, 0, 0, -x1, -y1, -1, x1*y2, y1*y2, y2])
    A = np.array(A, dtype=np.float64)

    _, _, Vh = np.linalg.svd(A)
    h = Vh[-1].reshape(3, 3)
    return h / h[2, 2]

def transform_point(pt: tuple, H: np.ndarray) -> tuple:
    """单点变换：pt (x,y) → 变换后坐标"""
    x, y = pt
    vec = np.array([x, y, 1.0], dtype=np.float64)
    res = H @ vec
    return (float(res[0]/res[2]), float(res[1]/res[2]))

def transform_points(pts: list, H: np.ndarray) -> list:
    """批量点变换"""
    return [transform_point(p, H) for p in pts]

class PlaneMapper:
    def __init__(self, rect_a: list, rect_b: list):
        """
        一次初始化，终身使用
        rect_a: 平面A 4点 [左上,右上,右下,左下]
        rect_b: 平面B 对应4点
        """
        # 格式转换
        self.pts_a = np.array(rect_a, dtype=np.float64)
        self.pts_b = np.array(rect_b, dtype=np.float64)

        # 校验输入
        assert self.pts_a.shape == (4,2), "rect_a 必须是4个2D点"
        assert self.pts_b.shape == (4,2), "rect_b 必须是4个2D点"

        # 计算正反单应矩阵
        self.H_ab = compute_homography(self.pts_a, self.pts_b)
        self.H_ba = np.linalg.inv(self.H_ab)  # 逆变换 B→A

    def a_to_b(self, pt_a: tuple) -> tuple:
        """A坐标 → B坐标"""
        return transform_point(pt_a, self.H_ab)

    def b_to_a(self, pt_b: tuple) -> tuple:
        """B坐标 → A坐标"""
        return transform_point(pt_b, self.H_ba)

    def batch_a_to_b(self, pts_a: list) -> list:
        return transform_points(pts_a, self.H_ab)

    def batch_b_to_a(self, pts_b: list) -> list:
        return transform_points(pts_b, self.H_ba)

    def check_precision(self) -> float:
        """精度自检：4个角点重投影误差均值，越小越准，一般<0.01就是完美"""
        pts_a_pred = self.batch_b_to_a(self.pts_b.tolist())
        errors = np.linalg.norm(self.pts_a - np.array(pts_a_pred), axis=1)
        return float(np.mean(errors))