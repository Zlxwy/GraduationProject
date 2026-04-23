# 绘制双连杆的两条线段
import cv2
import math
import numpy as np

frame_width = 1080
frame_height = 1080



"""
计算从点pt_start出发，长度为length，角度为angle_deg的线段的结束点
:param pt_start: 起始点 (x1, y1)
:param length: 线段长度
:param angle_deg: 角度（度）
:return: 移动距离 (dx, dy)
"""
def calculate_dx_dy(pt_start, length, angle_deg) -> tuple[float,float]:
  if angle_deg >= 0 and angle_deg < 360:
    angle_rad = math.radians(angle_deg) # 将角度转换为弧度
    dx = length * math.cos(angle_rad) # 计算x方向上的移动距离
    dy = length * math.sin(angle_rad) # 计算y方向上的移动距离
    return dx, dy
  else:
    raise ValueError(f"角度必须在0到360度之间，但是传入了个{angle_deg}度")






def CoordOnCartesianToCv(cart_point, cv_origin_on_cart_plane):
  """
  将笛卡尔坐标系的点，转换为OpenCV坐标系的点
  :param cart_point: 笛卡尔坐标系的点 (x, y)
  :param cv_origin_on_cart_plane: OpenCV坐标系原点在笛卡尔坐标系中的位置
  :return: OpenCV的点 (x, y)
  """
  cv_point = (
    cart_point[0] - cv_origin_on_cart_plane[0],
    cv_origin_on_cart_plane[1] - cart_point[1]
  )
  return cv_point

def CoordOnCvToCartesian(cv_point: tuple[int,int], cart_origin_on_cv_plane: tuple[int,int]) -> tuple[int,int]:
  """
  将OpenCV坐标系的点，转换为笛卡尔坐标系的点
  :param cv_point: 待转换的CV坐标系上的点坐标
  :param cart_origin_on_cv_plane: 笛卡尔坐标系原点在OpenCV坐标系中的位置
  :return: 笛卡尔坐标系的点 (x, y)
  """
  cart_point = (
    cv_point[0] - cart_origin_on_cv_plane[0],
    cart_origin_on_cv_plane[1] - cv_point[1]
  )
  return cart_point




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





"""
绘制双连杆（此函数深度绑定于自己写的calculate_dx_dy和CoordOnCartesianToCv函数，仅做测试用）
:param img: 要绘制的图像
:param pt_origin: 连杆的起点，笛卡尔坐标系
:param line1_length: 连杆A的长度
:param line1_angle_deg: 连杆A的角度（度），极坐标系，0度为x轴正方向，顺时针旋转0度为正方向
:param line2_length: 连杆B的长度
:param line2_angle_deg: 连杆B的角度（度）
"""
def MyDrawTwoLine(img, pt_origin, line1_length, line1_angle_deg, line2_length, line2_angle_deg):
  line1_pt_start = pt_origin
  line1_dx, line1_dy = calculate_dx_dy(line1_pt_start, line1_length, line1_angle_deg)
  line1_dx = round(line1_dx) # 四舍五入到最近的整数
  line1_dy = round(line1_dy) # 四舍五入到最近的整数
  line1_pt_end = ( line1_pt_start[0]+line1_dx, line1_pt_start[1]+line1_dy ) # 计算结束点
  
  line2_pt_start = line1_pt_end
  line2_dx, line2_dy = calculate_dx_dy(line2_pt_start, line2_length, line2_angle_deg)
  line2_dx = round(line2_dx) # 四舍五入到最近的整数
  line2_dy = round(line2_dy) # 四舍五入到最近的整数
  line2_pt_end = ( line2_pt_start[0]+line2_dx, line2_pt_start[1]+line2_dy ) # 计算结束点

  line1_pt_start = CoordOnCartesianToCv(line1_pt_start, (0,frame_height-1))
  line1_pt_end = CoordOnCartesianToCv(line1_pt_end, (0,frame_height-1))
  line2_pt_start = CoordOnCartesianToCv(line2_pt_start, (0,frame_height-1))
  line2_pt_end = CoordOnCartesianToCv(line2_pt_end, (0,frame_height-1))

  cv2.line(img, line1_pt_start, line1_pt_end, (0,255,0), 2) # 绘制线段1
  cv2.line(img, line2_pt_start, line2_pt_end, (0,255,0), 2) # 绘制线段2





def main():
  cv2.namedWindow('black_frame') # 创建名为"black_frame"的窗口
  print("按ESC键退出程序")

  angle_step = 1 # 角度步长，每次增加2度
  angle_step_cnt = 0 # 角度步长计数器，初始值为0
  angle_step_cnt_forward = 1 # 角度步长方向，初始值为1，表示向角度增加方向移动

  coord_step = 1 # 坐标步长，每次增加1像素
  target_x = 240 # 目标点X坐标，初始值为240
  target_y = 140 # 目标点Y坐标，初始值为540

  while True:
    black_frame = np.zeros((1080, 1080, 3), dtype=np.uint8)



    # # 在画布中绘制发散线段
    # pt_start = (540, 540) # 发散起始点
    # length = 200 # 发散线段长度
    # for angle_deg in range(0,360,int(360/24)): # 遍历角度，每次增加360/24度
    #   dx, dy = calculate_dx_dy(pt_start, length, angle_deg) # 计算移动距离
    #   dx = round(dx) # 四舍五入到最近的整数
    #   dy = round(dy) # 四舍五入到最近的整数
    #   pt_end = ( pt_start[0]+dx, pt_start[1]+dy ) # 计算结束点
    #   cv2.line(black_frame, pt_start, pt_end, (0,255,0), 2) # 绘制线段
    # cv2.circle(black_frame, pt_start, length, (0,255,0), 2) # 画一个圆，围住这些发散线段



    # # 在画布中绘制两条线段，一条长200，一条长300，像连杆一样旋转
    # pt_origin_x = 540 # 线段1的起始点X坐标
    # pt_origin_y = 0 # 线段1的起始点Y坐标
    # line1_length = 200 # 线段1的长度
    # line2_length = 300 # 线段2的长度
    # line1_angle_deg = 0 + angle_step_cnt * angle_step # 线段1的角度（度）
    # line2_angle_deg = 180 - angle_step_cnt * angle_step # 线段2的角度（度）

    # MyDrawTwoLine(black_frame, (pt_origin_x, pt_origin_y), line1_length, line1_angle_deg, line2_length, line2_angle_deg)

    # angle_step_cnt += angle_step_cnt_forward # 增加角度步长计数器
    # if angle_step_cnt*angle_step >= 180 or angle_step_cnt*angle_step <= 0: # 如果角度步长计数器已经在范围边缘了
    #   angle_step_cnt_forward *= -1 # 赶紧改变角度步长方向，不然下一次就会超出范围了



    cv2.rectangle(black_frame,
      CoordOnCartesianToCv( (240,940), (0,frame_height-1) ),
      CoordOnCartesianToCv( (840,140), (0,frame_height-1) ),
      (255,255,0), 2
    ) # 绘制矩形
    
    if target_x == 240 and target_y < 940:
      target_y += coord_step # 增加Y步长
    elif target_y == 940 and target_x < 840:
      target_x += coord_step # 增加X步长
    elif target_x == 840 and target_y > 140:
      target_y -= coord_step # 减少Y步长
    elif target_y == 140 and target_x > 240:
      target_x -= coord_step # 减少X步长
    elif target_y == 140 and target_x == 240:
      target_x = 240 # 回到起始点
      target_y = 140 # 回到起始点
    
    pt_origin_x = 540 # 双连杆的起始点X坐标
    pt_origin_y = 540 # 双连杆的起始点Y坐标
    line1_length = 200 # 线段1的长度
    line2_length = 300 # 线段2的长度
    
    try:
      line1_angle_deg, line2_angle_deg = decompose_vector(
        line1_length,
        line2_length,
        target_x - pt_origin_x,
        target_y - pt_origin_y
      ) # 求解线段1和线段2的角度
    except ValueError as e:
      print("decompose_vector error:", e)
      continue

    MyDrawTwoLine(black_frame,
      (pt_origin_x, pt_origin_y),
      line1_length,
      line1_angle_deg,
      line2_length,
      line2_angle_deg
    ) # 绘制双连杆的两条线段






    cv2.imshow('black_frame', black_frame) # 在窗口中显示裁剪后的图像

    PressKey = cv2.waitKey(1) & 0xFF
    if PressKey & 0xFF == 27: # 如果按下ESC键
      break # 退出循环
    
  cv2.destroyAllWindows() # 关闭所有窗口
  print("所有窗口已关闭")

if __name__ == "__main__":
  main()
