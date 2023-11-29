
# using data obtained from ultrasonic sensors for vehicle obstacle avoidance function

import sys
sys.path.append('/home/pi/picar-4wd')
import picar_4wd as fc
import time

def obstacle_relative_position(scan_list: str) -> int:
    '''
    calculate the relative position of obstacles to the car

    Args:
        scan_list (str): Scan for obstacles
        
    Rrturns:
            pos (int): the obstacle is located relative to the car
            max_obstacle (int): maximum obstacle size
    '''
    obstacle_number = [] # record the relative position of the obstacle to the car 

    paths = scan_list.split("2") 
    for path in paths:

        # 0 here represents no obstacle, 1 represents 18 degrees (180 degrees divided by 10 sets of data) 
        obstacle_number.append(len(path))
    max_obstacle = max(obstacle_number)
    largest_obstacle = obstacle_number.index(max_obstacle)
    
    # find the location of the largest obstacle in scan_list 
    pos = scan_list.index(paths[largest_obstacle])

    # determine whether the obstacle is located on the left front, right front or right front of the car
    pos += int((len(paths[largest_obstacle]) - 1) / 3 )
    return pos, max_obstacle


def move_backward25():
    '''
    there is an obstacle in front of the car and the car moves backwards
    '''
    SPEED = 30 # car speed setting
    for _ in range(4):
        speed4 = fc.Speed(SPEED)
        speed4.start()
        fc.backward(100)
        x = 0
        for i in range(1):
            time.sleep(0.1)
            speed = speed4()
            x += speed * 0.1
        speed4.deinit()
        fc.stop()


def main():
    SPEED = 30 # car speed setting
    SCAN_DISTANCE = 30 # set the distance for whether ultrasonic scanning obstacles will respond
    while True:

        # ultrasonic detection results
        scan_list = fc.scan_step(SCAN_DISTANCE)  
        if not scan_list:
            continue

        # make sure to scan all angles 
        if len(scan_list) > 9:
            scan_list = [str(i) for i in scan_list]
            scan_list = "".join(scan_list)

            # if there are no obstacles almost directly in front of you, go straight
            if "22222222" in scan_list[1:9]:
               fc.forward(25) 
            else:
                pos, max_obstacle = obstacle_relative_position(scan_list)
                if max_obstacle > 1:
                    if pos < 4 :  
                        fc.turn_right(SPEED)
                    elif pos > 5 : 
                        fc.turn_left(SPEED)
                    else:

                        # When the obstacle is directly ahead, back up first and then choose the turning direction.
                        move_backward25() 
                        time.sleep(0.8)
                        if pos == 4:
                            fc.turn_right(SPEED)
                        elif pos == 5:
                            fc.turn_left(SPEED)


if __name__ == "__main__":
    try: 
        main()
    finally:
        fc.stop()

