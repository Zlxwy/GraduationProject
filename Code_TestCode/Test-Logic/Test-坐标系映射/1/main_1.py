from PlaneMapper import PlaneMapper

# ========== 只需要初始化一次 ==========
rect_a = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
rect_b = [(20.1, 30.5), (50.2, 25.3), (55.7, 60.1), (22.4, 65.8)]

mapper = PlaneMapper(rect_a, rect_b)

# 查看精度（越小越好）
print("重投影误差均值:", mapper.check_precision())

# 单点 A→B
pt_b = mapper.a_to_b((3.2, 7.9))
print("A→B:", pt_b)

# 单点 B→A
pt_a = mapper.b_to_a(pt_b)
print("B→A:", pt_a)

# 批量点
pts_a = [(1,1), (2,3), (5,5), (7,8)]
pts_b = mapper.batch_a_to_b(pts_a)
print("批量A→B:", pts_b)