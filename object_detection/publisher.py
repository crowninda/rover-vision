
# This is a Python function used to transmit the Boolean results of obstacle detection to subscribers via MQTT.
# The function accepts the result of obstacle detection and publishes it to the specified MQTT topic without returning any data.
import paho.mqtt.client as mqtt  

MQTT_SERVER = "your Internal IP" 
MQTT_PORT = 1883  
MQTT_ALIVE = 60  
MQTT_TOPIC = "msg/info" 

mqtt_client = mqtt.Client()  
mqtt_client.connect(MQTT_SERVER, MQTT_PORT, MQTT_ALIVE)   

# Send ai recognition results to PiRoverVision project
def publish(ans)->None:
  """
  Send the AI ​​recognition results to the MQTT client.

  Args:
      ans (str): The result of AI identifying whether there are obstacles, should be 'True' or 'False'.
  """
  payload = ans
  mqtt_client.publish(MQTT_TOPIC, payload, qos=2)
  mqtt_client.loop_start() 
