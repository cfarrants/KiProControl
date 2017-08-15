"""
    Object definition for a Device class

    Author: Chris Farrants
    Created: 22/07/2017
    Updated:

    Notes:
        Uses snippets from AJA
"""

import urllib 
import json
import re

#Create a list to store all the devices in
DeviceList = []

class Device:

    #class variable: Counter to give each device and ID from 1 onwards
    device_id_counter = 1

    default_status = 'Not Connected'
    default_name = 'AJA KiPro Recorder'
    default_codec = 'none'

    #Initilisation method. Runs whenever a new instance of the object is created
    def __init__(self, device_ip):
        self.device_id = Device.device_id_counter
        self.device_ip = device_ip
        self.device_status = Device.default_status
        self.device_codec = Device.default_codec
        self.arm_status = False #Default is device not armed

        #Store the created device in the master list
        self.create_device()

        Device.device_id_counter +=1

    #Called from the __init__ method. Takes the object and places it in the list for recalling
    def create_device(self):
        DeviceList.append(self)
        pass

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

    #Returns' the objects current status
    def print_device_codec(self):
        # return(self.device_codec)
        (httpcode, response) = self.getRawParameter("eParamID_EncodeType_Low_FR")
        result = ("","")
        selected = self.getSelected(response)
        result = (selected['text'])
        self.device_codec = result
        return result

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
        value = self.check_device_status()
        self.device_status = value

    #Checks the remote devices' status. Used for updating the labels
    def check_device_status(self):
        (httpcode, response) = self.getRawParameter("eParamID_TransportState")
        result = ("","")
        selected = self.getSelected(response)
        result = (selected['text'])
        return result

    def getRawParameter(self, param_id):
        """ Returns (http error code, a json string containing all the information about the param including its current value) """
        result = (None, "")
        f = None
        try:
            f = urllib.urlopen(self.device_ip + '/options?' + param_id)
            result = (f.getcode(), f.read())
            f.close()
        except:
            if f is not None:
                f.close()
            raise

        return result

    def cleanResponse(self, response):
        """
        This deals with some historical peculiarities in Ki-Pro JSON formatting.
        """
        p = re.compile('([a-zA-Z_]+):')
        joined = "".join(response.splitlines())
        stripped = joined.strip(';')
        cleaned = p.sub(r'"\1":', stripped)
        return cleaned

    def asPython(self, response):
        """
        Convert a Ki-Pro response into a python object
        (usually an array of dictionaries depending on the json).
        """
        result = None
        try:
            result = json.loads(response)
        except:
            result = json.loads(self.cleanResponse(response))
        return result

    def getSelected(self, response):
        """
        The JSON returned is a list of all possible values for enum parameters with 
        the current value marked as selected. Integer and string parameters
        are returned in the same way with just one entry in the list.
        Return the selected value entry in the list.
        """
        result = None
        options = self.asPython(response)
        for option in options:
            if "selected" in option:
                if option["selected"] == "true":
                    result = option
                    break
        return result

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

    #Method for starting the device recording
    @classmethod
    def Record(cls):
        for device in DeviceList:
            if device.arm_status == True:
                device.roll_to_record()

    #Method for stopping the device recording
    @classmethod
    def Stop(cls):
        for device in DeviceList:
            device.stop_record()
