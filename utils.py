import pyautogui
import time
import os
import logging
from typing import Optional

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AutoMouseOperation:
    """自动鼠标操作类，用于处理微信朋友圈自动点赞"""
    
    DEFAULT_CONFIDENCES = [0.9, 0.8, 0.7]
    DEFAULT_TIMEOUT = 12
    DEFAULT_INTERVAL = 2
    MAX_ATTEMPTS = 3
    
    def __init__(self, image_folder: str = 'position'):
        """
        初始化自动鼠标操作类
        
        Args:
            image_folder: 图片资源所在文件夹路径
        """
        self.image_folder = image_folder
        
    def get_image_path(self, image_name: str) -> str:
        """获取图片的完整路径"""
        return os.path.join(self.image_folder, image_name)
        
    def wait_for_image(self, image_name: str, timeout: int = DEFAULT_TIMEOUT, interval: int = DEFAULT_INTERVAL) -> bool:
        """等待直到图片出现在屏幕上"""
        image_path = self.get_image_path(image_name)
        end_time = time.time() + timeout
        
        while time.time() < end_time:
            for confidence in self.DEFAULT_CONFIDENCES:  # 逐步降低匹配精度
                try:
                    logging.info(f"尝试以 {confidence} 的置信度等待图片: {image_name}")
                    if pyautogui.locateOnScreen(image_path, confidence=confidence):
                        logging.info(f"在置信度 {confidence} 下找到图片: {image_name}")
                        return True
                except pyautogui.ImageNotFoundException:
                    continue
                except Exception as e:
                    logging.error(f"等待图片时发生错误: {str(e)}, 错误类型: {type(e).__name__}")
                    break
            
            logging.info(f"未找到图片 {image_name}，等待 {interval} 秒后重试")
            time.sleep(interval)
            
        logging.warning(f"等待图片 {image_name} 超时（{timeout}秒）")
        return False

    def locate_and_click(self, image_name: str, clicks: int = 1, confidence: float = 0.9) -> bool:
        """
        定位图片并点击
        
        Args:
            image_name: 图片文件名
            clicks: 点击次数
            confidence: 图像匹配置信度
            
        Returns:
            bool: 操作是否成功
        """
        try:
            image_path = self.get_image_path(image_name)
            logging.info(f"正在查找图片: {image_name}")
            
            # 添加重试机制
            max_attempts = self.MAX_ATTEMPTS
            for attempt in range(max_attempts):
                try:
                    # 增加识别容错性
                    location = None
                    for conf in [confidence, confidence - 0.1, confidence - 0.2]:  # 逐步降低匹配精度
                        try:
                            logging.info(f"尝试以 {conf} 的置信度查找图片")
                            location = pyautogui.locateOnScreen(image_path, confidence=conf)
                            if location:
                                logging.info(f"在置信度 {conf} 下找到图片")
                                break
                        except pyautogui.ImageNotFoundException:
                            continue
                        except Exception as e:
                            logging.error(f"图像识别出现异常: {str(e)}")
                            break
                            
                    if location:
                        # 记录当前位置
                        current_pos = pyautogui.position()
                        logging.info(f"找到图片位置: {location}, 当前鼠标位置: ({current_pos.x}, {current_pos.y})")
                        
                        # 移动到目标位置并等待
                        center = pyautogui.center(location)
                        pyautogui.moveTo(center, duration=0.5)
                        time.sleep(0.5)
                        
                        # 执行点击
                        for i in range(clicks):
                            pyautogui.click()
                            logging.info(f"完成第 {i+1} 次点击")
                            time.sleep(0.8)  # 增加点击间隔
                            
                        logging.info(f"成功点击图片: {image_name}")
                        return True
                    else:
                        logging.warning(f"第 {attempt + 1} 次尝试未找到图片: {image_name}")
                        if attempt < max_attempts - 1:
                            time.sleep(1)  # 等待后重试
                            
                except pyautogui.ImageNotFoundException:
                    logging.warning(f"第 {attempt + 1} 次尝试未找到图片: {image_name}")
                    if attempt < max_attempts - 1:
                        time.sleep(1)
                except Exception as e:
                    logging.error(f"第 {attempt + 1} 次尝试时发生错误: {str(e)}, 错误类型: {type(e).__name__}")
                    if attempt < max_attempts - 1:
                        time.sleep(1)
                        
            logging.error(f"在 {max_attempts} 次尝试后仍未能成功点击图片: {image_name}")
            return False
                
        except Exception as e:
            logging.error(f"处理图片 {image_name} 时发生未知错误: {str(e)}, 错误类型: {type(e).__name__}")
            return False
            
    def auto_like_moments(self):
        """自动打开微信并给朋友圈点赞"""
        try:
            logging.info("=== 开始执行朋友圈点赞操作 ===")
            # 尝试打开微信并等待朋友圈按钮出现
            max_attempts = 5
            success = False
            
            for attempt in range(max_attempts):
                logging.info(f"第 {attempt + 1} 次尝试打开微信")
                try:
                    image_path = self.get_image_path('wechat.png')
                    location = pyautogui.locateOnScreen(image_path, confidence=0.8)
                    if location:
                        pyautogui.doubleClick(location)
                        logging.info("执行了双击操作")
                        if self.wait_for_image('moment.png'):
                            logging.info("微信已成功打开（已看到朋友圈按钮）")
                            success = True
                            break
                except Exception as e:
                    logging.error(f"双击操作失败: {str(e)}")
                time.sleep(2)
            
            if not success:
                logging.error(f"尝试 {max_attempts} 次后仍未能成功打开微信")
                return

            # 点击朋友圈并等待更多按钮出现
            max_attempts = 3
            success = False
            
            for attempt in range(max_attempts):
                logging.info(f"第 {attempt + 1} 次尝试进入朋友圈")
                if self.locate_and_click('moment.png', confidence=0.8):
                    if self.wait_for_image('more.png'):
                        logging.info("朋友圈已成功打开（已看到更多按钮）")
                        success = True
                        break
                time.sleep(2)
            
            if not success:
                logging.error(f"尝试 {max_attempts} 次后仍未能成功进入朋友圈")
                return

            while True:
                # 检查是否存在更多按钮
                image_path_more = self.get_image_path('more.png')
                more_found = False
                
                # 增加识别容错性
                for conf in self.DEFAULT_CONFIDENCES:
                    try:
                        logging.info(f"尝试以 {conf} 的置信度查找更多按钮")
                        if pyautogui.locateOnScreen(image_path_more, confidence=conf):
                            more_found = True
                            logging.info(f"在置信度 {conf} 下找到更多按钮")
                            break
                    except pyautogui.ImageNotFoundException:
                        continue
                    except Exception as e:
                        logging.error(f"查找更多按钮时出现异常: {str(e)}")
                        break
                
                if more_found:
                    # 点击更多按钮
                    self.locate_and_click('more.png')
                    time.sleep(2)  # 增加等待时间
                    
                    # 检查是否存在good图像
                    image_path_good = self.get_image_path('good.png')
                    good_found = False
                    
                    # 增加识别容错性
                    for conf in self.DEFAULT_CONFIDENCES:
                        try:
                            logging.info(f"尝试以 {conf} 的置信度查找点赞按钮")
                            if pyautogui.locateOnScreen(image_path_good, confidence=conf):
                                good_found = True
                                logging.info(f"在置信度 {conf} 下找到点赞按钮")
                                break
                        except pyautogui.ImageNotFoundException:
                            continue
                        except Exception as e:
                            logging.error(f"查找点赞按钮时出现异常: {str(e)}")
                            break
                            
                    if good_found:
                        try:
                            logging.info("发现点赞按钮，准备点击")
                            success = self.locate_and_click('good.png', clicks=2)  # 双击点赞
                            if success:
                                logging.info("点赞操作成功完成")
                                time.sleep(1.5)  # 增加点赞后等待时间
                            else:
                                logging.error("点赞操作失败")
                                continue
                        except Exception as e:
                            logging.error(f"执行点赞操作时出现异常: {str(e)}")
                            continue
                    else:
                        # 检查是否存在already_good图像
                        try:
                            image_path_already_good = self.get_image_path('already_good.png')
                            logging.info("正在检查是否已点赞")
                            location = None
                            
                            # 重试机制检查already_good状态
                            for attempt in range(3):
                                try:
                                    location = pyautogui.locateOnScreen(image_path_already_good, confidence=0.9)
                                    if location:
                                        break
                                    time.sleep(0.5)
                                except Exception as e:
                                    logging.warning(f"第 {attempt + 1} 次检查已点赞状态失败: {str(e)}")
                                    
                            if location:
                                logging.info("检测到已点赞状态，准备滚动")
                                try:
                                    # 获取图片中心位置
                                    center = pyautogui.center(location)
                                    logging.info(f"已点赞图标中心位置: ({center.x}, {center.y})")
                                    
                                    # 平滑移动鼠标到图片位置
                                    pyautogui.moveTo(center.x, center.y, duration=0.5)
                                    time.sleep(1)  # 等待鼠标移动完成
                                    
                                    # 验证鼠标位置
                                    current_pos = pyautogui.position()
                                    logging.info(f"当前鼠标位置: ({current_pos.x}, {current_pos.y})")
                                    
                                    
                                    # 确保鼠标已移动到正确位置
                                    logging.info("准备进行点击聚焦")
                                    focus_success = False
                                    for focus_attempt in range(3):  # 最多尝试3次聚焦
                                        try:
                                            pyautogui.click()
                                            logging.info(f"第 {focus_attempt + 1} 次点击聚焦成功")
                                            time.sleep(0.7)  # 减少聚焦等待时间
                                            focus_success = True
                                            break
                                        except Exception as e:
                                            logging.error(f"第 {focus_attempt + 1} 次点击聚焦失败: {str(e)}")
                                            if focus_attempt < 2:  # 如果不是最后一次尝试
                                                time.sleep(1)
                                                continue
                                    
                                    if not focus_success:
                                        logging.error("多次尝试聚焦都失败，尝试直接滚动")
                                    
                                    logging.info("开始执行滚动操作")
                                    scroll_success = 0
                                    max_scroll_attempts = 3  # 改为3次滑动
                                    
                                    for i in range(max_scroll_attempts):
                                        try:
                                            current_pos = pyautogui.position()
                                            logging.info(f"滚动前鼠标位置: ({current_pos.x}, {current_pos.y})")
                                            
                                            pyautogui.scroll(-200)  # 适当增加滚动幅度
                                            scroll_success += 1
                                            logging.info(f"完成第 {i+1} 次滚动")
                                            time.sleep(0.7)  # 减少滚动间隔时间
                                        except Exception as e:
                                            logging.error(f"第 {i+1} 次滚动失败: {str(e)}, 错误类型: {type(e).__name__}")
                                            time.sleep(1)  # 失败后等待一下再继续尝试
                                            
                                    time.sleep(2)  # 滚动完成后等待
                                    logging.info("滚动操作完成")
                                    # 继续循环检查更多按钮
                                    continue
                                    
                                except Exception as e:
                                    logging.error(f"滚动操作过程中发生错误: {str(e)}")
                                    # 即使滚动失败也继续循环
                                    continue
                            else:
                                logging.info("未检测到已点赞状态")
                                # 继续检查下一个点赞按钮
                                continue
                                
                        except Exception as e:
                            logging.error(f"检查点赞状态时发生错误: {str(e)}, 错误类型: {type(e).__name__}")
                            # 出错时等待后继续
                            time.sleep(1)
                            continue
                    
                    logging.info("=== 本次操作完成，等待页面更新 ===")
                    time.sleep(2)  # 增加页面更新等待时间
                else:
                    logging.info("未找到更多按钮，结束操作")
                    break
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            logging.error("=== 执行点赞操作时发生错误 ===")
            logging.error(f"错误类型: {type(e).__name__}")
            logging.error(f"错误信息: {str(e)}")
            logging.error("详细堆栈信息:")
            logging.error(error_trace)