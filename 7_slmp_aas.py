# -----------------------------------------------------------------------------
# ReDi School Lesson 5 - SLMP
# -----------------------------------------------------------------------------
#
# Usage of SLMP package and MQTT
# 
# Created by Matthias Mueller, FA-EDC, Mitsubishi Electric Europe B.V.
# -----------------------------------------------------------------------------

from datetime import datetime
from time import sleep
from pymcprotocol import mcprotocolconst
from pymcprotocol.type3e import Type3E
#Requires numpy to be installed
import numpy as np
import socket
import paho.mqtt.client as mqtt
import json

from mitsubishi_aas_client import MitsubishiApiRestClient

# SLMP Information
ipAddress = '194.145.95.179'
portNumbers = [3002]

# Information of the MQTT Brokers
MQTT_BROKER_IP = "test.mosquitto.org" #"i40.mitsubishielectric.de"; 
MQTT_BROKER_PORT = 1883
MQTT_QOS = 1
MQTT_CLIENT_ID = "ReDI-Schueler-" + socket.gethostname()
# Change the topic to the PLC that you have
MQTT_TOPIC = "ReDI-School/"
MQTT_USERNAME="ReDI"
MQTT_PASSWORD="XG#oLG%ubuN4"
print(MQTT_CLIENT_ID)

def readAndDisplayPlcTypeName():
    plcType = slmp.read_cputype()
    print(f'PLC type name: {plcType[0]}')
    print(f'PLC type code: {plcType[1]}')

def stopWait5SecondsAndStopPlc():
    slmp.remote_stop()
    print('PLC stopped')

    sleep(5)

    slmp.remote_run(clear_mode=0, force_exec=False)
    print('PLC started')

def readDevice(slmp, device):
    values = slmp.randomread([device], [])
    return values[0][0]

def writeDevice(slmp, device, value):
    slmp.randomwrite([device], [value], [], [])

# Connect to the MQTT Broker
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    
# Read status information from the PLC via SLMP and publish via MQTT
def read_and_send_status(slmp):
    status_info = {}     #Information to be published with low frequency
    
    # Operating Status
    device = 'SD203'
    value = readDevice(slmp, device)
    print(f'Operating Status={value} (0: RUN, 2: STOP, 3: PAUSE)')
    status_info["operating_status"] = value

    # LED Status
    device = 'SD201'
    value = readDevice(slmp, device)
    print(f'LED status={bin(value).replace("0b","")} ')
    status_info["led_status"] = bin(value).replace("0b","")

    # Clock Data (7 Devices)
    device = 'SD210'
    value = slmp.batchread_wordunits(device, 7)
    print(f'Clock Data={value} ')
    status_info["clock_data"] = value

    # Scan Times (6 Devices)
    value = slmp.batchread_wordunits('SD520', 6)
    print(f'Scan Times={value}')
    status_info["scan_time"] = value

    # add a time stamp
    status_info["time_stamp"] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S.%f")

    # publish to the client, also as retained message
    client.publish(mqtt_topics[x] + "/StatusInfo", json.dumps(status_info), retain=True)

#Read runtime data/values from the PLC via SLMP and publish via MQTT
def read_and_send_runtime(slmp):
    
    runtime_data = {}   #Information to be published with high frequency

   

    # read Runtime Values
    value = slmp.batchread_wordunits('D400', 10)
    print(f'Batch Read: {value}')
    runtime_data["data"] = value

    # Scan Counter
    value = readDevice(slmp, 'SD420')
    print(f'Scan Counter={value}')
    runtime_data["scan_counter"] = value

    # add a time stamp
    runtime_data["time_stamp"] = datetime.now().strftime("%m/%d/%Y, %H:%M:%S.%f")
    
    #Publish
    client.publish(mqtt_topics[x] + "/RuntimeData", json.dumps(runtime_data))

    motor1temp = runtime_data["data"][3]
    print(f'Motor1: cur{motor1temp} with min {motor_range[0]["min"]} and max {motor_range[0]["max"]}')
    if motor1temp >= int(motor_range[0]["max"]):
        msg = {msg : "Temperature too high",
               "cur" : motor1temp,
               "max" : motor_range[0]["max"]}
        client.publish(mqtt_topics[x] + "Motor1Msg", json.dumps(msg))  

    if motor1temp >= int(motor_range[0]["min"]):
        msg = {msg : "Temperature too low",
               "cur" : motor1temp,
               "min" : motor_range[0]["min"]}
        client.publish(mqtt_topics[x] + "Motor1Msg", json.dumps(msg))     
        print("Temperuature too low")  

    motor2temp = runtime_data["data"][4]
    print(f'Motor2: cur{motor2temp} with min {motor_range[0]["min"]} and max {motor_range[0]["max"]}')
    if motor2temp >= int(motor_range[0]["max"]):
        msg = {msg : "Temperature too high",
               "cur" : motor2temp,
               "max" : motor_range[0]["max"]}
        client.publish(mqtt_topics[x] + "Motor2Msg", json.dumps(msg))  

    if motor2temp >= int(motor_range[0]["min"]):
        msg = {msg : "Temperature too low",
               "cur" : motor2temp,
               "max" : motor_range[0]["min"]}
        client.publish(mqtt_topics[x] + "Motor2Msg", json.dumps(msg)) 
        print("Temperuature too low")   
            

# initialize the MQTT client and connect to the broker    
client = mqtt.Client(client_id = MQTT_CLIENT_ID, clean_session = True)
client.on_connect = on_connect
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
client.connect(MQTT_BROKER_IP, MQTT_BROKER_PORT, 60)

aas_client = MitsubishiApiRestClient()
motor_range = aas_client.get_motor_ranges('R01CPU_00053B17C0010081')
for r in motor_range:
    print(f'{r["idShort"]} with min {r["min"]} and max {r["max"]}')
# wait for MQTT Connection to be established
#while not client.is_connected():
#    sleep(2)

# create SLMP objects
slmp_list = []
mqtt_topics = []
for port in portNumbers:
    slmp = Type3E(mcprotocolconst.iQR_SERIES)

    # create SLMP connection
    try:
        slmp.connect(ipAddress, port)
        if slmp._is_connected:
            print(f'Connected to {ipAddress}:{port}')
            slmp_list.append(slmp)
            # set extend the base part of the topic to be unique we use the CPU Type and the Port
            mqtt_topics.append(MQTT_TOPIC + str(port))
    except:
        print("Failed")        


print(f'No. of successfull SLMP connections {len(slmp_list)}')
# confirm SLMP connection
if len(slmp_list) != 0:
    
    
    
    for x in range(len(slmp_list)):
        # first, tell the CPU to write the Clock Data into the devices
        slmp_list[x].batchwrite_bitunits("SM213", [1])
        

        # define the object that shall contain information to be published
        base_info = {}      
        
        # read, display and use PLC Type as topic
        cputype = slmp_list[x].read_cputype()
        print(f'Name {cputype[0]} with Code {cputype[1]}')
        base_info["cpu_type"] = cputype[0]
        
       
        
        # time Zone
        value = readDevice(slmp_list[x], 'SD218')    
        print(f'Time Zone Setting (UTC)={value/60}')
        base_info["time_zone"] = value
    
        # firmware Version
        device = 'SD160'
        value = readDevice(slmp_list[x],device)
        print(f'Firmware={value}')
        base_info["firmware"] = value

        # publish the Base Information once, make it retained on the brocker
        client.publish(mqtt_topics[x] + "/BaseInfo", json.dumps(base_info), retain=True)

    sleep(3)    
    
    # Main Loop
    count = 0
    main_sleep = 2
    status_factor = 5
    while count < 1000:
        
        # call status only every 5th cycle
        if count % status_factor == 0:
            for x in range(len(slmp_list)):
                read_and_send_status(slmp_list[x])
        
        for x in range(len(slmp_list)):
            read_and_send_runtime(slmp_list[x])
        
        count += 1
        sleep(main_sleep)

    for slmp in slmp_list:
        slmp.close()
    print('Connection closed')
else:
    print('Connection failed!')

