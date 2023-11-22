
# 根據算法提供最佳路線座標，依序轉換為自走車前進步數與轉彎方向
import sys
sys.path.append('/home/pi/picar-4wd')

# 常量
TURN_LEFT = "turn_left"
TURN_RIGHT = "turn_right"
UP = "up"
DOWN = "down"
RIGHT = "right"
LEFT = "left"


def turning_direction_and_step(x_diff: int, y_diff: int, current_direct: list, movements: list, step_count: int) -> list:
    ''' 
    判斷自走車接下來要採取的動作和走的步數
    
    Args: 
        x_diff: 計算當下與下一步的 x座標的差異
        y_diff: 計算當下與下一步的 y座標的差異
        current_direct: 自走車當下動作
        movements: 紀錄自走車依序應該做的動作 
    
    Returns:
        step_count: 最後一個轉彎後，直走的步數
    '''

    # 下一步 y 座標變動
    if y_diff != 0:

        # 當下的動作方向是x軸改變
        if current_direct[0] == "x":

            # 當自走車下一步的x或y軸變化時，代表車子即將改變方向，將累計的步數存入
            movements.append(step_count)

            # 步數歸零，重新計算
            step_count = 0

            # 當自走車下一步 y座標增加且當下前進的方向向右，或y座標減少且當下前進的方向向左，則接下來要向左轉
            if (y_diff > 0 and current_direct[1] == RIGHT) or (y_diff < 0 and current_direct[1] == LEFT):               
                movements.append(TURN_LEFT)

            # 當自走車下一步 y座標減少且當下前進的方向向右，或y座標增加且當下前進的方向向左，則接下來要向右轉
            elif (y_diff < 0 and current_direct[1] == RIGHT) or (y_diff > 0 and current_direct[1] == LEFT):
                movements.append(TURN_RIGHT)
        
        # 修改當前動作座標變化為y軸
        current_direct[0] = "y"

        if y_diff > 0: 
            current_direct[1] = UP
        elif y_diff < 0: 
            current_direct[1] = DOWN
   
    elif x_diff != 0:
        if current_direct[0] == "y":
            movements.append(step_count)
            step_count = 0
            if (x_diff < 0 and current_direct[1] == UP) or (x_diff > 0 and current_direct[1] == DOWN):
                movements.append(TURN_LEFT)   
            elif (x_diff < 0 and current_direct[1] == DOWN) or (x_diff > 0 and current_direct[1] == UP):
                movements.append(TURN_RIGHT)

        current_direct[0] = "x"

        if x_diff > 0: 
            current_direct[1] = RIGHT
        elif x_diff < 0: 
            current_direct[1] = LEFT

    # 當自走車保持相同x或y周方向前進時，步數持續增加
    step_count += 1
    return step_count


def first_step(current_direct: list, start_point: int, path: list) -> list:
    ''' 
    確定自走車的第一步 是沿著哪軸，並朝哪一個方向走
    
    Args:
        current_direct: 第1步相較起點座標要走的方向
        start_point: 最佳路徑圖的起點座標
        path: 最佳路徑圖
    
    Returns:
        current_direct: 得到變動的軸向與方向
    '''
    
    # x 座標變化
    if start_point[0] != path[1][0]: 
        current_direct[0] = "x"
        if path[1][0] > start_point[0]: 
            current_direct[1] = RIGHT
        else: 
            current_direct[1] = LEFT
    
    # y 座標變化
    elif start_point[1] != path[1][1]:
        current_direct[0] = "y"
        if path[1][1] > start_point[1]:
            current_direct[1] = UP
        else: 
            current_direct[1] = DOWN

    print("first_step: {}".format(current_direct))
    return current_direct


def calculate_movement(path: list) -> list:
    '''
    根據座標list，換算自走車要做的動作

    Args:
        path: 起點到終點最佳路徑的座標圖

    Returns:
        movements: 自走車自起點到終點依序的移動方位及步數 
    '''
    current_direct = [None, None] # current_direct[0] 是當下要走的軸(x或y軸)  current_direct[1] 是當下要走的方向(上 下 左 右)
    start_point = path[0] # 自走車移動路線的第一個座標位置
    movements = [] # 儲存驅動的方向與步數的列表
    step_count = 0  # 驅動的步數計數

    # 觀察第一步要移動的座標軸與方向
    current_direct = first_step(current_direct, start_point, path)

    # 若第一步改變的方向是x軸，且左或右走，則以自走車為中心，先加入轉彎的動作
    if current_direct[0] == 'x' and current_direct[1] == LEFT:
        movements.append(TURN_LEFT)
    elif current_direct[0] == 'x' and current_direct[1] == RIGHT:
        movements.append(TURN_RIGHT)


    # 根據路徑座標換算自走車前進步數與轉彎方向
    for i in range(len(path) - 1):
        current_x, current_y = path[i]
        next_x, next_y = path[i + 1]
        x_diff = next_x - current_x
        y_diff = next_y - current_y

        # 此step_count為最後一段要走的步數長
        step_count = turning_direction_and_step(x_diff, y_diff, current_direct, movements, step_count)
    movements.append(step_count)
    return movements
