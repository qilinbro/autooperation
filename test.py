import pyautogui as pa
import time

# while True:
#     x, y = pa.position()
#     print(f"当前鼠标位置: ({x}, {y})")
#     time.sleep(0.5)

pa.moveTo(1819, 504, duration=1)
pa.click()
while True:
    pa.scroll(-200)