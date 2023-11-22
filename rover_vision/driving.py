
# 自走車使用超聲波感測器得到的資料進行避障

import sys
sys.path.append('/home/pi/picar-4wd')
import picar_4wd as fc
import time

SPEED = 30 # 自走車速度設定
SCAN_DISTANCE = 30 # 超聲波掃描得到障礙物距離設定

def obstacle_relative_position(scan_list: str) -> int:
    '''
    計算障礙物對於自走車的相對位置

    Args:
        scan_list (str): 扫描是否有障碍物结果 (0, 1, 2 的字符串)
        
    Rrturns:
            pos (int): 障礙物位於自走的的相對位置
            max_obstacle (int): 最大的障礙物大小
    '''
    obstacle_number = [] # 障礙物位於自走車正前方的哪個位置，以及幾組資料為障礙物

    # 所得10組資料中，2為障礙物距離大於設定偵測距離或無障礙物者
    paths = scan_list.split("2") 
    for path in paths:

        # 在此處0代表無障礙物，其餘數字代表障礙物佔全角度(180度)的10組資料中，角度的百分比
        obstacle_number.append(len(path))
    max_obstacle = max(obstacle_number)
    largest_obstacle = obstacle_number.index(max_obstacle)
    
    # 找出最大障礙物是位於scan_list的第幾筆資料，以待後續推斷要往哪個方向走
    pos = scan_list.index(paths[largest_obstacle])

    # 計算這個障礙物地區，是位於180角正前方中的哪一邊，因為只分左中右三邊，所以除以3
    pos += int((len(paths[largest_obstacle]) - 1) / 3 )
    return pos, max_obstacle


def move_backward25():
    '''
    正前方遇到障礙物，自走車後退
    '''
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
    while True:

        # 超聲波偵測結果
        scan_list = fc.scan_step(SCAN_DISTANCE)  
        if not scan_list:
            continue

        # 確保掃描到全部角度(一輪掃描總共10筆資料)
        if len(scan_list) > 9:
            scan_list = [str(i) for i in scan_list]
            scan_list = "".join(scan_list)

            # 若幾乎正前方都無障礙物時直走
            if "22222222" in scan_list[1:9]:
               fc.forward(SPEED) 
            else:
                pos, max_obstacle = obstacle_relative_position(scan_list)
                # print("障礙物的相對位置: pos: {}".format(pos))
                # print("障礙物佔的角度個數: {}".format(max_obstacle))
                # print("scan_list :      {}".format(scan_list))
                if max_obstacle > 1:
                    if pos < 4 :  
                        fc.turn_right(SPEED)
                    elif pos > 5 : 
                        fc.turn_left(SPEED)
                    else:

                        # 當障礙物位在較中心時，先後退再根據障礙物方位選擇相反的地方移動
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

