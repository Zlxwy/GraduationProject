import numpy as np
import cv2
import math
import numpy as np



def DrawIrregularQuad(img, pts, color, thickness):
  ptTL, ptTR, ptBR, ptBL = pts # 左上、右上、右下、左下
  cv2.line(img, ptTL, ptTR, color, thickness)
  cv2.line(img, ptTR, ptBR, color, thickness)
  cv2.line(img, ptBR, ptBL, color, thickness)
  cv2.line(img, ptBL, ptTL, color, thickness)



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



mouse_x = 0
mouse_y = 0
LButtonDownFlag = False
MouseMoveFlag = False
LButtonUpFlag = False

def mouse_callback(event, x, y, flags, param):
  global mouse_x, mouse_y, LButtonDownFlag, MouseMoveFlag, LButtonUpFlag
  mouse_x = x
  mouse_y = y
  if event == cv2.EVENT_LBUTTONDOWN: LButtonDownFlag = True # 鼠标左键按下
  if event == cv2.EVENT_MOUSEMOVE: MouseMoveFlag = True # 鼠标移动 
  if event == cv2.EVENT_LBUTTONUP: LButtonUpFlag = True # 鼠标左键释放



# 在画面的CV坐标系中，四边形的四个顶点坐标
CvPlane_Rect_TopLeft = [50,50]
CvPlane_Rect_TopRight = [200,50]
CvPlane_Rect_BottomRight = [200,200]
CvPlane_Rect_BottomLeft = [50,200]
CvPlane_ChangeRef = None
# 在机械臂坐标系中，四边形的四个顶点坐标
ArmPlane_Rect_TopLeft = [0,9]
ArmPlane_Rect_TopRight = [8,9]
ArmPlane_Rect_BottomRight = [8,0]
ArmPlane_Rect_BottomLeft = [0,0]

def main():
  global mouse_x, mouse_y, LButtonDownFlag, MouseMoveFlag, LButtonUpFlag
  global CvPlane_Rect_TopLeft, CvPlane_Rect_TopRight, CvPlane_Rect_BottomRight, CvPlane_Rect_BottomLeft
  global CvPlane_ChangeRef
  global ArmPlane_Rect_TopLeft, ArmPlane_Rect_TopRight, ArmPlane_Rect_BottomRight, ArmPlane_Rect_BottomLeft

  cap = cv2.VideoCapture(1)
  if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()
  cv2.namedWindow("Frame")
  cv2.setMouseCallback("Frame", mouse_callback)

  is_pressed = False
  while True:
    ret, frame = cap.read()
    if not ret:
      print("Error: Could not read frame.")
      break

    if LButtonDownFlag:
      LButtonDownFlag = False
      is_pressed = True
      mx = mouse_x
      my = mouse_y
      DisRefToTopLeft = math.dist((mx,my), CvPlane_Rect_TopLeft)
      DisRefToTopRight = math.dist((mx,my), CvPlane_Rect_TopRight)
      DisRefToBottomRight = math.dist((mx,my), CvPlane_Rect_BottomRight)
      DisRefToBottomLeft = math.dist((mx,my), CvPlane_Rect_BottomLeft)
      EffectiveRadius = 20.0 # 有效半径
      if DisRefToTopLeft < EffectiveRadius: CvPlane_ChangeRef = CvPlane_Rect_TopLeft
      if DisRefToTopRight <= DisRefToTopLeft and DisRefToTopRight < EffectiveRadius: CvPlane_ChangeRef = CvPlane_Rect_TopRight
      if DisRefToBottomRight <= DisRefToTopRight and DisRefToBottomRight < EffectiveRadius: CvPlane_ChangeRef = CvPlane_Rect_BottomRight
      if DisRefToBottomLeft <= DisRefToBottomRight and DisRefToBottomLeft < EffectiveRadius: CvPlane_ChangeRef = CvPlane_Rect_BottomLeft
    elif LButtonUpFlag:
      LButtonUpFlag = False
      is_pressed = False
      CvPlane_ChangeRef = None
    else: pass

    if is_pressed and MouseMoveFlag:
      if CvPlane_ChangeRef is not None:
        CvPlane_ChangeRef[0] = mouse_x
        CvPlane_ChangeRef[1] = mouse_y
    
    draw_color = (255,0,0)
    text_color = (0,255,0)
    DrawTable_Perspective(frame, [CvPlane_Rect_TopLeft, CvPlane_Rect_TopRight, CvPlane_Rect_BottomRight, CvPlane_Rect_BottomLeft], 9, 8, draw_color, 2)
    DrawIntersectionPointOfTable_Perspective(frame, [CvPlane_Rect_TopLeft, CvPlane_Rect_TopRight, CvPlane_Rect_BottomRight, CvPlane_Rect_BottomLeft], 9, 8, draw_color, 6, 2)
    point_grid = GetAllIntersectionPointOfTable_Perspective([CvPlane_Rect_TopLeft, CvPlane_Rect_TopRight, CvPlane_Rect_BottomRight, CvPlane_Rect_BottomLeft], 9, 8)
    for i,row in enumerate(point_grid):
      for j,pt in enumerate(row):
        cv2.circle(frame, pt, 3, draw_color, 2)
        cv2.putText(frame, f"{i*len(row)+j}", pt, cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)



    cv2.circle(frame, CvPlane_Rect_TopLeft, 10, draw_color, 2)
    cv2.circle(frame, CvPlane_Rect_TopRight, 10, draw_color, 2)
    cv2.circle(frame, CvPlane_Rect_BottomRight, 10, draw_color, 2)
    cv2.circle(frame, CvPlane_Rect_BottomLeft, 10, draw_color, 2)
    cv2.putText(frame, "TL", CvPlane_Rect_TopLeft, cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
    cv2.putText(frame, "TR", CvPlane_Rect_TopRight, cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
    cv2.putText(frame, "BR", CvPlane_Rect_BottomRight, cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)
    cv2.putText(frame, "BL", CvPlane_Rect_BottomLeft, cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)

    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) == ord('\x1b'):
      break

if __name__ == "__main__":
  main()