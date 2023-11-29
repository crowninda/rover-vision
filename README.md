## PiRoverVision


Quick Links:

 * [Description](#Project_Name_and_Description)
 * [Install](#Installation_Instructions)
 * [User's_Guide](#Usage_Instructions)
 * [License](#License)
 * [Version](#Version_History)
 * [Contact_us](#Contact_Us)
 * [Acknowledgments](#Acknowledgments)
 * [Related_links](#Related_Links)



----------------------------------------------
<a id="Project_Name_and_Description"></a>
### Project_Name_and_Description： 
- PiRoverVision
- This project is an extension of the [picar-4wd](https://github.com/sunfounder/picar-4wd) project provided by a Coursera course, aimed at adding obstacle avoidance, map drawing, object detection, and navigation features to the Raspberry Pi self-driving car.


----------------------------------------------
<a id="Installation_Instructions"></a>
### Installation Instructions：

- Please follow the [installation steps](https://m.media-amazon.com/images/I/C1Tq1JjfipS.pdf) provided by picar to install on Raspberry Pi.

- Download [TensorFlow Lite](https://github.com/tensorflow/examples/blob/master/lite/examples/object_detection/raspberry_pi/README.md)  and set up a virtual environment.

- Install MQTT and configure it accordingly.

- Moving Files in the 'object_detection' Folder：
  1. In my project, you will find a folder named 'object_detection'.
  2. This folder contains two files: repo_detect.py and publisher.py.
  3. Copy these files into the same folder where the 'detect.py' file is located in the TensorFlow Lite object detection project.
    -   This file arrangement aims to improve the code's maintainability and readability, ensuring that the object detection functionality operates efficiently and independently from other system components.

- Moving the 'rover_vision' Folder:
  1. Locate the 'rover_vision' folder in my project.
  2. Move this folder to the original picar-4wd project, ensuring it is placed at the same level as the 'picar_4wd' folder.

- Moving 'init.py':
  1. Find the 'init.py' file in the 'picar_4wd' folder of my project.
  2. Move this file to the same-name 'picar_4wd' folder in the original picar-4wd project, overwriting the existing file.
    - For using the navigation feature, please refer to the 'requirement_car.txt' for guidance on setting up the necessary virtual environment on your Raspberry Pi.


----------------------------------------------
<a id="Usage_Instructions"></a>
### Usage Instructions：

- Obstacle Avoidance: :
  Detailed Description：
  - The obstacle avoidance feature enables the self-driving car to automatically stop or change its route upon encountering obstacles, thus preventing collisions. This is facilitated by an ultrasonic sensor that detects obstacles ahead and reacts based on the sensor data.
  Configuration and Usage Steps :
    1. Ensure the ultrasonic sensor is properly installed and connected to the Raspberry Pi.
    2. In the picar-4wd project, navigate to the corresponding file location, open the Terminal, and activate the virtual environment.
    3. Run the following command to activate the obstacle avoidance feature:
      ```python3 driving.py```

- Map Drawing :
  Detailed Description :
  - This feature uses the ultrasonic sensor to scan the surrounding area and converts the data into a map representation.
  Configuration and Usage Steps :
    1. Ensure the ultrasonic sensor is functioning correctly.
    2. In the picar-4wd project, go to the file's location, open the Terminal, and make sure the virtual environment is active.
    3. Execute the following command to draw the map:
      ```python3 mapping.py```

- Object Detection :
  Detailed Description：
  - This function uses the camera module to detect if a target appears and then notifies accordingly.
  Configuration and Usage Steps :
    1. Ensure the camera is working properly.
    2. Make sure the virtual environment of the Tensorflow lite project is active
    3. Enter the Internal IP in publisher.py
    4. At the path of repo_detect.py in the Tensorflow lite project, open the Terminal and execute the following command to start the object detection feature:
      ```python3 repo_detect.py```

- Navigation Function : 
  Detailed Description：
  - Enables the rover to autonomously navigate to a destination specified by the user. Utilizing obstacle location data from sensors, combined with object detection and path planning algorithms, the rover can calculate the optimal route to the destination and move to the endpoint.
  Configuration and Usage Steps :
    1. Ensure the MQTT service is running to facilitate communication between projects.
    2. Make sure the object detection feature is activated.
    3. In the picar-4wd project, open a Terminal at the path of navigation.py and execute the following command to start the navigation feature:
      ```python3 navigation.py```
    4. Follow prompts to input destination coordinates; the car will move according to the calculated path.


----------------------------------------------
<a id="License"></a>
### License：
- The original project is under the GPL license. You can see the full text of the GPL license in the LICENSE file,[link](https://www.gnu.org/licenses/gpl-3.0.en.html)
- This project includes modified code from [picar-4wd](https://github.com/sunfounder/picar-4wd), which is available under the GNU General Public License, version 2. The modifications were made by Hsinghua Lu to add some new functions, including modifying the sleep time of the ultrasonic sensor and calculating and returning obstacle coordinates, in the file init.py located in the picar_4wd folder.


----------------------------------------------
<a id="Version History"></a>
### Version_History：
- Version 1.0.0  18 November 2023
- Version 2.0.0  29 November 2023

----------------------------------------------
<a id="Contact_Us"></a>
### Contact Us
- Hsinghua Lu
- crowninda@gmail.com


----------------------------------------------
<a id="Acknowledgments"></a>
### Acknowledgments
- In the object detection part of the project, we have used code from TensorFlow Lite, which is released under the Apache 2.0 license. A [license](https://github.com/tensorflow/tensorflow) declaration and acknowledgment is attached. 
- Additionally, the autonomous car navigation algorithm utilizes code that is also published under the Apache 2.0 license. An acknowledgment and the [license](https://opensource.org/license/apache-2-0/) declaration are hereby included.


----------------------------------------------
<a id="Related_Links"></a>
### Related Links
- [A* algorithm](http://theory.stanford.edu/~amitp/GameProgramming/)
- [Installation of picar-4wd](https://m.media-amazon.com/images/I/C1Tq1JjfipS.pdf)
- [Obstacle avoidance videos](https://www.youtube.com/watch?v=ysPxrZEFabw)