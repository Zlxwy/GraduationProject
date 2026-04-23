import cv2
import numpy as np
import math

# --------------------------------------数学计算函数---------------------------------------

def compute_homography(pts_src: np.ndarray, pts_dst: np.ndarray) -> np.ndarray:
  A = []
  for (x1, y1), (x2, y2) in zip(pts_src, pts_dst):
    A.append([-x1, -y1, -1, 0, 0, 0, x1*x2, y1*x2, x2])
    A.append([0, 0, 0, -x1, -y1, -1, x1*y2, y1*y2, y2])
  A = np.array(A, dtype=np.float64)
  _, _, Vh = np.linalg.svd(A)
  h = Vh[-1].reshape(3, 3)
  return h / h[2, 2]

def transform_point(pt: tuple, H: np.ndarray) -> tuple:
  x, y = pt
  vec = np.array([x, y, 1.0], dtype=np.float64)
  res = H @ vec
  return (float(res[0]/res[2]), float(res[1]/res[2]))

def transform_points(pts: list, H: np.ndarray) -> list:
  return [transform_point(p, H) for p in pts]





# --------------------------------------画图函数---------------------------------------

def DrawIrregularQuad(img, pts, color, thickness):
  """
  绘制不规则四边形（修复了顶点排序逻辑）
  img: 目标图像
  pts: 四个顶点的CV坐标系坐标，按照CV坐标系的左上、右上、右下、左下的顺序排列
  color: 线条颜色
  thickness: 线条粗细
  """
  ptTL, ptTR, ptBR, ptBL = pts # 左上、右上、右下、左下
  cv2.line(img, ptTL, ptTR, color, thickness)
  cv2.line(img, ptTR, ptBR, color, thickness)
  cv2.line(img, ptBR, ptBL, color, thickness)
  cv2.line(img, ptBL, ptTL, color, thickness)



def DrawTable_Perspective(img, pts, rows, cols, color, thickness):
  """
  绘制带透视变换表格的四边形
  img: 目标图像
  pts: 四个顶点的CV坐标系坐标，按照CV坐标系的左上、右上、右下、左下的顺序排列
  rows: 表格行数
  cols: 表格列数
  color: 线条颜色
  thickness: 线条粗细
  """
  ptTL, ptTR, ptBR, ptBL = np.float32(pts)
  DrawIrregularQuad(img, pts, color, thickness)
  arm_width = cols
  arm_height = rows
  std_TL = np.float32([0, arm_height])
  std_TR = np.float32([arm_width, arm_height])
  std_BR = np.float32([arm_width, 0])
  std_BL = np.float32([0, 0])
  H_std2img = compute_homography([std_TL, std_TR, std_BR, std_BL], [ptTL, ptTR, ptBR, ptBL])
  for r in range(rows + 1):
    y_arm = rows - r
    p_left_arm = (0, y_arm)
    p_right_arm = (arm_width, y_arm)
    p_left_img = transform_point(p_left_arm, H_std2img)
    p_right_img = transform_point(p_right_arm, H_std2img)
    cv2.line(img, (int(p_left_img[0]), int(p_left_img[1])),
      (int(p_right_img[0]), int(p_right_img[1])), color, thickness)
  for c in range(cols + 1):
    x_arm = c
    p_top_arm = (x_arm, arm_height)
    p_bottom_arm = (x_arm, 0)
    p_top_img = transform_point(p_top_arm, H_std2img)
    p_bottom_img = transform_point(p_bottom_arm, H_std2img)
    cv2.line(img, (int(p_top_img[0]), int(p_top_img[1])),
      (int(p_bottom_img[0]), int(p_bottom_img[1])), color, thickness)



def DrawTable_Uniform(img, pts, rows, cols, color, thickness):
  """
  绘制带均匀表格的四边形（修复了顶点排序逻辑）
  img: 目标图像
  pts: 四个顶点的CV坐标系坐标，按照CV坐标系的左上、右上、右下、左下的顺序排列
  rows: 表格行数
  cols: 表格列数
  color: 线条颜色
  thickness: 线条粗细
  """
  DrawIrregularQuad(img, pts, color, thickness)
  ptTL, ptTR, ptBR, ptBL = pts # 左上、右上、右下、左下
  ptTL, ptTR, ptBR, ptBL = np.float32([ptTL, ptTR, ptBR, ptBL]) # 将点转换为浮点数以便进行插值计算
  for r in range(1, rows): # 循环绘制内部的行线 (横向分割)
    # 从 1 到 rows-1，因为 0 和 rows 已经是外边框了
    # 计算当前行在左边框和右边框上的位置
    alpha_r = r / float(rows) # alpha_r 是比例因子 (0.0 ~ 1.0)
    pt_left = ptTL + (ptBL - ptTL) * alpha_r # 线性插值：计算左边框上的点 (从TL到BL)
    pt_right = ptTR + (ptBR - ptTR) * alpha_r # 线性插值：计算右边框上的点 (从TR到BR)
    cv2.line(img, tuple(pt_left.astype(int)), tuple(pt_right.astype(int)), color, thickness) # 绘制横线
  for c in range(1, cols): # 循环绘制内部的列线 (纵向分割)
    # 从 1 到 cols-1，因为 0 和 cols 已经是外边框了
    # 计算当前列在上边框和下边框上的位置
    alpha_c = c / float(cols) # alpha_c 是比例因子 (0.0 ~ 1.0)
    pt_top = ptTL + (ptTR - ptTL) * alpha_c # 上边框 (从TL到TR)
    pt_bottom = ptBL + (ptBR - ptBL) * alpha_c # 下边框 (从BL到BR)
    cv2.line(img, tuple(pt_top.astype(int)), tuple(pt_bottom.astype(int)), color, thickness) # 绘制竖线



def get_intersection_point(line1, line2) -> tuple[int,int]:
  """
  brief:
    计算两条直线的交点，无论是笛卡尔坐标系坐标，还是CV坐标系坐标，都可以计算。
  line1: 第一个线段，格式为 ((x1, y1), (x2, y2))
  line2: 第二个线段，格式为 ((x3, y3), (x4, y4))
  return:
    如果两条线平行则返回 None,None，否则返回交点坐标 ix, iy
  """
  x1, y1 = line1[0]
  x2, y2 = line1[1]
  x3, y3 = line2[0]
  x4, y4 = line2[1]
  denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
  if abs(denom) < 1e-9: return None,None # 用极小值判断，避免浮点数精度问题
  det1 = (x1 * y2 - y1 * x2)
  det2 = (x3 * y4 - y3 * x4)
  ix = (det1 * (x3 - x4) - (x1 - x2) * det2) / denom
  iy = (det1 * (y3 - y4) - (y1 - y2) * det2) / denom
  return int(ix), int(iy)



def DrawIntersectionPointOfTable_Perspective(img, pts, rows, cols, color, radius, thickness):
  """
  brief:
    绘制透视变换表格四边形的交点，与函数DrawTable_Perspective是对应的
  img: 目标图像
  pts: 四个顶点的CV坐标系坐标，按照CV坐标系的左上、右上、右下、左下的顺序排列
  rows: 表格行数
  cols: 表格列数
  color: 线条颜色
  thickness: 线条粗细
  """
  ptTL, ptTR, ptBR, ptBL = np.float32(pts)
  # 标准网格参数（和画线函数完全一致）
  arm_width = cols
  arm_height = rows
  std_TL = np.float32([0, arm_height])
  std_TR = np.float32([arm_width, arm_height])
  std_BR = np.float32([arm_width, 0])
  std_BL = np.float32([0, 0])
  # 计算透视变换矩阵
  H_std2img = compute_homography([std_TL, std_TR, std_BR, std_BL], [ptTL, ptTR, ptBR, ptBL])
  # 遍历所有交点：(rows+1)行 × (cols+1)列
  for r in range(rows + 1):
    for c in range(cols + 1):
      # 标准坐标系下的交点
      x_arm = c
      y_arm = rows - r
      pt_arm = (x_arm, y_arm)
      # 透视变换到图像坐标
      pt_img = transform_point(pt_arm, H_std2img)
      ix, iy = int(round(pt_img[0])), int(round(pt_img[1]))
      # 绘制圆点
      cv2.circle(img, (ix, iy), radius, color, thickness)



def DrawIntersectionPointOfTable_Uniform(img, pts, rows, cols, color, radius, thickness):
  """
  brief:
    绘制均匀表格四边形的交点，与函数DrawTable_Uniform是对应的
  img: 目标图像
  pts: 四个顶点的CV坐标系坐标，按照CV坐标系的左上、右上、右下、左下的顺序排列
  rows: 表格行数
  cols: 表格列数
  color: 线条颜色
  thickness: 线条粗细
  """
  ptTL, ptTR, ptBR, ptBL = pts # 左上、右上、右下、左下
  ptTL, ptTR, ptBR, ptBL = np.float32([ptTL, ptTR, ptBR, ptBL]) # 将点转换为浮点数以便进行插值计算
  for r in range(0, rows+1): # 循环绘制内部的行线 (横向分割)
    alpha_r = r / float(rows) # alpha_r 是比例因子 (0.0 ~ 1.0)
    pt_left = ptTL + (ptBL - ptTL) * alpha_r # 线性插值：计算左边框上的点 (从TL到BL)
    pt_right = ptTR + (ptBR - ptTR) * alpha_r # 线性插值：计算右边框上的点 (从TR到BR)
    for c in range(0, cols+1): # 循环绘制内部的列线 (纵向分割)
      alpha_c = c / float(cols) # alpha_c 是比例因子 (0.0 ~ 1.0)
      pt_top = ptTL + (ptTR - ptTL) * alpha_c # 上边框 (从TL到TR)
      pt_bottom = ptBL + (ptBR - ptBL) * alpha_c # 下边框 (从BL到BR)
      line1 = (tuple(pt_left.astype(int)), tuple(pt_right.astype(int)))
      line2 = (tuple(pt_top.astype(int)), tuple(pt_bottom.astype(int)))
      ix, iy = get_intersection_point(line1, line2)
      if ix is not None and iy is not None:
        cv2.circle(img, (ix,iy), radius, color, thickness)



def GetAllIntersectionPointOfTable_Perspective(pts, rows, cols):
  """
  brief:
    获取透视变换四边形表格的所有交点，与函数DrawIntersectionPointOfTable_Perspective是对应的。
  pts: 四个顶点的CV坐标系坐标，按照CV坐标系的左上、右上、右下、左下的顺序排列
  rows: 表格行数
  cols: 表格列数
  return:
    其返回的数据结构为 = [
      [ [左上点x,左上点y], ... , [右上点x,右上点y] ],
      [ [x,y], [x,y], ............ , [x,y], [x,y] ],
      [ [x,y], [x,y], ............ , [x,y], [x,y] ],
      [ [x,y], [x,y], ............ , [x,y], [x,y] ],
      [ [左下点x,左下点y], ... , [右下点x,右下点y] ]
    ]
    其维度和行列有关，为 (rows+1, cols+1, 2)
  """
  ptTL, ptTR, ptBR, ptBL = np.float32(pts)
  # 标准网格参数
  arm_width = cols
  arm_height = rows
  std_TL = np.float32([0, arm_height])
  std_TR = np.float32([arm_width, arm_height])
  std_BR = np.float32([arm_width, 0])
  std_BL = np.float32([0, 0])
  # 透视矩阵
  H_std2img = compute_homography([std_TL, std_TR, std_BR, std_BL], [ptTL, ptTR, ptBR, ptBL])
  # 生成所有交点
  points = []
  for r in range(rows + 1):
    row_points = []
    for c in range(cols + 1):
      x_arm = c
      y_arm = rows - r
      pt_img = transform_point((x_arm, y_arm), H_std2img)
      # 取整（OpenCV 坐标必须是整数）
      row_points.append([int(round(pt_img[0])), int(round(pt_img[1]))])
    points.append(row_points)
  return points



def GetAllIntersectionPointOfTable_Uniform(pts, rows, cols):
  """
  brief:
    获取均匀四边形表格的所有交点，与函数DrawIntersectionPointOfTable_Uniform是对应的。
  pts: 四个顶点的CV坐标系坐标，按照CV坐标系的左上、右上、右下、左下的顺序排列
  rows: 表格行数
  cols: 表格列数
  return:
    其返回的数据结构为 = [
      [ [左上点x,左上点y], ... , [右上点x,右上点y] ],
      [ [x,y], [x,y], ............ , [x,y], [x,y] ],
      [ [x,y], [x,y], ............ , [x,y], [x,y] ],
      [ [x,y], [x,y], ............ , [x,y], [x,y] ],
      [ [左下点x,左下点y], ... , [右下点x,右下点y] ]
    ]
    其维度和行列有关，为 (rows+1, cols+1, 2)
  """
  pts = np.array(pts, dtype=np.float32)
  TL, TR, BR, BL = pts[0], pts[1], pts[2], pts[3]
  v = np.linspace(0, 1, rows + 1)  # 垂直方向（上下）
  u = np.linspace(0, 1, cols + 1)  # 水平方向（左右）
  uu, vv = np.meshgrid(u, v)  # 去掉 ij，默认 xy 模式，最适合OpenCV图像
  uu = uu[..., None]
  vv = vv[..., None]
  points = (1-uu)*(1-vv)*TL + uu*(1-vv)*TR + uu*vv*BR + (1-uu)*vv*BL # 双线性插值（不规则四边形专用）
  points = np.round(points).astype(np.int32) # 转整数，OpenCV可用
  return points.tolist()



def find_nearest_intersection(target_point, intersection_list):
  """
  输入：
    target_point: 你鼠标点的坐标 (x, y)
    intersection_list: 你的交点列表 (rows, cols, 2)
  输出：
    nearest_point: 最近的交点 (x, y)
    distance: 距离（可选）
    row_idx, col_idx: 在网格中的行列号（超级有用！）
  """
  min_dist = float('inf')
  nearest_point = None
  nearest_row = -1
  nearest_col = -1

  # 遍历所有网格交点
  for i, row in enumerate(intersection_list):
    for j, (x, y) in enumerate(row):
      # 计算欧氏距离
      dx = target_point[0] - x
      dy = target_point[1] - y
      dist = math.sqrt(dx*dx + dy*dy)

      # 记录最小距离
      if dist < min_dist:
        min_dist = dist
        nearest_point = (x, y)
        nearest_row = i
        nearest_col = j

  return nearest_point, min_dist, nearest_row, nearest_col



def is_point_in_quad(point, quad):
  def cross(o,a,b):
    return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
  p1,p2,p3,p4 = quad
  c1 = cross(p1,p2,point)
  c2 = cross(p2,p3,point)
  c3 = cross(p3,p4,point)
  c4 = cross(p4,p1,point)

  all_positive = (c1>=0) and (c2>=0) and (c3>=0) and (c4>=0)  # 全正：在内侧
  all_negative = (c1<=0) and (c2<=0) and (c3<=0) and (c4<=0)  # 全负：也在内侧

  return all_positive or all_negative



def find_diff_position_in_two_chessboard(chessboard1, chessboard2):
  """
  输入：
    chessboard1: 第一个棋盘的棋子二维列表
    chessboard2: 第二个棋盘的棋子二维列表
    两个列表的维度要一致
  输出：
    diff_positions: 两个棋盘不同位置棋子所在行列的列表
    如果有n个不同位置的棋子，返回数据结构为 [ [row1_idx, col1_idx], ... , [rown_idx, coln_idx] ]
    如果没有不同位置的棋子，返回None
  """
  diffs = []
  rows = len(chessboard1)
  cols = len(chessboard1[0])
  for i in range(rows):
    for j in range(cols):
      if chessboard1[i][j] != chessboard2[i][j]:
        diffs.append([i,j])
  if diffs: return diffs
  else: return None
  


# if __name__ == '__main__':
#   is_pressed = False
#   cv2.namedWindow('black_frame') # 创建名为"black_frame"的窗口
#   cv2.setMouseCallback("black_frame", mouse_callback)
#   print("按ESC键退出程序")
#   while True:
#     black_frame = np.zeros((1080, 1080, 3), dtype=np.uint8)
#     if LButtonDownFlag: # 如果左键按下标志位触发
#       LButtonDownFlag = False # 清除左键按下标志位
#       is_pressed = True # 设置按下状态
#       mark_point = (mouse_x, mouse_y) # 记录当前鼠标位置
#     elif LButtonUpFlag: # 如果左键释放标志位触发
#       LButtonUpFlag = False # 清除左键释放标志位
#       is_pressed = False # 清除按下状态
#     else: pass
#     if is_pressed:
#       pts = (
#         (100, 200),
#         (666, 250),
#         (666, 800),
#         (mouse_x, mouse_y)
#       )
#       DrawTable_Perspective(
#         black_frame, # 黑板底图
#         pts,
#         rows=9, cols=8, 
#         color=(0,255,0),
#         thickness=2
#       ) # 调用函数绘制带均匀表格的矩形
#       DrawTablePlus_DrawIntersectionPoint(
#         black_frame, # 黑板底图
#         pts,
#         rows=9, cols=8,
#         color=(0,255,0),
#         radius=10,
#         thickness=2
#       )
#     cv2.imshow('black_frame', black_frame) # 在窗口中显示黑色帧
#     PressKey = cv2.waitKey(10) & 0xFF
#     if PressKey & 0xFF == 27: # 如果按下ESC键
#       break # 退出循环
#   cv2.destroyAllWindows() # 关闭所有窗口
#   print("程序退出")













def decompose_vector(len_a: float, len_b: float, c_x: float, c_y: float, solution: int=0):
  """
  在笛卡尔平面坐标系中，已知矢量A、B的长度和矢量C的坐标，
  求解满足 C = A + B 的矢量A和B的角度。
  参数:
    len_a: 矢量A的长度（必须为正数）
    len_b: 矢量B的长度（必须为正数）
    c_x: 矢量C的x坐标
    c_y: 矢量C的y坐标
    solution: 解的选择，0或1
              0 - 选择矢量A角度 <= 矢量B角度的解
              1 - 选择矢量A角度 > 矢量B角度的解
  返回:
    tuple: (angle_a, angle_b) 矢量A和B的角度（单位：度，范围 [0, 360)）
  异常:
    ValueError: 当输入参数无效或无解时抛出
  """
  if len_a <= 0 or len_b <= 0: raise ValueError("矢量长度必须为正数") # 参数验证
  if solution not in (0, 1): raise ValueError("solution 参数必须是 0 或 1")
  len_c = math.sqrt(c_x**2 + c_y**2) # 计算矢量C的长度和角度
  if len_c == 0: # 特殊情况：C为零矢量
    if abs(len_a - len_b) < 1e-10: # 无穷多解
      # 返回两个相反方向的角度
      if solution == 0: return (0.0, 180.0)
      else: return (180.0, 0.0)
    else: raise ValueError("C为零矢量时，A和B必须等长")
  theta_c = math.atan2(c_y, c_x) # 矢量C的角度
  cos_diff = (len_c**2 + len_a**2 - len_b**2) / (2 * len_a * len_c) # 使用余弦定理求解角度差 cos(θ_C - θ_A) = (|C|² + |A|² - |B|²) / (2|A||C|)
  if cos_diff < -1 - 1e-10 or cos_diff > 1 + 1e-10: # 检查是否有解（三角形不等式）
    raise ValueError(
      f"无解：给定的矢量长度不满足三角形不等式。\n"
      f"需要 |{len_a:.2f} - {len_b:.2f}| <= {len_c:.2f} <= {len_a:.2f} + {len_b:.2f}"
    )
  cos_diff = max(-1.0, min(1.0, cos_diff)) # 限制在有效范围内
  angle_diff = math.acos(cos_diff) # 角度差
  theta_a1 = theta_c - angle_diff  # θ_A = θ_C - arccos(...)
  theta_a2 = theta_c + angle_diff  # θ_A = θ_C + arccos(...)
  # B = C - A，所以 θ_B = atan2(B_y, B_x)
  def calc_angle_b(theta_a): # 计算对应的B的角度
    a_x = len_a * math.cos(theta_a)
    a_y = len_a * math.sin(theta_a)
    b_x = c_x - a_x
    b_y = c_y - a_y
    return math.atan2(b_y, b_x)

  theta_b1 = calc_angle_b(theta_a1)
  theta_b2 = calc_angle_b(theta_a2)

  def to_degrees(angle_rad): # 转换为度数 [0, 360)
    angle_deg = math.degrees(angle_rad)
    return angle_deg % 360

  angle_a1 = to_degrees(theta_a1)
  angle_b1 = to_degrees(theta_b1)
  angle_a2 = to_degrees(theta_a2)
  angle_b2 = to_degrees(theta_b2)

  def cal_angle_diff(zero_degree: float, curr_degree: float, area: float) -> float:
    """
    以 a1 为 0 参考角度，将 a2 转换为极坐标轴上的角度
    与原 C 语言 fmodf 逻辑完全等价
    """
    diff = curr_degree - zero_degree
    value = diff + area * 3.0
    mod = math.fmod(value, area * 2.0)  # Python fmod 对应 C fmodf
    return mod - area

  # 根据solution选择解
  if solution == 0:
    # 选择 angle_a 为零度时，angle_b 为正数角度的解，即 angle_a <= angle_b 的解
    if cal_angle_diff(angle_a1, angle_b1, 180) >= 0:
      return (angle_a1, angle_b1)
    else:
      return (angle_a2, angle_b2)
  else:
    # 选择 angle_a 为零度时，angle_b 为负数角度的解，即 angle_a  > angle_b 的解
    if cal_angle_diff(angle_a1, angle_b1, 180) < 0:
      return (angle_a1, angle_b1)
    else:
      return (angle_a2, angle_b2)
