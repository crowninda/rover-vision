
# 檢查輸入座標是否符合限制規則
import sys
sys.path.append('/home/pi/picar-4wd')
import navigation
import re

class DataInput:
    def __init__(self):
        self.num_x = 0
        self.num_y = 0
    
    def check_number_range(self, num: str, coordinate: str) -> bool:
        '''
        確認輸入座標範圍

        Args:
            num: 輸入的座標
            coordinate: 輸入數字屬於x或y 座標

        Returns:
                bool: 回傳是否判斷結果
        '''
        if coordinate == "x":
            if float(num) > navigation.MAX_X:
                print(f"Please input a number smaller than {navigation.MAX_X}")
            elif float(num) < -100:
                print(f"Please input a number large than -100")
            return -100 <= float(num) < navigation.MAX_X 
        elif coordinate == "y":
            if float(num) > navigation.MAX_Y:
                print(f"Please input a number smaller than {navigation.MAX_Y}")
            elif float(num) < 0:
                print(f"Please input a number large than 0")
            return 0 <= float(num) < navigation.MAX_Y
        else:
            return False


    def check_double_zero(self, num_x: int, num_y: int) -> bool:
        '''
        判斷是否輸入座標為(0, 0)

        Args:
            num_x: 輸入x座標
            num_y: 輸入y座標

        Returns:
                bool: 判斷的結果布林值
        '''
        return num_x == 0 and num_y == 0
    

    def is_valid_input(self, num: str) -> bool:
        '''
        排除輸入值是非數字字符的字串、英文、小數點

        Args:
            num: 輸入的座標

        Returns:
                bool: 是否符合條件的布林值
        '''
        num_format = re.compile(r"^\-?[0-9]+$")
        return re.match(num_format, num)


    def get_input(self, coordinate: str) -> None:
        '''
        根據輸入的數字進行規則判斷

        Args:
            coordinate: 輸入的數字是x座標還是y座標
        '''
        while True:
            user_input = input(f"Please input end point, coordinates {coordinate} = ")
            if self.is_valid_input(user_input):
                num = int(user_input)
                if self.check_number_range(num, coordinate):
                    return num
            else:
                print("Please enter an integer.")

    def check_number(self) -> int:
        '''
        輸入座標，進行是否為原點(0, 0)以及其他判斷

        Returns:
                num_x (int): 符合條件的x座標. 
                num_y (int): 符合條件的y座標
        '''
        self.num_x = self.get_input("x")
        self.num_y = self.get_input("y")

        while self.check_double_zero(self.num_x, self.num_y):
            print("Please enter a non-zero coordinates.")
            self.num_x = self.get_input("x")
            self.num_y = self.get_input("y")

        return self.num_x, self.num_y

if __name__ == "__main__":
    input_number = DataInput()
    x, y = input_number.check_number()
    # print("(x, y) = {}, {}".format(x, y))