import Tkinter as tk #Main Tkinter GUI interface
import tkMessageBox
import threading #Multithreading for live status updates and keepalive
from deviceclass import * #Custom writtern class to handle the KiPro
import time

font_unitid = ('Helvetica', 26, 'bold')
font_status = ('Helvetica', 18)
font_recbutton = ('Helvetica', 16, 'bold')
font_codecselect = ('Helvetica', 26, 'bold')
font_guibuttons = ('Helvetica', 16, 'bold')
font_title = ('Helvetica', 26, 'bold')

num_units = 6

class KiProControl(tk.Tk):
    def __init__ (self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("AJA KiPro Control")
        self.geometry('800x480') #Force window size for RaspberryPi touchscreen
        self.maxsize(width='800', height='480')

        #Load current ip addresses from file and create devices
        #First, test to see if the file eists, if not create it
        try:
            f = open('settings/ipaddress.txt', "r")
            f.close()
        except:
            f = open("settings/ipaddress.txt", "w+")
            f.close()

        #Try reading each line into the device list, use a default ip address if no line
        with open('settings/ipaddress.txt', "r") as f:
            count = 1
            lines = 0
            for line in f:
                newdevice = Device(line.strip())
                lines +=1
                count += 1
            if count <= num_units:
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

    @classmethod
    def popup_box(cls):
        tkMessageBox.showinfo("About", "AJA KiPro Remote Control. Build 1a. Created by: Chris Farrants. Created for Coldplay Tour 2017")


class Overview(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        #Images for arm and disarm buttons
        self.imgRed = tk.PhotoImage(file="images/arm_red.gif")
        self.imgBlack = tk.PhotoImage(file="images/arm_black.gif")

        #Define lists to store objects in for referencing later on parameter updates
        self.id_label_list = []
        self.status_label_list = []
        self.codec_label_list = []
        self.arm_button_list = []

        #When page is initilised, create a grid displaying all listed devices
        self.create_device_grid()

        self.arm_button_status()

        #Record button
        self.imgRecord = tk.PhotoImage(file="images/record.gif")
        btnRecord = tk.Button(self, image=self.imgRecord,
            command=lambda: self.btnRecord_click())
        btnRecord.grid(row=1, column=4, rowspan=2)

        #Stop button
        self.imgStop = tk.PhotoImage(file="images/stop.gif")
        btnStop = tk.Button(self, image=self.imgStop, 
            command=lambda: self.btnStop_click())
        btnStop.grid(row=3, column=4, rowspan=2)

        #Arm all button
        btnArmAll = tk.Button(self, text="Arm All", font=font_guibuttons, 
            command=lambda: self.btnArmAll_click())
        btnArmAll.grid(row=5, column=4)

        #Disarm all button
        btnDisarmAll = tk.Button(self, text="Disarm All", font=font_guibuttons, 
            command=lambda: self.btnDisarmAll_click())
        btnDisarmAll.grid(row=6, column=4)

        #Settings button
        btnSettings = tk.Button(self, text="Settings", font=font_guibuttons, 
            command=lambda: controller.show_page(Settings))
        btnSettings.grid(column=0, row=num_units+1, padx=15, columnspan=2, sticky="nw")

        #About button
        btnAbout = tk.Button(self, text="About", font=font_guibuttons, 
            command=lambda: controller.show_page(About))
        btnAbout.grid(column=1, row=num_units+1, columnspan=2, padx=150, sticky="nw")

        #CP AHFD Logo
        self.imgLogo = tk.PhotoImage(file="images/cp_logo.gif")
        lblLogo = tk.Label(self, image=self.imgLogo)
        lblLogo.grid(column=4, row=num_units+1, sticky="SE")

        self.start_thread()

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

            status = device.print_device_status()
            label = tk.Label(self, text=status, font=font_status, fg="green")
            label.grid(column=1, row=i, padx=10, sticky="w")
            self.status_label_list.append(label)

            codec = device.print_device_codec()
            label = tk.Label(self, text="Codec: " + codec, font=font_status)
            label.grid(column=2, row=i, padx=10, sticky="w")
            self.codec_label_list.append(label)

            button = tk.Button(self, text="",
                command=lambda name=i-1: self.arm_button_click(name))
            button.grid(column=3, row=i, padx=10)
            self.arm_button_list.append(button)

    def arm_button_click(self, button_id):
        DeviceList[button_id].arm_device()
        self.arm_button_status()

    #Method looks for the arm status at each object in the device list
    #and appropriatly sets the arm button to match
    #Dirty: when one button is clicked it still checks all objects
    def arm_button_status(self):
        for device in DeviceList:
            #Dirty fix for id not matching list pointer
            i = device.device_id-1
            button = self.arm_button_list[i]
            if device.arm_status == True:
                button.config(text="Armed", image=self.imgRed)
            else:
                button.config(text="Disarmed", image=self.imgBlack)

    def btnArmAll_click(self):
        for device in DeviceList:
            device.arm_status = True
            self.arm_button_status()

    def btnDisarmAll_click(self):
        for device in DeviceList:
            device.arm_status = False
            self.arm_button_status()

    def btnRecord_click(self):
        Device.Record()

    def btnStop_click(self):
        Device.Stop()

    def updateCodecLabels(self):
        for device in DeviceList:
            device.print_device_codec()
            i = device.device_id-1
            label = self.codec_label_list[i]
            label.config(text=device.device_codec)

    #Threading code
    def live_status(self):
        while True:
            for device in DeviceList:
                i = device.device_id -1
                if device.check_device_status == device.device_status:
                    pass
                else:
                    device.update_device_status()
                    label = self.status_label_list[i]
                    label.config(text=device.device_status)
                    if label['text'] == "Idle":
                        label.config(fg="#039b05")
                    if label['text'] == "Recording":
                        label.config(fg="#bf0000")
                    else:
                        pass
            self.updateCodecLabels()
            time.sleep(1)

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

            current_codec = device.print_device_codec()
            codecmenu = tk.Menubutton(self, text=current_codec, relief="solid", font=font_codecselect)
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

        lblTitle = tk.Label(self, text="AJA KiPro Remote Control", font=font_title)
        lblTitle.grid(sticky="w")

        lblVersion = tk.Label(self, text="Version: 1.0a")
        lblVersion.grid(sticky="w")

        lblBuildDate = tk.Label(self, text="Built: 30 July 2017")
        lblBuildDate.grid(sticky="w")

        lblAuthor = tk.Label(self, text="Created by: Chris Farrants")
        lblAuthor.grid(sticky="w")

        lblCreatedfor = tk.Label(self, text="Created for: Coldplay Tour 2017")
        lblCreatedfor.grid(sticky="w")

        #Overview button
        btnOverview = tk.Button(self, text="Overview", font=font_guibuttons,
            command=lambda: controller.show_page(Overview))
        btnOverview.grid(column=0, padx=15, sticky="nw")

        #Settings button
        btnSettings = tk.Button(self, text="Settings", font=font_guibuttons, 
            command=lambda: controller.show_page(Settings))
        btnSettings.grid(column=1, padx=15, sticky="nw")



#Run the application
app = KiProControl()
app.mainloop()