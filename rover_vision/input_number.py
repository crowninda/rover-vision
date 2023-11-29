
# check whether the input coordinates comply with the restriction rules
import sys
sys.path.append('/home/pi/picar-4wd')
import navigation
import re

class DataInput:
    def __init__(self):
        self.num_x = 0
        self.num_y = 0
    
    def check_number_range(self, num: str, axis: str) -> bool:
        '''
        confirm the range of input coordinates

        Args:
            num: input coordinates
            axis: the input coordinate is either an x-coordinate or a y-coordinate

        Returns:
                bool: return the judgment result
        '''
        if axis == "x":
            if float(num) >= navigation.MAX_X /2:
                print(f"Please input a number smaller than {int(navigation.MAX_X /2)}")
            elif float(num) < -100:
                print(f"Please input a number large than -100")
            return -100 <= float(num) < int(navigation.MAX_X /2)
        elif axis == "y":
            if float(num) >= navigation.MAX_Y:
                print(f"Please input a number smaller than {navigation.MAX_Y}")
            elif float(num) < 0:
                print(f"Please input a number large than 0")
            return 0 <= float(num) < navigation.MAX_Y
        else:
            return False


    def check_double_zero(self, num_x: int, num_y: int) -> bool:
        '''
        determine if the input coordinates are (0, 0) 

        Args:
            num_x: input x-coordinate 
            num_y: input y-coordinate 

        Returns:
                bool: boolean value of the judgment result
        '''
        return num_x == 0 and num_y == 0
    

    def is_valid_input(self, num: str) -> bool:
        '''
        exclude input values that are non-numeric characters, English, or decimal points

        Args:
            num: input coordinates 

        Returns:
                bool: boolean value of whether it meets the criteria
        '''
        num_format = re.compile(r"^\-?[0-9]+$")
        return re.match(num_format, num)


    def get_input(self, axis: str) -> None:
        '''
        rule-based judgment based on the input number

        Args:
            axis: the input str would "x" or "y"
        '''
        while True:
            user_input = input(f"Please input end point, coordinates {axis} = ")
            if self.is_valid_input(user_input):
                num = int(user_input)
                if self.check_number_range(num, axis):
                    return num
            else:
                print("Please enter an integer.")

    def check_number(self) -> int:
        '''
        input coordinates, check whether it is the origin (0, 0) and other judgments

        Returns:
                num_x (int): x-coordinate that meets the criteria
                num_y (int): y-coordinate that meets the criteria
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
    print("(x, y) = {}, {}".format(x, y))