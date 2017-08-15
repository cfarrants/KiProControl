import Tkinter as tk #Main Tkinter GUI interface
import ttk #Extra Tkinter styling options
from tkFont import Font

font_unitid = ('Helvetica', 26, 'bold')
font_status = ('Helvetica', 18)
font_recbutton = ('Helvetica', 16, 'bold')

num_units = 6
selectall = 1

class KiProControl(tk.Tk):

    def __init__ (self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title("AJA KiPro Control")
        self.geometry('800x480') #Force window size for RaspberryPi touchscreen

        container = tk.Frame(self) #Main holder for the entire application

        container.pack(side="top", fill="both", expand = True) #Place the main holder

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {} #Page dictionary

        PageList = (Overview, settings)

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

        #Generate KiPro unit labels
        for i in range(num_units):
            label = tk.Label(self, text=i+1, font=font_unitid)
            label.grid(column=0, row=i)

        #Generate device status labels
        for i in range(num_units):
            label = tk.Label(self, text="STANDBY", font=font_status)
            label.grid(column=1, row=i, padx=20)

        #Generate device codec labels
        for i in range(num_units):
            label = tk.Label(self, text="ProRes 422", font=font_status)
            label.grid(column=2, row=i, padx=20)

        #Generate Arm/Disarm buttons
        self.arm_buttons = [] # iist of buttons
        for i in range(num_units):
            button = tk.Button(self, text="ARM", height=2, width=10, highlightbackground="black", bg="black",
                command=lambda name=i: self.btnArm_click(name))
            button.grid(column=3, row=i, padx=10, pady=5)
            self.arm_buttons.append(button)

        #Record button
        btnRecord = ttk.Button(self, text="RECORD",
            command=lambda: self.btnRecord_click())
        btnRecord.grid(column=3, row=num_units+1, pady=20)

        #Select/deselect all
        btnAll = tk.Button(self, text="Select All")
        btnAll.grid(column=2, row=num_units+1)

        #Settings button
        btnSettings = ttk.Button(self, text="Settings",
            command=lambda: controller.show_page(settings))
        btnSettings.grid(column=0, row=num_units+1)

    def btnArm_click(self, name):
        clicked = self.arm_buttons[name]

        if clicked['highlightbackground'] == "black":
            clicked.config(highlightbackground="red", bg="red")
        else:
            clicked.config(highlightbackground="black", bg="black")

    def btnRecord_click(self):
        i=1
        for button in self.arm_buttons:
            if button['highlightbackground'] == 'red':
                print(i)
                i=i+1
            else:
                print("hello")


class settings(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Settings")
        label.pack(pady=10, padx=10)

        btnOverview = ttk.Button(self, text="Overview",
            command=lambda: controller.show_page(Overview))
        btnOverview.pack()


app = KiProControl()
app.mainloop()
