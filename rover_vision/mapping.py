
# 進行障礙物偵測及加工，繪製出映射地圖返回加工後障礙物座標

import sys
sys.path.append('/home/pi/picar-4wd')
import numpy as np
import navigation
import logger
import itertools
import fcntl

log = logger.setup_logger("Log.log")

class Map:
    def __init__(self, scan_list:list):
        self.scan_list = scan_list
        self.VALID_SCAN_LIST = [] # 存放符合條件的障礙物座標
        self.OBSTACLE = [] # 障礙物座標，用於A*算法使用
        self.DISTANCE_THRESHOLD = 20 # 定义距离阈值常量
        

    def draw_map(self, obstacle: list) -> bool:
        ''' 
        根據障礙物座標，創建地圖
        
        Args:
            list: 障礙物的座標list
        '''

        # 創建一個 200 乘 100 的 NumPy 陣列(地圖)並初始化為 0
        array = np.zeros((navigation.MAX_X, navigation.MAX_Y), dtype = int) 
        for i in range(len(obstacle)):
            array[obstacle[i][0], obstacle[i][1]] = 1
        try:
            with open('array.txt', 'w') as file:
                # 保存数组到文本
                np.savetxt(file, array, fmt='%d', delimiter=',')
            return True

        except Exception as e:
            print("IO Error while draw map: ", str(e))
            log.error("IO Error while draw map: ", str(e))


    def check_add(self, x: int, y: int) -> None:
        ''' 
        將調整加工後的x,y值判斷範圍後，加入需求的list當中
        
        Args:
            x: 調整後的x座標
            y: 調整後的y座標
            list_name: 各種存放障礙物座標的判斷條件
        '''
        if 0 <= x < navigation.MAX_X and 0 <= y < navigation.MAX_Y:
            self.VALID_SCAN_LIST.append([x, y])


    def coordinate_conversion(self) -> None:
        ''' 
        將座標進行加工轉化為可用的資料. 以自走車為中心。 左方x軸為負值右方為正值並進行座標平移
        
        Args:
            scan_list: 超聲波掃描後得到的10組障礙物座標
        '''
        try:
            for i, (x, y) in enumerate(self.scan_list):

                # 返回座標x軸有-2.0或2.0則代表無障礙物或障礙物距離自走車距離遠
                if (x != -2.0) and (x!= 2.0):

                    # 將超聲波掃描所得10組結果，前4組(左方障礙物)座標的X軸數值轉換為負值
                    if i < len(self.scan_list) // 2 and x != 0.0:
                        x = -x 

                    # 掃描後將地圖中障礙物的位置，其x座標向右平移 100
                    x_idx = int(x + navigation.OFFSET_X)
                    y_idx = int(y)

                    # 將映射後座標，其位置不超過映射地圖範圍者納入有效的資料列表中
                    self.check_add(x_idx, y_idx)

        except Exception as e:
            print("error_coordinate_conversion: {}".format(e))
            log.error(f"error_coordinate_conversion: {str(e)}")


    def advance_mapping(self) -> list:
        ''' 
        將障礙物座標進行加工後回傳有效座標

        Args:
            scan_list: 超聲波感測器掃描後所得10組障礙物座標
        
        Returns:
                obstacle: 障礙物座標    
        '''

        # 障礙物座標第一種加工
        self.coordinate_conversion()

        # 將轉換完的障礙物座標複製一份，待A* 算法使用，tuple轉成list
        self.OBSTACLE = [tuple(sublist) for sublist in self.VALID_SCAN_LIST] 

        try:

            # 障礙物座標第二種加工-將障礙物座標相鄰者，判斷是否為同一障礙物  
            for i in range(len(self.VALID_SCAN_LIST) - 1): 
                x1, y1 = self.VALID_SCAN_LIST[i]
                x2, y2 = self.VALID_SCAN_LIST[i + 1]

                # 判斷x 及 y 座標差異是否小於設定閾值，符合者 兩座標間相關聯座標儲存為障礙物座標
                if abs(y2 - y1) <= self.DISTANCE_THRESHOLD and abs(x2 - x1) <= self.DISTANCE_THRESHOLD: 
                    min_x, max_x = int(min(x1, x2)), int(max(x1, x2))
                    min_y, max_y = int(min(y1, y2)), int(max(y1, y2))
                    
                    self.OBSTACLE.extend(itertools.product(range(min_x, max_x), range(min_y, max_y)))

            for i in range(len(self.VALID_SCAN_LIST)):
                x1, y1 = self.VALID_SCAN_LIST[i]
                
                # 障礙物座標的第三種加工-為避免自走車未考慮自身大小，太靠近障礙物導致碰撞，將障礙物座標周圍15個座標範圍都改成有障礙物的狀況
                start = (x1 - 15, y1 - 15) 
                
                # 起點(start)座標(x, y) 各增加10的範圍內的座標  
                min_x, max_x = int(start[0] + 0), int(start[0] + 30)
                min_y, max_y = int(start[1] + 0), int(start[1] + 30)
                if 0 <= max_x < navigation.MAX_X and 0 <= max_y < navigation.MAX_Y:
                    self.OBSTACLE.extend(itertools.product(range(min_x, max_x), range(min_y, max_y)))

        except Exception as e:
            print("An unexpected error occurred while advance_mapping: {}".format(e))
            log.error(f"An unexpected error occurred: {str(e)}", exc_info=True)

        self.draw_map(self.OBSTACLE)
        return self.OBSTACLE

if __name__ == "__main__":
    obstacle_item = [(100,1), (100,2)]
    item = Map(obstacle_item)
    suu = item.draw_map(obstacle_item)
    print(suu)

