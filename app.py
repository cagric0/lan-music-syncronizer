import tkinter as tk
from PIL import Image, ImageTk

from globals import *


class TkinterApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry('700x400+350+200')
        self.resizable(False, False)
        self.title('LAN Music Synchronizer')
        icon = tk.PhotoImage(file='res/logo.png')
        self.iconphoto(False, icon)

        global username
        username = tk.StringVar()

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, Page1, Page2):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg=COLORS[3])
        global photo_image
        img = Image.open("res/logo.png").convert("RGBA")
        img_resized = img.resize((100, 100), Image.ANTIALIAS)
        photo_image = ImageTk.PhotoImage(img_resized)
        logo_label = tk.Label(self, image=photo_image, bg=COLORS[3])
        logo_label.pack(padx=50, pady=50)
        label = tk.Label(self, text='Please enter your name',
                         font=SMALLFONT, bg=COLORS[3], fg='white')
        self.username_input = tk.Entry(self, bg='white')
        label.pack(padx=5, pady=5)
        self.username_input.pack(padx=5, pady=5)
        self.login_button = tk.Button(self, text="Log In", command=lambda: self.onclick_login(controller))
        self.login_button.pack(padx=5, pady=5)
        self.master.master.bind('<Return>', lambda x: self.onclick_login(controller))

    def onclick_login(self, controller):
        val = str(self.username_input.get())
        val = val.strip()
        if val:
            global username
            username.set(val)
            print(f"[LOGIN] {username.get()}")
            self.master.master.unbind('<Return>')
            controller.show_frame(Page1)
        else:
            self.username_input.configure(highlightbackground="#ff4f64", highlightcolor="#ff4f64")


class Page1(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg=COLORS[3])
        global username
        label = tk.Label(self, text='welcome ', font=SMALLFONT, bg=COLORS[3], fg='white')
        label.grid(row=0, column=3, padx=0, pady=10)
        label = tk.Label(self, textvariable=username, font=SMALLFONT, bg=COLORS[3], fg='white')
        label.grid(row=0, column=4, padx=0, pady=10)

        button1 = tk.Button(self, text="Log Out",
                            command=lambda: controller.show_frame(StartPage))
        button1.grid(row=1, column=1, padx=10, pady=10)


class Page2(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.configure(bg=COLORS[3])
        label = tk.Label(self, text="Page 2", font=LARGEFONT)
        label.grid(row=0, column=4, padx=10, pady=10)

        button1 = tk.Button(self, text="Page 1",
                            command=lambda: controller.show_frame(Page1))

        button1.grid(row=1, column=1, padx=10, pady=10)

        button2 = tk.Button(self, text="Startpage",
                            command=lambda: controller.show_frame(StartPage))

        button2.grid(row=2, column=1, padx=10, pady=10)


app = TkinterApp()
app.mainloop()
