"""
    Object definition for a Device class

    Author: Chris Farrants
    Created: 22/07/2017
    Updated:

    Notes:
        Uses snippets from AJA
"""

import urllib
import urllib2
import json
import re

DEBUG = False

#Create a list to store all the devices in
DeviceList = []

class Device:

    #class variable: Counter to give each device and ID from 1 onwards
    device_id_counter = 1

    default_status = 'No Device'
    default_name = 'AJA KiPro Recorder'
    default_codec = 'none'

    #Initilisation method. Runs whenever a new instance of the object is created
    def __init__(self, device_ip):
        if DEBUG == True:
            print("Attempting __init__ for device number " + str(self.device_id_counter))
        #Fixed variable definitions
        self.device_id = Device.device_id_counter
        self.device_ip = device_ip
        #Updatable variable definitions
        self.device_status = Device.default_status
        self.device_codec = Device.default_codec
        self.drive_space_remaining = "#"

        self.arm_status = False #Default is device not armed

        #Store the created device in the master list
        self.create_device()

        #Update the device counter ready for the next one to be created
        Device.device_id_counter +=1

    #Called from the __init__ method. Takes the object and places it in the list for recalling
    def create_device(self):
        DeviceList.append(self)
        if DEBUG == True:
            print("DeviceList Appended")

        #Initial poll of the device for status
        self.device_status = self.get_current_status()
        self.device_codec = self.get_current_codec()

        self.drive_space_remaining = self.refresh_drive_space()

        if DEBUG == True:
            print(self.device_status)
            print(self.device_codec)

    def get_current_status(self):
        try:
            response = self.getRawParameter("eParamID_TransportState")
            selected = self.getSelected(response)
            result = (selected['text'])
            if result == "Recording":
                result="Rec"
            return result
        except:
            return "Err"

    def get_current_codec(self):
        try:
            response = self.getRawParameter("eParamID_EncodeType_Low_FR")
            selected = self.getSelected(response)
            result = (selected['text'])
            self.device_codec = result
            return result
        except:
            return "none"

    def refresh_drive_space(self):
        if DEBUG == True:
            print("Refresh Drive Space")
        try:
            response = self.getRawParameter("eParamID_CurrentMediaAvailable")
            selected = self.getSelected(response)
            result = (selected['text'])
            if DEBUG == True:
                print(result)
            self.drive_space_remaining = result
            return result
        except:
            return "#"

    #Stolen from the AJA class found online. Main get parameter method
    def getRawParameter(self, param_id):
        if DEBUG == True:
            print("Running getRawParameter request for " + param_id + "......")

        #Test device to see if it is still online
        try:
            f = urllib2.urlopen(self.device_ip, timeout=1)
            f.close()
            if DEBUG == True:
                print("Device online")
        except:
            if DEBUG == True:
                print("Device offline")
            return

        #If device is online, run the rawParameter request
        result = (None, "")
        f = None
        try:
            f = urllib2.urlopen(self.device_ip + '/options?' + param_id)
            # result = (f.getcode(), f.read())
            result = f.read()
            f.close()
            if DEBUG == True:
                print("getRawParameter request sucsess")
                print(result)
            return result
        except:
            if DEBUG == True:
                print("getRawParameter request FAIL")

    # def format_media(self, mode):
    #     #mode1 = single, mode2 = all
    #     if mode == 1:
    #         for device in DeviceList:
    #             #Send format command
    #             pass
    #     if mode == 2:
    #         #format this device
    #         pass

    #Returns the objects' device id
    def print_device_id(self):
        return self.device_id

    #Returns the objects' ip address
    def print_device_ip(self):
        return self.device_ip

    #Method for setting the objects' ip address
    def set_device_ip(self, value):
        self.device_ip = value
        self.print_device_status()

    #Returns' the objects current status
    def print_device_status(self):
        return(self.device_status)

    #Roll to record on a single device
    def record_one(self):
        self.roll_to_record()
        print(self.device_ip)
        print("RECORD")

    #Stop recording on a single device
    def stop_one(self):
        self.stop_record()
        print(self.device_ip)
        print("STOP")

    #Send http request to start device recording
    def roll_to_record(self):
        params = "newValue=3&paramName=eParamID_TransportCommand"
        try:
            f = urllib.urlopen(self.device_ip + '/config', params)
            result = (f.getcode(), f.read())
            f.close()
        except:
            print("FAIL")

    def stop_record(self):
        params = "newValue=4&paramName=eParamID_TransportCommand"
        try:
            f = urllib.urlopen(self.device_ip + '/config', params)
            result = (f.getcode(), f.read())
            f.close()
        except:
            print("FAIL")

    #Updates the objects' status. Pulled over the network
    def update_device_status(self):
        """
            TODO: Add code for pulling the status from the network
        """
        try:
            value = self.check_device_status()
            self.device_status = value
        except:
            pass

    #Checks the remote devices' status. Used for updating the labels
    def check_device_status(self):
        pass

    #Stolen from AJA class online. Cleans up the JSON response
    def cleanResponse(self, response):
        p = re.compile('([a-zA-Z_]+):')
        joined = "".join(response.splitlines())
        stripped = joined.strip(';')
        cleaned = p.sub(r'"\1":', stripped)
        return cleaned

    #From the AJA class found online
    def asPython(self, response):
        result = None
        try:
            result = json.loads(response)
        except:
            result = json.loads(self.cleanResponse(response))
        return result

    def getSelected(self, response):
        result = None
        options = self.asPython(response)
        for option in options:
            if "selected" in option:
                if option["selected"] == "true":
                    result = option
                    break
        return result

    #Set the codec on a specific device
    def setCodec(self, codec_id):
        param = "eParamID_EncodeType_Low_FR"
        value = codec_id

        params = urllib.urlencode({'paramName':param, 'newValue' : value})
        try:
            f = urllib.urlopen(self.device_ip + '/config', params)
            result = (f.getcode(), f.read())
            f.close()
        except:
            print("FAIL")

        #Update the object codec variable
        self.print_device_codec()

    #Method arms or disarms the device
    def arm_device(self):
        if self.arm_status == False:
            self.arm_status = True
        else:
            self.arm_status = False

    #Method for starting the all devices recording
    @classmethod
    def Record(cls):
        for device in DeviceList:
            if device.arm_status == True:
                device.roll_to_record()

    #Method for stopping all devices recording
    @classmethod
    def Stop(cls):
        for device in DeviceList:
            device.stop_record()
