
# 自走車進行障礙物掃描及目的地導航，若臨時有障礙物闖入路徑則停止移動直到障礙物消失再重新啟動
import sys
sys.path.append('/home/pi/picar-4wd')
from picar_4wd import getIP
from examples import keyboard_control
import picar_4wd as fc
import action
import mapping
import grid
import a_star
import asyncio
import paho.mqtt.client as mqtt  
import input_number
import time
import logger

MAX_X = 200  # 地圖的最大寬度
MAX_Y = 100  # 地圖的最大高度
OFFSET_X = 100  # x 座標的位移量
SPEED_TURN = 60 # 旋轉時電機速度
SPEED = 70 # 直走時的電機速度


# MQTT 連線資料
mqtt_server = getIP()   
mqtt_port = 1883  
mqtt_alive = 60  
mqtt_topic = "msg/info"

log = logger.setup_logger("../Log.log")

# 創建事件作為障礙物是否存在的觸發器
obstacle_event = asyncio.Event()

def highest_number_occurrences(temp: list) -> list:
    ''' 
    將4次掃描紀錄進行比對，每次掃描會得10組資料
    
    Args:
        temp: 4次掃描紀錄的障礙物座標資料
    
    Returns:
        final_ans: 同組資料中各自出現次數最多者
    '''
    same_index = [] # 不同次掃描中 同組的座標資訊
    final_ans = [] # 比對後得到最終資料
    for i in range(len(temp[0])):
        for j in range(len(temp)):
            same_index.append(temp[j][i])
        # 進行各組座標出現次數比對
        compare_max = max(same_index, key = same_index.count)
        final_ans.append(compare_max)
        same_index = []

    return final_ans        


def check_input_coordinates(obstacle_result: list) -> bool:
    '''
    排除輸入座標上面有障礙物的情況

    Args:
        obstacle_result: 障礙物座標

    Returns:
            input_location_is_obstacle (bool): 輸入座標是否在障礙物上
    '''
    input_location_is_obstacle = False
    for x_obstacle, y_obstacle in obstacle_result:
        if x_obstacle == (OFFSET_X + x_input) and y_obstacle == y_input:
            print("輸入座標上面是障礙物")
            input_location_is_obstacle = True
    return input_location_is_obstacle


async def mqtt_listener(obstacle_event: asyncio.Event) -> None: 
    '''建立 MQTT client 接收AI辨識障礙物結果  

    Args:
        obstacle_event: 是否有障礙物的事件
    '''
    # 定義 MQTT 回調函數來處理
    def on_message(client, userdata, msg) -> None: 
        '''
        根據接收的消息進行相對應的動作執行
        Args:
            msg: 是否有障礙物的布林值
        '''
        message = msg.payload.decode("utf-8") 
        # 有障礙物時事件啟動，自走車停止移動
        if str(message) == "True": 
            obstacle_event.set() 
        elif str(message) == "False":
            obstacle_event.clear()
    try:
        # 創建 MQTT client
        client = mqtt.Client()
        # 設置消息接收的回調函數
        client.on_message = on_message
        # 連接到 MQTT 服務器
        client.connect(mqtt_server, mqtt_port, mqtt_alive)
        # 訂閱主題
        client.subscribe(mqtt_topic)
        # 啟動 MQTT client 消息循環
        client.loop_start() 
    except Exception as e:
        log.error(f"An unexpected error occurred : {str(e)}")


async def car_control_loop(step: list) -> None:
    '''
    根據行動路徑，使自走車移動方向
    
    Args:
        step: 由起點到終點行走的步數及轉彎方向
    '''
    cm_exchange = 5 # 直走次數換算成公分
    forward_number, turn_number = 1, 6 # 電機的運轉次數 
    for action in step:
        if isinstance(action, int):
            # 1個adj_steps，為直走5cm
            adj_steps = int(action / cm_exchange)
            for _ in range(adj_steps):
                await perform_action('forward', forward_number)
        elif action == 'turn_left':
            await perform_action('turn_left', turn_number)
        elif action == 'turn_right':
            await perform_action('turn_right', turn_number)


async def perform_action(action: str, duration: int) -> None:
    '''
    根據自走車移動方向及參數，調控電機開始移動及停止
    
    Args:
        action: 車子行走方向
        duration: 車子要走多遠或角度要轉動多少
    '''
    for _ in range(duration):
        while obstacle_event.is_set():
            await asyncio.sleep(1)
        speed4 = fc.Speed(25)
        speed4.start()
        if action == 'forward':
            fc.forward(SPEED)
        elif action == 'turn_left':
            fc.turn_left(SPEED_TURN)
        elif action == 'turn_right':
            fc.turn_right(SPEED_TURN)
        time.sleep(0.1)
        speed4.deinit()
        fc.stop()


async def main(movement: list) -> None:
    ''' 
    同步進行 MQTT 通信及自走車移動控制
    
    Args:
        movement: 由起點到終點行走的步數及轉彎方向
    '''
    mqtt_task = asyncio.create_task(mqtt_listener(obstacle_event))
    car_task = asyncio.create_task(car_control_loop(movement)) 
    try:
        await asyncio.gather(mqtt_task, car_task)   
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    count = 1 # 超聲波掃描一輪後的次數，作用為挑選較穩定的資料
    movement = [] # 移動自走車的路徑及方向設定

    # 是否設定終點 進行導航
    while True:
        detect = True # 超聲波感測器是否進行 障礙物掃瞄
        temp = [] # 四輪的scan_list的暫存結果
        path = [] # 起點到終點路線

        # 進行輸入座標的檢查處理
        input_coordinate = input_number.DataInput()
        x_input, y_input = input_coordinate.check_number()
        start, goal = (OFFSET_X, 0), (OFFSET_X + x_input, y_input)
        while detect:

            # 超聲波感測器得到障礙物的點位
            scan_list = fc.scan_step_xy() 
            if scan_list :
                if count > 1: # 第一次掃描只有轉動半圈，所以排除不計算 
                    temp.append(scan_list)
                    if count == 5 and detect:

                        # 進行出現最高次數的障礙物座標計算
                        scan_list = highest_number_occurrences(temp)
                
                        # 加工並回傳障礙物的點位
                        obstacle = mapping.Map(scan_list)
                        obstacle_result = obstacle.advance_mapping()
        
                        # 確認輸入座標不位於障礙物上
                        input_location_obstacle = check_input_coordinates(obstacle_result)
                        if input_location_obstacle:
                            detect = False
                            continue
                        else:  

                            # 計算 起點到終點需要走的步數及所需代價並回推最佳路徑
                            diagram = grid.GridWithWeights(MAX_X, MAX_Y)
                            diagram.walls = obstacle_result           
                            came_from, cost_so_far = a_star.a_star_search(diagram, start, goal)
                            path = a_star.reconstruct_path(came_from, start, goal)
                    
                        # 若有最佳路徑，則進行自走車移動以及 MQTT 通信
                        if path:
                            movement = action.calculate_movement(path) 
                            detect = False
                            asyncio.run(main(movement))
                        else:
                            print("No path, backward.")
                            fc.backward(SPEED)
                            time.sleep(0.5) #20cm
                            fc.stop()
                            detect = False
                            continue     
                count += 1 
            
        # 自走車結束移動，決定是否進行下一次移動
        print("If you want to quit, please press q. If you want continue, please press any value")  
        key = keyboard_control.readkey()
        
        if key == 'q':
            print("quit")  
            break 
        else: 
            del input_coordinate
            count = 1
            continue
            
