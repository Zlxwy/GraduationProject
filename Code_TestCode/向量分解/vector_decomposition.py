"""
矢量分解函数
给定矢量C和两个矢量A、B的长度，求解A和B的角度，使得 C = A + B
"""

import math


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
def decompose_vector(len_a: float, len_b: float, c_x: float, c_y: float, solution: int=0):
  # 参数验证
  if len_a <= 0 or len_b <= 0:
    raise ValueError("矢量长度必须为正数")
  
  if solution not in (0, 1):
    raise ValueError("solution 参数必须是 0 或 1")

  # 计算矢量C的长度和角度
  len_c = math.sqrt(c_x**2 + c_y**2)
  
  # 特殊情况：C为零矢量
  if len_c == 0:
    # A和B必须等长反向
    if abs(len_a - len_b) < 1e-10:
      # 无穷多解，返回两个相反方向
      if solution == 0:
        return (0.0, 180.0)
      else:
        return (180.0, 0.0)
    else:
      raise ValueError("C为零矢量时，A和B必须等长")

  # 矢量C的角度
  theta_c = math.atan2(c_y, c_x)

  # 使用余弦定理求解角度差
  # cos(θ_C - θ_A) = (|C|² + |A|² - |B|²) / (2|A||C|)
  cos_diff = (len_c**2 + len_a**2 - len_b**2) / (2 * len_a * len_c)

  # 检查是否有解（三角形不等式）
  if cos_diff < -1 - 1e-10 or cos_diff > 1 + 1e-10:
    raise ValueError(
      f"无解：给定的矢量长度不满足三角形不等式。\n"
      f"需要 |{len_a:.2f} - {len_b:.2f}| <= {len_c:.2f} <= {len_a:.2f} + {len_b:.2f}"
    )

  # 限制在有效范围内
  cos_diff = max(-1.0, min(1.0, cos_diff))

  # 角度差
  angle_diff = math.acos(cos_diff)

  # 两个解
  theta_a1 = theta_c - angle_diff  # θ_A = θ_C - arccos(...)
  theta_a2 = theta_c + angle_diff  # θ_A = θ_C + arccos(...)

  # 计算对应的B的角度
  # B = C - A，所以 θ_B = atan2(B_y, B_x)
  def calc_angle_b(theta_a):
    a_x = len_a * math.cos(theta_a)
    a_y = len_a * math.sin(theta_a)
    b_x = c_x - a_x
    b_y = c_y - a_y
    return math.atan2(b_y, b_x)

  theta_b1 = calc_angle_b(theta_a1)
  theta_b2 = calc_angle_b(theta_a2)

  # 转换为度数 [0, 360)
  def to_degrees(angle_rad):
    angle_deg = math.degrees(angle_rad)
    return angle_deg % 360

  angle_a1 = to_degrees(theta_a1)
  angle_b1 = to_degrees(theta_b1)
  angle_a2 = to_degrees(theta_a2)
  angle_b2 = to_degrees(theta_b2)

  """
  以 a1 为 0 参考角度，将 a2 转换为极坐标轴上的角度
  与原 C 语言 fmodf 逻辑完全等价
  """
  def cal_angle_diff(zero_degree: float, curr_degree: float, area: float) -> float:
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


# ==================== 使用示例 ====================

if __name__ == "__main__":
  print("=" * 60)
  print("矢量分解函数使用示例")
  print("=" * 60)
  
  # 示例1：简单的水平情况
  print("\n【示例1】简单情况")
  print("矢量A长度 = 3, 矢量B长度 = 4, 矢量C坐标 = (3, 4)")
  print("预期：A沿x轴正方向(0°), B沿y轴正方向(90°)")
  try:
    angle_a, angle_b = decompose_vector(3, 4, 3, 4, solution=0)
    print(f"解0：A的角度 = {angle_a:.2f}°, B的角度 = {angle_b:.2f}°")
    angle_a, angle_b = decompose_vector(3, 4, 3, 4, solution=1)
    print(f"解1：A的角度 = {angle_a:.2f}°, B的角度 = {angle_b:.2f}°")
  except ValueError as e:
    print(f"错误: {e}")

  # 示例2：等腰三角形
  print("\n【示例2】等腰三角形")
  print("矢量A长度 = 5, 矢量B长度 = 5, 矢量C坐标 = (8, 0)")
  print("预期：A和B关于x轴对称")
  try:
    angle_a, angle_b = decompose_vector(5, 5, 8, 0, solution=0)
    print(f"解0：A的角度 = {angle_a:.2f}°, B的角度 = {angle_b:.2f}°")
    angle_a, angle_b = decompose_vector(5, 5, 8, 0, solution=1)
    print(f"解1：A的角度 = {angle_a:.2f}°, B的角度 = {angle_b:.2f}°")
  except ValueError as e:
    print(f"错误: {e}")

  # 示例3：一般情况
  print("\n【示例3】一般情况")
  print("矢量A长度 = 5, 矢量B长度 = 7, 矢量C坐标 = (6, 8)")
  try:
    angle_a, angle_b = decompose_vector(5, 7, 6, 8, solution=0)
    print(f"解0：A的角度 = {angle_a:.2f}°, B的角度 = {angle_b:.2f}°")
    
    # 验证结果
    import math
    a_x = 5 * math.cos(math.radians(angle_a))
    a_y = 5 * math.sin(math.radians(angle_a))
    b_x = 7 * math.cos(math.radians(angle_b))
    b_y = 7 * math.sin(math.radians(angle_b))
    c_calc_x = a_x + b_x
    c_calc_y = a_y + b_y
    print(f"验证：A({a_x:.4f}, {a_y:.4f}) + B({b_x:.4f}, {b_y:.4f}) = ({c_calc_x:.4f}, {c_calc_y:.4f})")
    print(f"       应该等于 C(6, 8)")
  except ValueError as e:
    print(f"错误: {e}")

  # 示例4：无解情况
  print("\n【示例4】无解情况（不满足三角形不等式）")
  print("矢量A长度 = 2, 矢量B长度 = 3, 矢量C坐标 = (10, 0)")
  print("原因：2 + 3 < 10，不满足三角形不等式")
  try:
    angle_a, angle_b = decompose_vector(2, 3, 10, 0, solution=0)
    print(f"结果：A的角度 = {angle_a:.2f}°, B的角度 = {angle_b:.2f}°")
  except ValueError as e:
    print(f"错误: {e}")

  # 示例5：连杆机构应用
  print("\n【示例5】连杆机构应用示例")
  print("假设有一个平面连杆机构，需要确定两个连杆的角度位置")
  print("连杆A长度 = 100mm, 连杆B长度 = 80mm, 目标点C坐标 = (120, 50)")
  try:
    angle_a, angle_b = decompose_vector(100, 80, 120, 50, solution=0)
    print(f"解0：连杆A角度 = {angle_a:.2f}°, 连杆B角度 = {angle_b:.2f}°")
    angle_a, angle_b = decompose_vector(100, 80, 120, 50, solution=1)
    print(f"解1：连杆A角度 = {angle_a:.2f}°, 连杆B角度 = {angle_b:.2f}°")
  except ValueError as e:
    print(f"错误: {e}")

  print("\n" + "=" * 60)