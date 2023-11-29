# According to the algorithm, provide the optimal route coordinates, and then convert them into the number of 
# steps forward and the direction of turns for the autonomous vehicle
import sys
sys.path.append('/home/pi/picar-4wd')

# constant
TURN_LEFT = "turn_left"
TURN_RIGHT = "turn_right"
UP = "up"
DOWN = "down"
RIGHT = "right"
LEFT = "left"


def turning_direction_and_step(x_diff: int, y_diff: int, current_action: list, movements: list, step_count: int) -> list:
    ''' 
    determine the next action the car will take and the number of steps it will take
    
    Args: 
        x_diff: the difference between the current x-coordinate and the x-coordinate of the next step 
        y_diff: the difference between the current y-coordinate and the y-coordinate of the next step
        current_action: the current movement of the car 
        movements: record the actions that the car should do in sequence
    
    Returns:
        step_count: number of steps taken straight after the last turn
    '''
    if y_diff != 0:

        # The current action direction involves a change in the x-axis 
        if current_action[0] == "x":

            # When the axis direction changes in the next step of the car, it indicates that the vehicle
            #  is about to change direction, and the previously accumulated steps will be stored 
            movements.append(step_count)

            # return the number of steps to zero and recalculate
            step_count = 0
            if (y_diff > 0 and current_action[1] == RIGHT) or (y_diff < 0 and current_action[1] == LEFT):               
                movements.append(TURN_LEFT)
            elif (y_diff < 0 and current_action[1] == RIGHT) or (y_diff > 0 and current_action[1] == LEFT):
                movements.append(TURN_RIGHT)
        current_action[0] = "y"
        if y_diff > 0: 
            current_action[1] = UP
        elif y_diff < 0: 
            current_action[1] = DOWN
   
    elif x_diff != 0:
        if current_action[0] == "y":
            movements.append(step_count)
            step_count = 0
            if (x_diff < 0 and current_action[1] == UP) or (x_diff > 0 and current_action[1] == DOWN):
                movements.append(TURN_LEFT)   
            elif (x_diff < 0 and current_action[1] == DOWN) or (x_diff > 0 and current_action[1] == UP):
                movements.append(TURN_RIGHT)

        current_action[0] = "x"
        if x_diff > 0: 
            current_action[1] = RIGHT
        elif x_diff < 0: 
            current_action[1] = LEFT

    # when the car keeps moving in the same x or y axis direction, the number of steps continues to increase
    step_count += 1
    return step_count


def first_step(current_direct: list, start_point: int, path: list) -> list:
    ''' 
    confirm which axis and in which direction the car will move in its first step
    
    Args:
        current_direct: starting from the starting point, the first step is to take the direction of progress
        start_point: starting point coordinates of the optimal path map 
        path: best road map
    
    Returns:
        current_direct: get the axis and direction of the change
    '''
    
    # x coordinate change x 座標變化
    if start_point[0] != path[1][0]: 
        current_direct[0] = "x"
        if path[1][0] > start_point[0]: 
            current_direct[1] = RIGHT
        else: 
            current_direct[1] = LEFT
    
    # y coordinate change y 座標變化
    elif start_point[1] != path[1][1]:
        current_direct[0] = "y"
        if path[1][1] > start_point[1]:
            current_direct[1] = UP
        else: 
            current_direct[1] = DOWN
    return current_direct


def calculate_movement(path: list) -> list:
    '''
    according to the coordinate list, convert it into the action to be performed by the car 

    Args:
        path: coordinate map of the best path from starting point to end point 

    Returns:
        movements: the moving direction and number of steps of the car from the starting point to the end point 
    '''
    current_direct = [None, None] # current_direct[0] is the axis (x or y-axis) to be followed currently, 
                                  # and current_direct[1] is the current direction to move in (up, down, left, right) 
    start_point = path[0] # the starting point 
    movements = [] # store a list of turning directions and number of steps for driving the car
    step_count = 0  # car step counting
    current_direct = first_step(current_direct, start_point, path)

    # if the direction of change in the first step is the x-axis, then take the car as the center and first add the turning action
    if current_direct[0] == 'x' and current_direct[1] == LEFT:
        movements.append(TURN_LEFT)
    elif current_direct[0] == 'x' and current_direct[1] == RIGHT:
        movements.append(TURN_RIGHT)

    # convert the number of forward steps and turning direction of the car based on the path coordinates
    for i in range(len(path) - 1):
        current_x, current_y = path[i]
        next_x, next_y = path[i + 1]
        x_diff = next_x - current_x
        y_diff = next_y - current_y
        step_count = turning_direction_and_step(x_diff, y_diff, current_direct, movements, step_count)
    movements.append(step_count)
    return movements
