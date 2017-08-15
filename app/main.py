import Tkinter as tk #Main Tkinter GUI interface
import tkMessageBox
import threading #Multithreading for live status updates and keepalive
from deviceclass import * #Custom writtern class to handle the KiPro
import time
import sys

DEBUG = False #Main debugger
DEBUG2 = False #Threading debugger
TESTING = False

#Define fonts used
font_unitid = ('Helvetica', 26, 'bold')
font_status = ('Helvetica', 18)
font_recbutton = ('Helvetica', 16, 'bold')
font_codecselect = ('Helvetica', 26, 'bold')
font_guibuttons = ('Helvetica', 16, 'bold')
font_title = ('Helvetica', 26, 'bold')
font_drivespace = ('Helvetica', 16, 'bold')

#Currently a constant to define the number of devices in the system. Could be moved to the settings file later
num_units = 6

#Primary application class
class KiProControl(tk.Tk):
    def __init__ (self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        #Set up the main window
        self.title("AJA KiPro Control")
        self.geometry('800x480') #Force window size for RaspberryPi touchscreen
        self.maxsize(width='800', height='480')
        self.overrideredirect(1) #Enable borderless Frame

        #Load current ip addresses from file and create devices
        #First, test to see if the file eists, if not create it
        try:
            f = open('settings/ipaddress.txt', "r")
            f.close()
            if DEBUG == True:
                print("Loaded ip file sucsesfully")
        except:
            f = open("settings/ipaddress.txt", "w+")
            f.close()
            if DEBUG == True:
                print("No ip file, new one created")

        #Try reading each line into the device list, use a default ip address if no line
        with open('settings/ipaddress.txt', "r") as f:
            count = 1 #Keep track of the number of devices created
            lines = 0 #Keep track of the number of lines in the text file
            for line in f:
                if count <= num_units: #Check that we haven't exceded the number of units to create
                    if DEBUG == True:
                        print("Creating device for " + line)
                    newdevice = Device(line.strip()) #Create a new device with the ip addresses read from the file
                    lines +=1
                    count += 1
            if count <= num_units: #If we haven't reached the number of units to create, carry on and use default ip addresses
                if DEBUG == True:
                    print("Not enough lines in ip file, creating defaults")
                while count <= num_units:
                    newdevice = Device("192.168.0.1")
                    count +=1
            f.close()

        container = tk.Frame(self) #Main holder for the entire application

        container.pack(side="top", fill="both", expand = True) #Place the main holder

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {} #Page dictionary

        PageList = (Overview, Settings, About)

        for P in (PageList):
            page = P(container, self)
            self.frames[P] = page
            page.grid(row=0, column=0, sticky="NESW")

        self.show_page(Overview) #Default startup page

    def show_page(self, cont):
        page = self.frames[cont]
        page.tkraise()


class Overview(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.configure(bg="black")

        #Images for arm and disarm buttons
        self.imgRed = tk.PhotoImage(file="images/arm_red.gif")
        self.imgBlack = tk.PhotoImage(file="images/arm_black.gif")

        #Define lists to store objects in for referencing later on parameter updates
        self.id_label_list = []
        self.status_label_list = []
        self.codec_label_list = []
        self.arm_button_list = []
        self.stopone_button_list = []
        self.recone_button_list = []
        self.armbutton = []
        self.drivespace_labels = []

        #When page is initilised, create a grid displaying all listed devices
        self.create_device_grid()

        self.arm_button_status()

        #Record button
        self.imgRecord = tk.PhotoImage(file="images/record.gif")
        btnRecord = tk.Button(self, image=self.imgRecord,
            command=lambda: self.btnRecord_click())
        btnRecord.grid(row=num_units+1, column=0, columnspan=3, padx=10)

        #Stop button
        self.imgStop = tk.PhotoImage(file="images/stop.gif")
        btnStop = tk.Button(self, image=self.imgStop, 
            command=lambda: self.btnStop_click())
        btnStop.grid(row=num_units+1, column=2, columnspan=3)

        #Arm all button
        btnArmAll = tk.Button(self, text="Arm All", font=font_guibuttons, bg="black", fg="white", 
            command=lambda: self.btnArmAll_click())
        btnArmAll.grid(row=1, column=7, sticky="we", padx=10)
        self.armbutton.append(btnArmAll)

        #Settings button
        btnSettings = tk.Button(self, text="Settings", font=font_guibuttons, bg="black", fg="white", 
            command=lambda: controller.show_page(Settings))
        btnSettings.grid(column=7, row=2, sticky="we", padx=10)
        
        #About button
        btnAbout = tk.Button(self, text="About", font=font_guibuttons, bg="black", fg="white", 
            command=lambda: controller.show_page(About))
        btnAbout.grid(column=7, row=3, sticky="we", padx=10)

        #Exit Button
        btnExit = tk.Button(self, text="Exit", font=font_guibuttons, bg="black", fg="white", 
            command=lambda: self.btnExit_click())
        btnExit.grid(column=7, row=4, sticky="we", padx=10)
        btnExit.grid_rowconfigure(0, weight=1)
        btnExit.grid_columnconfigure(0, weight=1)

        #Test Button
        if TESTING == True:
            btnExit = tk.Button(self, text="##TEST##", font=font_guibuttons, bg="black", fg="white", 
                command=lambda: self.btnTest_click())
            btnExit.grid(column=7, row=5, sticky="we", padx=10)
        
        self.start_thread()

    #Method for creating a grid to display all the devices on the Overview page
    def create_device_grid(self):
        self.imgRecOne = tk.PhotoImage(file="images/rec_one.gif")
        self.imgStopOne = tk.PhotoImage(file="images/stop_one.gif")

        #Loop to create a new line for each device in the DeviceList
        for device in DeviceList:
            #Variable linked to device id, subtract 1 for referencing objects
            i = device.device_id
            current_status = device.device_status
            current_codec = device.device_codec
            name = device.print_device_id()

            label = tk.Label(self, text=name, font=font_unitid, bg="black", fg="white")
            label.grid(column=0, row=i, padx=20, pady=10)
            self.id_label_list.append(label)

            # status = device.print_device_status()
            label = tk.Label(self, text=current_status, font=font_status, fg="white", bg="black")
            label.grid(column=1, row=i, padx=20, sticky="w")
            self.status_label_list.append(label)

            # codec = device.print_device_codec()
            label = tk.Label(self, text=current_codec, font=font_status, bg="black", fg="white")
            label.grid(column=2, row=i, padx=20, sticky="w")
            self.codec_label_list.append(label)

            button = tk.Button(self, text="rec", image=self.imgRecOne, bg="black",
                command=lambda name=i-1: self.btnRecOne_click(name))
            button.grid(column=3, row=i, padx=10)
            self.recone_button_list.append(button)

            button = tk.Button(self, text="stop", image=self.imgStopOne, bg="black",
                command=lambda name=i-1: self.btnStopOne_click(name))
            button.grid(column=4, row=i,)
            self.stopone_button_list.append(button)

            button = tk.Button(self, text="gang", bg="#828282",
                command=lambda name=i-1: self.arm_button_click(name))
            button.grid(column=5, row=i, padx=20)
            self.arm_button_list.append(button)

            label = tk.Label(self, text=device.drive_space_remaining, font=font_drivespace, bg="black", fg="white")
            label.grid(column=6, row=i, padx=5, sticky="w")
            self.drivespace_labels.append(label)

    def arm_button_click(self, button_id):
        DeviceList[button_id].arm_device()
        self.arm_button_status()

    def btnTest_click(self):
        data = DeviceList[1].getRawParameter("eParamID_CurrentMediaAvailable")

        print("=========")
        print(data)

    #Method looks for the arm status at each object in the device list
    #and appropriatly sets the arm button to match
    #Dirty: when one button is clicked it still checks all objects
    def arm_button_status(self):
        for device in DeviceList:
            #Dirty fix for id not matching list pointer
            i = device.device_id-1
            button = self.arm_button_list[i]
            if device.arm_status == True:
                button.config(image=self.imgRed)
            else:
                button.config(image=self.imgBlack)

    def btnArmAll_click(self):
        button = self.armbutton[0]
        if button['text'] == "Arm All":
            for device in DeviceList:
                device.arm_status = True
            button.config(text="Disarm All")
        elif button['text'] == "Disarm All":
            for device in DeviceList:
                device.arm_status = False
            button.config(text="Arm All")
        else:
            pass

        self.arm_button_status() #Update the individual arm buttons based on the status of the deivce

    #Set all armed devices into Record mode
    def btnRecord_click(self):
        Device.Record()

    #Stop all armed recorders
    def btnStop_click(self):
        Device.Stop()

    #Start an invidual device recording
    def btnRecOne_click(self, id_passed):
        device = DeviceList[id_passed]
        device.record_one()

    def btnExit_click(self):
        try:
            self.master.destroy()
            self.quit()
        except:
            print("Fail")


    #Stop an individual device
    def btnStopOne_click(self, id_passed):
        device = DeviceList[id_passed]
        device.stop_one()

    def updateCodecLabels(self):
        for device in DeviceList:
            device.get_current_codec()
            i = device.device_id-1
            label = self.codec_label_list[i]
            label.config(text=device.device_codec)

    #Threading code
    def live_status(self):
        if DEBUG == True:
            print("Running threading code")
        try:
            while True:
                if DEBUG2 == True:
                    print("Thread loop")

                for device in DeviceList:
                    i = device.device_id -1

                    if DEBUG == True:
                        print i
                    
                    #Update the device status
                    device.device_status = device.get_current_status()
                    
                    label = self.status_label_list[i]
                    label.config(text=device.device_status)

                    if label['text'] == "Idle":
                        label.config(fg="#0cb700")
                    if label['text'] == "Rec":
                        label.config(fg="#f20000")
                    if label['text'] == "Err":
                        label.config(fg= "#ff7700")

                    #Update the device drive space indicator
                    device.refresh_drive_space()
                    label = self.drivespace_labels[i]
                    label.config(text=str(device.drive_space_remaining) + "%")

                self.updateCodecLabels()
                time.sleep(1)
        except:
             pass

    def start_thread(self):
        t1 = threading.Thread(target=self.live_status, args=())
        t1.start()


class Settings(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        #Define lists to store objects in for referencing later on parameter updates
        self.id_label_list = []
        self.ip_entry_list = []
        self.codec_menu_list = []

        #When page is initilised, create a grid displaying all listed devices
        self.create_device_grid()

        #Overview button
        btnOverview = tk.Button(self, text="Overview", font=font_guibuttons,
            command=lambda: controller.show_page(Overview))
        btnOverview.grid(column=0, row=num_units+1, padx=15, columnspan=2, sticky="nw")

        #About button
        btnAbout = tk.Button(self, text="About", font=font_guibuttons, 
            command=lambda: controller.show_page(About))
        btnAbout.grid(column=1, row=num_units+1, columnspan=2, padx=150, sticky="nw")

        #Set ip button
        btnSetIP = tk.Button(self, text="Save IP Address Changes", font=font_guibuttons, 
            command=lambda: self.btnSetIP_click())
        btnSetIP.grid(column=2, row=num_units+1, padx=15, columnspan=2)

        #Keep the ip file up to date, adds and default ip addresses created if the text file was empty
        self.update_ip_file()

    #Method for creating a grid to display all the devices on the Overview page
    def create_device_grid(self):
        #Loop to create a new line for each device in the DeviceList
        for device in DeviceList:
            #Variable linked to device id, subtract 1 for referencing objects
            i = device.device_id

            name = device.print_device_id()
            label = tk.Label(self, text=name, font=font_unitid)
            label.grid(column=0, row=i, padx=20, pady=10)
            self.id_label_list.append(label)

            ip = device.print_device_ip()
            entry = tk.Entry(self, width=15, font=font_status)
            entry.insert(0, ip)
            entry.grid(column=1, row=i, padx=10)
            self.ip_entry_list.append(entry)

            codecmenu = tk.Menubutton(self, text=device.device_codec, relief="solid", font=font_codecselect)
            codecmenu.grid(column=2, row=i, sticky="w", padx=20)
            codecmenu.menu = tk.Menu(codecmenu, tearoff=0)
            codecmenu["menu"] = codecmenu.menu
            codecmenu.menu.add_command (label="ProRes 444", font=font_codecselect, 
                command=lambda name=i: self.change_codec(name,7))
            codecmenu.menu.add_command (label="ProRes 422 (HQ)", font=font_codecselect, 
                command=lambda name=i: self.change_codec(name, 1))
            codecmenu.menu.add_command (label="ProRes 422", font=font_codecselect, 
                command=lambda name=i: self.change_codec(name, 0))
            codecmenu.menu.add_command (label="ProRes 422 (LT)", font=font_codecselect, 
                command=lambda name=i: self.change_codec(name, 2))
            codecmenu.menu.add_command (label="ProRes 422 (Proxy)", font=font_codecselect, 
                command=lambda name=i: self.change_codec(name, 3))
            self.codec_menu_list.append(codecmenu)

    def btnSetIP_click(self):
        i = 0
        for device in DeviceList:
            entry = self.ip_entry_list[i].get()
            device.device_ip = entry
            i += 1

        self.update_ip_file()

    def update_ip_file(self):
        f = open('settings/ipaddress.txt', "w")
        for device in DeviceList:
            f.write(device.device_ip + "\n")
        f.close()

    def change_codec(self, device_id, codec_id):
        device = DeviceList[device_id-1]
        device.setCodec(codec_id)
        self.updateCodecMenu()

    def updateCodecMenu(self):
        for device in DeviceList:
            i = device.device_id-1
            menu = self.codec_menu_list[i]
            menu.config(text=device.device_codec)


class About(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        font_info = ('Helvetica', 16, '')
        font_2 = ('Helvetica', 18, 'bold')

        self.configure(bg="black")

        lblTitle = tk.Label(self, text="AJA KiPro Remote Control", font=font_title, fg="white", bg="black")
        lblTitle.grid(column=1, row=1, sticky="we")

        lblVersion = tk.Label(self, text="Version: 1.0a", font=font_info, fg="white", bg="black")
        lblVersion.grid(column=1, row=2, sticky="w")

        lblBuildDate = tk.Label(self, text="Built: 30 July 2017", fg="white", bg="black")
        lblBuildDate.grid(column=1, row=3, sticky="w")

        lblAuthor = tk.Label(self, text="Created by: Chris Farrants & Piotr Klimczyk", font=font_2, fg="white", bg="black")
        lblAuthor.grid(column=1, row=4, sticky="w")

        lblCreatedfor = tk.Label(self, text="Created for: Coldplay Tour 2017", fg="white", bg="black")
        lblCreatedfor.grid(column=1, row=5, sticky="w")

        #Overview button
        btnOverview = tk.Button(self, text="Back", font=font_guibuttons, fg="white", bg="black",
            command=lambda: controller.show_page(Overview))
        btnOverview.grid(column=1, row=6, sticky="e")


def quit_app():
    self.quit()

#Run the application
app = KiProControl()
app.mainloop()

