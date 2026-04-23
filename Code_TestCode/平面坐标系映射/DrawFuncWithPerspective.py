import numpy as np
import math
import cv2

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