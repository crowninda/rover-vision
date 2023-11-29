# detect and process obstacles, draw a mapping map and return the processed obstacle coordinates

import sys
sys.path.append('/home/pi/picar-4wd')
import numpy as np
import navigation
import logger
import itertools
from typing import Generator

log = logger.setup_logger("../Log.log")

class Map:
    def __init__(self, scan_list:list):
        self.scan_list = scan_list
        self.VALID_SCAN_LIST = [] # store the coordinates of obstacles that meet the conditions 
        self.OBSTACLE = set() # obstacle coordinates, used by A* algorithm 
        self.DISTANCE_THRESHOLD = 20 # define distance threshold constants 
        

    def draw_map(self, obstacle: list) -> bool:
        ''' 
        create a map based on obstacle coordinates 
        
        Args:
            list: coordinate list of obstacles 
        
        Returns:
                bool: whether the obstacle coordinates are successfully written to the map
        '''

        # create a 200 x 100 NumPy array (map) and initialize it to 0 
        array = np.zeros((navigation.MAX_X, navigation.MAX_Y), dtype = int) 
        for i in range(len(obstacle)):
            array[obstacle[i][0], obstacle[i][1]] = 1
        try:
            with open('array.txt', 'w') as file:
                
                # save array to text 
                np.savetxt(file, array, fmt='%d', delimiter=',')
            return True

        except Exception as e:
            # print("IO Error while draw map: ", str(e))
            log.error("IO Error while draw map: ", str(e))


    def check_add(self, x: int, y: int) -> None:
        ''' 
        judge the processed coordinates and add those who meet the conditions to the list 
        
        Args:
            x: adjusted x coordinate 
            y: adjusted y coordinate 
            list_name: a list that stores obstacle coordinates
        '''
        if 0 <= x < navigation.MAX_X and 0 <= y < navigation.MAX_Y:
            self.VALID_SCAN_LIST.append([x, y])


    def coordinate_conversion(self) -> None:
        ''' 
        process the coordinates and convert them into map coordinates 
        '''
        for i, (x, y) in enumerate(self.scan_list):

            # if the x-axis of the return coordinate has -2.0 or 2.0, it means there is no obstacle or the obstacle is far away from the car 
            if (x != -2.0) and (x!= 2.0):

                # convert the X-axis values ​​of the coordinates of the first 5 sets (obstacles on the left) of the 10 sets of results obtained from ultrasonic scanning into negative values 
                if i < len(self.scan_list) // 2 and x != 0.0:
                    x = -x 

                # x coordinate conversion, translate to the right 100
                x_idx = int(x + navigation.OFFSET_X)
                y_idx = int(y)
                self.check_add(x_idx, y_idx)

    
    def generate_obstacle_neighbor(self) -> Generator[tuple, None, None]:
        '''
        the second processing of obstacle coordinates - determine whether adjacent obstacle coordinates are the same obstacle 
        
        Returns:
                generator, generate coordinate pairs (x, y) one by one, representing the position of the obstacle
        '''
        for i in range(len(self.VALID_SCAN_LIST) - 1): 
            x1, y1 = self.VALID_SCAN_LIST[i]
            x2, y2 = self.VALID_SCAN_LIST[i + 1]
            if abs(y2 - y1) <= self.DISTANCE_THRESHOLD and abs(x2 - x1) <= self.DISTANCE_THRESHOLD: 
                min_x, max_x = int(min(x1, x2)), int(max(x1, x2))
                min_y, max_y = int(min(y1, y2)), int(max(y1, y2))
                for coord in itertools.product(range(min_x, max_x), range(min_y, max_y)):
                    yield coord
    
    
    def generate_obstacle_close(self) -> Generator[tuple, None, None]:
        '''
        the third processing of obstacle coordinates - 
        in order to prevent the car from not considering its own size and getting too close to the obstacle and causing a collision
        
        Returns:
                generator, generate coordinate pairs (x, y) one by one, representing the position of the obstacle
        '''
        for i in range(len(self.VALID_SCAN_LIST)):
            x1, y1 = self.VALID_SCAN_LIST[i]
            start = (x1 - 10, y1 - 10) 
            
            # the coordinates within the starting point coordinates (x, y) each increased by 10 are considered obstacles.  
            min_x, max_x = int(start[0] + 0), int(start[0] + 20)
            min_y, max_y = int(start[1] + 0), int(start[1] + 20)
            if 0 <= max_x < navigation.MAX_X and 0 <= max_y < navigation.MAX_Y:
                for coord in itertools.product(range(min_x, max_x), range(min_y, max_y)):
                    yield coord


    def advance_mapping(self) -> list:
        ''' 
        process the obstacle coordinates and return the effective coordinates 

        Returns:
                obstacle: the coordinates of the obstacle 
        '''

        # the first processing of obstacle coordinates 
        self.coordinate_conversion()
        self.OBSTACLE = set(tuple(sublist) for sublist in self.VALID_SCAN_LIST) 
        try:
            for coord in self.generate_obstacle_neighbor():
                self.OBSTACLE.add(coord)
            for coord in self.generate_obstacle_close():
                self.OBSTACLE.add(coord)
        except Exception as e:
            # print("An unexpected error occurred while advance_mapping: {}".format(e))
            log.error(f"An unexpected error occurred: {str(e)}", exc_info=True)
        
        self.draw_map(list(self.OBSTACLE))
        return list(self.OBSTACLE)

if __name__ == "__main__":
    obstacle_item = [(35, 29), (35, 30), (40, 25)]
    item = Map(obstacle_item)
    obstacle = item.advance_mapping()
    # print(obstacle)


