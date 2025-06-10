import pyautogui
import time
import os
import logging
from typing import Optional

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AutoMouseOperation:
    """自动鼠标操作类，用于处理微信朋友圈自动点赞"""
    
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
            
            try:
                location = pyautogui.locateOnScreen(image_path, confidence=confidence)
            except pyautogui.ImageNotFoundException:
                logging.warning(f"未找到图片: {image_name}")
                return False
            except Exception as e:
                logging.error(f"查找图片 {image_name} 时发生错误: {str(e)}")
                return False
            
            if location:
                try:
                    for _ in range(clicks):
                        pyautogui.click(location)
                        time.sleep(0.5)  # 点击之间添加短暂延时
                    logging.info(f"成功点击图片: {image_name}")
                    return True
                except Exception as e:
                    logging.error(f"点击图片 {image_name} 时发生错误: {str(e)}")
                    return False
            else:
                logging.warning(f"未找到图片: {image_name}")
                return False
                
        except Exception as e:
            logging.error(f"处理图片 {image_name} 时发生未知错误: {str(e)}")
            return False
            
    def auto_like_moments(self):
        """自动打开微信并给朋友圈点赞"""
        try:
            # 打开微信
            if not self.locate_and_click('wechat.png', clicks=2):
                return
            time.sleep(2)  # 增加等待时间
            
            # 打开朋友圈
            if not self.locate_and_click('moment.png'):
                return
            time.sleep(2)  # 增加等待时间
            
            while True:
                # 检查是否存在更多按钮
                image_path_more = self.get_image_path('more.png')
                if pyautogui.locateOnScreen(image_path_more, confidence=0.9):
                    # 点击更多按钮
                    self.locate_and_click('more.png')
                    time.sleep(2)  # 增加等待时间
                    
                    # 检查是否存在good图像
                    image_path_good = self.get_image_path('good.png')
                    if pyautogui.locateOnScreen(image_path_good, confidence=0.9):
                        self.locate_and_click('good.png')
                        logging.info("点击了点赞按钮")
                        time.sleep(1.5)  # 增加点赞后等待时间
                    else:
                        # 检查是否存在already_good图像
                        try:
                            image_path_already_good = self.get_image_path('already_good.png')
                            logging.info("正在检查是否已点赞")
                            location = pyautogui.locateOnScreen(image_path_already_good, confidence=0.9)
                            
                            if location:
                                logging.info("检测到已点赞状态，准备滚动")
                                try:
                                    # 移动鼠标到图片位置
                                    pyautogui.moveTo(location)
                                    time.sleep(1.5)  # 等待鼠标移动完成
                                    
                                    # 确保鼠标已移动到正确位置
                                    logging.info("开始执行滚动操作")
                                    for i in range(5):
                                        try:
                                            pyautogui.scroll(-200)
                                            logging.info(f"完成第 {i+1} 次滚动")
                                            time.sleep(1)  # 增加滚动间隔
                                        except Exception as e:
                                            logging.error(f"第 {i+1} 次滚动失败: {str(e)}")
                                            
                                    time.sleep(2)  # 滚动完成后等待
                                    logging.info("滚动操作完成")
                                    
                                except Exception as e:
                                    logging.error(f"滚动操作过程中发生错误: {str(e)}")
                            else:
                                logging.info("未检测到已点赞状态")
                                
                        except Exception as e:
                            logging.error(f"检查点赞状态时发生错误: {str(e)}")
                    
                    time.sleep(2)  # 增加页面更新等待时间
                else:
                    logging.info("未找到更多按钮，结束操作")
                    break
            
        except Exception as e:
            logging.error(f"执行点赞操作时发生错误: {str(e)}")

if __name__ == '__main__':
    auto_mouse = AutoMouseOperation()
    auto_mouse.auto_like_moments()