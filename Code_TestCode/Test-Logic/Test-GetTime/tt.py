import time

start = time.monotonic()

# 模拟耗时操作
time.sleep(1.5)

end = time.monotonic()

TimeCost_ms = int((end-start) * 1000)

print(f"耗时: {TimeCost_ms} 毫秒")