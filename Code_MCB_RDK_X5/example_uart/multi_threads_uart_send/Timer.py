import threading
import time
from typing import Callable


"""
一个简单的定时器类，功能类似于提供的C++代码。
它启动一个后台线程，以指定的间隔重复执行一个任务。
"""
class Timer:

  def __init__(self, interval_ms: int, task: Callable[[], None]):
    """
    初始化定时器。
    Args:
      interval_ms (int): 任务执行的间隔时间，单位为毫秒 (ms)。
      task (Callable[[], None]): 需要重复执行的任务函数。
    """
    self.interval_s = interval_ms / 1000.0  # 转换为秒，因为 time.sleep 使用秒
    self.task = task
    self.running = False
    self.worker_thread = None



  """
  启动定时器。
  """
  def start(self):
    if self.running: return
    self.running = True
    self.worker_thread = threading.Thread(target=self._run, daemon=True) # 创建这个线程，是将会在后台循环运行的
    self.worker_thread.start()



  """
  停止定时器。
  """
  def stop(self):
    if not self.running: return
    self.running = False
    
    # # 等待工作线程结束（也可以不等待，因为它是daemon线程，会随着主线程结束而结束）
    # if self.worker_thread and self.worker_thread.is_alive():
    #   self.worker_thread.join()



  """
  工作线程的执行函数。
  """
  def _run(self):
    while self.running:
      if self.running: # 再次检查，防止在sleep期间被stop
        # 创建一个新线程来执行任务，然后立即分离(detach)
        # Python中没有detach，因此启动一个daemon线程让它自己结束
        task_thread = threading.Thread(target=self.task, daemon=True)
        task_thread.start()
      time.sleep(self.interval_s)

