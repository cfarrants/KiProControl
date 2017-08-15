import Tkinter as tk #Main Tkinter GUI interface
from aja.embedded.rest.kipro import Client
import app.deviceslass import Device

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


class Settings(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Settings")



app = KiProControl()
app.mainloop()
