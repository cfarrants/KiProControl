import Tkinter as tk #Main Tkinter GUI interface
from aja.embedded.rest.kipro import Client

font_unitid = ('Helvetica', 26, 'bold')
font_status = ('Helvetica', 18)
font_recbutton = ('Helvetica', 18, 'bold')

num_units = 6
client_list = [] #List of client objects
iplist = [] #List of unit ip addresses


class KiProControl(tk.Tk):

    def __init__ (self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.LoadIPAddresses()
        #self.Connections()

        #Setup window
        self.title("AJA KiPro")
        self.geometry('800x480') #Force window size for RaspberryPi touchscreen

        container = tk.Frame(self) #Main holder for the entire application
        container.pack(side="top", fill="both", expand = True) #Place the main holder
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {} #Page dictionary

        PageList = (Overview, Settings) #Simple way for adding pages to the application

        for P in (PageList):
            page = P(container, self)
            self.frames[P] = page
            page.grid(row=0, column=0, sticky="NESW")

        self.show_page(Overview) #Default startup page

    def show_page(self, cont):
        page = self.frames[cont]
        page.tkraise()

    def LoadIPAddresses(self):
        #Dirty: Load list of clients from ip address text file
        with open('ipaddress.txt', "r") as f:
            for line in f:
                iplist.append(line.strip())
            f.close()

    def Connections(self):
        for item in iplist:
            print('Connecting to: ')
            print(item)
            newclient = Client(item)
            client_list.append(newclient)
        print(client_list)


class Overview(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        #Generate KiPro unit labels
        for i in range(num_units):
            label = tk.Label(self, text=i+1, font=font_unitid)
            label.grid(column=0, row=i)

        #Generate device status labels
        self.unit_status = []
        for i in range(num_units):
            label = tk.Label(self, text="STANDBY", font=font_status, fg="green")
            label.grid(column=1, row=i, padx=20)
            self.unit_status.append(label)

        #Generate device codec labels
        self.unit_codec = []
        for i in range(num_units):
            label = tk.Label(self, text="ProRes 422", font=font_status)
            label.grid(column=2, row=i, padx=20)
            self.unit_codec.append(label)

        #Generate Arm/Disarm buttons
        self.imgRed = tk.PhotoImage(file="red.gif")
        self.imgBlack = tk.PhotoImage(file="black.gif")
        self.arm_buttons = [] #List of buttons
        for i in range(num_units):
            button = tk.Button(self, height=50, width=50, image=self.imgBlack, bg="black",
                command=lambda name=i: self.btnArm_click(name))
            button.grid(column=3, row=i, padx=10, pady=5)
            self.arm_buttons.append(button)

        #Record button
        self.imgRecord = tk.PhotoImage(file="record.gif")
        btnRecord = tk.Button(self, image=self.imgRecord, font=font_recbutton, padx=30, pady=100,
            command=lambda: self.btnRecord_click())
        btnRecord.grid(column=4, row=0, rowspan=2, columnspan=2, padx=20)

        #Stop button
        self.imgStop = tk.PhotoImage(file="stop.gif")
        btnStop = tk.Button(self, image=self.imgStop)
        btnStop.grid(column=4, row=2, rowspan=2, columnspan=2)

        #Select all button
        btnAll = tk.Button(self, text="Select All",
            command= lambda: self.btnSelectAll())
        btnAll.grid(column=4, row=4, pady=30)

        #Select none button
        btnNone = tk.Button(self, text="Select None",
            command= lambda: self.btnSelectNone())
        btnNone.grid(column=5, row=4, pady=30)

        #Settings button
        btnSettings = tk.Button(self, text="Settings",
            command=lambda: controller.show_page(Settings))
        btnSettings.grid(column=0, row=num_units+1)

    def btnArm_click(self, name):
        clicked = self.arm_buttons[name]

        if clicked['bg'] == "black":
            clicked.config(image=self.imgRed, bg="red")
        else:
            clicked.config(image=self.imgBlack, bg="black")

    def btnRecord_click(self):
        for client in client_list:
            client.record()

    def btnSelectAll(self):
        for i in self.arm_buttons:
            i.config(image=self.imgRed, bg="red")

    def btnSelectNone(self):
        for i in self.arm_buttons:
            i.config(image=self.imgBlack, bg="black")


class Settings(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Settings")

        #Generate KiPro unit labels
        for i in range(num_units):
            label = tk.Label(self, text=i+1, font=font_unitid)
            label.grid(column=0, row=i)

        #Run the method to load current IP addresses from the text file
        #self.populateIP()

        #Generate ip address fields
        self.ip_input = [] #List of ip address input boxes
        self.ip_buttons = [] #List of SetIP buttons
        for i in range(num_units):
            #ip Address Fields
            e = tk.Entry(self, width=15, font=font_status)
            e.insert(0, iplist[i]) #Pull ip address from the list
            e.grid(column=1, row=i)
            self.ip_input.append(e)
            #Set buttons
            button = tk.Button(self, text="Set",
                command=lambda name=i: self.setIP(name, "Test"))
            button.grid(column=2, row=i)
            self.ip_buttons.append(button)


        btnOverview = tk.Button(self, text="Overview",
            command=lambda: controller.show_page(Overview))
        btnOverview.grid(column=0, row=num_units+1)

    def setIP(self, index, data):
        update = self.ip_input[index] #Create a variable containing the input box object to read from
        text = update.get() #Load the text from that input box into a variable
        iplist[index] = text #Update that IP address in the IP list

        #Write the IP addresses back to the file
        f = open('ipaddress.txt', "w")
        for item in iplist:
            f.write("%s\n" % item)
        f.close()


app = KiProControl()
app.mainloop()
