# the autonomous vehicle conducts obstacle scanning and destination navigation. 
# If an obstacle suddenly intrudes into the path, the vehicle will stop moving and only restart 
# after the obstacle has disappeared
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

MAX_X = 200  # maximum x-axis distance in map
MAX_Y = 100  # maximum y-axis distance in map
OFFSET_X = 100  # the position of the car at the x-axis coordinate when at the starting point
SPEED = 70 # The speed of the car when moving straight

log = logger.setup_logger("../Log.log")

# create an event as a trigger for the presence of an obstacle 
obstacle_event = asyncio.Event()

# MQTT connection data 
mqtt_server = getIP()   
mqtt_port = 1883  
mqtt_alive = 60  
mqtt_topic = "msg/info"

try:
    # MQTT connection 
    client = mqtt.Client()
    # connect to the MQTT server
    client.connect(mqtt_server, mqtt_port, mqtt_alive)
    # subscribe to the topic
    client.subscribe(mqtt_topic)
    # start the MQTT client message loop
    client.loop_start() 
except Exception as e:
    log.error(f"An unexpected error occurred : {str(e)}")

def highest_number_occurrences(temp: list) -> list:
    ''' 
    compare the records from 3 rounds of to-and-fro scanning, with each scan yielding 10 sets of data 
    
    Args:
        temp:  obstacle coordinate data recorded from 3 rounds of back-and-forth scanning 
    
    Returns:
        final_ans: the most frequently occurring data in each set 
    '''
    same_index = [] # coordinate information of the same angle in different scans 
    final_ans = [] # final data obtained after comparison
    for i in range(len(temp[0])):
        for j in range(len(temp)):
            same_index.append(temp[j][i])
        compare_max = max(same_index, key = same_index.count)
        final_ans.append(compare_max)
        same_index = []
    return final_ans        


def check_input_coordinates(obstacle_result: list) -> bool:
    '''
    exclude the situation where there are obstacles on the input coordinates

    Args:
        obstacle_result: obstacle coordinates

    Returns:
            input_location_is_obstacle (bool): whether the input coordinates are on an obstacle 
    '''
    input_location_is_obstacle = False
    for x_obstacle, y_obstacle in obstacle_result:
        if x_obstacle == (OFFSET_X + x_input) and y_obstacle == y_input:
            log.info("the input coordinates are on an obstacle")
            fc.backward(SPEED)
            time.sleep(0.5) #20cm
            fc.stop()
            input_location_is_obstacle = True
    return input_location_is_obstacle


async def mqtt_listener(obstacle_event: asyncio.Event) -> None: 
    '''
    establish an MQTT client to receive AI-detected obstacle results  

    Args:
        obstacle_event: event for the presence of an obstacle 
    '''
    def on_message(client, userdata, msg) -> None: 
        '''
        perform corresponding actions based on the received messages 
        Args:
            msg: the boolean value of whether there are obstacles
        '''
        message = msg.payload.decode("utf-8")

        # event activation when there are obstacles, stopping the movement of the autonomous vehicle
        if str(message) == "True": 
            fc.stop()
            obstacle_event.set() 
        elif str(message) == "False":
            obstacle_event.clear()
    
    # set up the callback function for message reception
    client.on_message = on_message


async def car_control_loop(step: list) -> None:
    '''
    move the autonomous vehicle according to the route 
    
    Args:
        step: number of steps and turning direction from start to end
    '''
    cm_exchange = 5 # convert straight walking counts into centimeters
    forward_number = 1 # the vehicle moves straight for 5cm
    turn_number = 6 # the vehicle turns 90 degrees 
    for action in step:
        if isinstance(action, int):
            adj_steps = int(action / cm_exchange) # one adj_step equates to moving straight for 5cm
            for _ in range(adj_steps):
                await perform_action('forward', forward_number)
        elif action == 'turn_left':
            await perform_action('turn_left', turn_number)
        elif action == 'turn_right':
            await perform_action('turn_right', turn_number)


async def perform_action(action: str, duration: int) -> None:
    '''
    control the motor to start and stop according to the direction and parameters of the autonomous vehicle's movement 根據自走車移動方向及參數，調控電機開始移動及停止
    
    Args:
        action: direction of the vehicle's movement 
        duration: number of loops when the vehicle walks or turns
    '''
    speed_turn = 60 # motor speed during rotation 
    for _ in range(duration):
        while obstacle_event.is_set():
            # print("here")
            await asyncio.sleep(0.5) 
        speed4 = fc.Speed(25)
        speed4.start()
        if action == 'forward':
            fc.forward(SPEED)
        elif action == 'turn_left':
            fc.turn_left(speed_turn)
        elif action == 'turn_right':
            fc.turn_right(speed_turn)
        time.sleep(0.05) 
        speed4.deinit()
        fc.stop()
        await asyncio.sleep(0)


async def main(movement: list) -> None:
    ''' 
    simultaneously carry out MQTT communication and control of the autonomous vehicle's movement
    
    Args:
        movement: the number of steps and turning direction from the starting point to the endpoint
    '''
    mqtt_task = asyncio.create_task(mqtt_listener(obstacle_event))
    car_task = asyncio.create_task(car_control_loop(movement)) 
    try:
        await asyncio.gather(mqtt_task, car_task)   
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    movement = [] # autonomous vehicle's sequential movement path and direction

    # set a destination for navigation
    while True:
        count = 1 # the number of times a round of ultrasonic scanning is conducted, used to select more stable data
        detect = True # bool for whether the ultrasonic sensor performs obstacle scanning
        temp = [] # temporary results of the scan_list from three rounds of to-and-fro scanning
        path = [] # the route from the starting point to the endpoint

        # processing and checking of input coordinates
        input_coordinate = input_number.DataInput()
        x_input, y_input = input_coordinate.check_number()
        start, goal = (OFFSET_X, 0), (OFFSET_X + x_input, y_input)
        while detect:

            # obstacle points detected by the ultrasonic sensor
            scan_list = fc.scan_step_xy() 
            if scan_list :
                if count > 1: # the first scan only rotates half a circle, so it is excluded from the calculation 
                    temp.append(scan_list)
                    if count == 4 and detect:

                        # calculate the coordinates of the most frequently appearing obstacles
                        scan_list = highest_number_occurrences(temp)

                        # process and return the coordinates of the obstacles
                        obstacle = mapping.Map(scan_list)
                        obstacle_result = obstacle.advance_mapping()

                        # ensure the input coordinates are not located on an obstacle
                        input_location_obstacle = check_input_coordinates(obstacle_result)
                        if input_location_obstacle:
                            detect = False
                            continue
                        else:  

                            # calculate the number of steps and cost required from the starting point to the endpoint and backtrack the optimal route
                            diagram = grid.GridWithWeights(MAX_X, MAX_Y)
                            diagram.walls = obstacle_result           
                            came_from, cost_so_far = a_star.a_star_search(diagram, start, goal)
                            path = a_star.reconstruct_path(came_from, start, goal)
                            
                        # if there is an optimal route, proceed with the movement of the autonomous vehicle and MQTT communication
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
            
        # after the autonomous vehicle stops moving, decide whether to make the next move
        print("If you want to quit, please press q. If you want continue, please press any value")  
        key = keyboard_control.readkey()
        
        if key == 'q':
            print("quit")  
            break 
        else: 
            del input_coordinate

            
