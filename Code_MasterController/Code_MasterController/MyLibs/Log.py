import time
import threading
import queue
import os

class Log:
  def __init__(self):
    # 1. 创建线程安全队列，存放待输出日志
    self.log_queue = queue.Queue()
    
    # 2. 生成当天日期的日志文件名
    if not os.path.exists("./Logs"): os.makedirs("./Logs")
    self.log_filename = f"./Logs/ProgramLog_{time.strftime('%Y_%m_%d_%H_%M_%S', time.localtime())}.txt"
    
    # 3. 控制线程运行的标志
    self.running = True
    
    # 4. 创建并启动后台日志处理线程
    self.log_thread = threading.Thread(target=self._process_log_loop, daemon=True)
    self.log_thread.start()

  """
  外部调用的日志打印接口
  只负责把消息入队，不做耗时操作，不阻塞主线程
  """
  def PrintString(self, msg: str):
    self.log_queue.put(msg)

  def PrintHexBytes(self, msg: bytes, prefix="", suffix=""):
    hex_str = ""
    for byte in msg:
      hex_str += hex(byte)[2:].zfill(2) + " "
    self.log_queue.put(prefix + hex_str + suffix)

  def _process_log_loop(self):
    """
    【后台线程】
    无限循环：从队列取消息 → 加时间戳 → 打印 → 写入文件
    """
    while self.running:
      try:
        msg = self.log_queue.get(timeout=0.5) # 阻塞等待队列中的日志（没有日志时线程休眠，不占CPU）
        log_info = f"[{time.strftime('%Y.%m.%d %H:%M:%S', time.localtime())}] {msg}" # 拼接带时间戳的日志字符串
        print(log_info) # 控制台打印
        with open(self.log_filename, 'a', encoding='utf-8') as f: # 写入日志文件（追加模式）
          f.write(log_info + '\n') # 写入日志字符串
        self.log_queue.task_done() # 标记任务完成
      except queue.Empty: # 队列为空，继续循环
        continue # 超时无消息，继续循环

  """
  停止日志线程（程序退出时调用）
  """
  def stop(self):
    if not self.running: return # 防止重复stop
    self.running = False
    if self.log_thread is not None and self.log_thread.is_alive():
      self.log_thread.join()

  def __del__(self):
    """
    类销毁时自动停止线程
    """
    self.stop()