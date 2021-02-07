import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image, ImageTk
import os
import time
import pygame
from mutagen.mp3 import MP3
from globals import *


class TkinterApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry('700x600+350+100')
        self.resizable(False, False)
        self.title('LAN Music Synchronizer')
        icon = tk.PhotoImage(file='res/logo.png')
        self.iconphoto(False, icon)

        global username, rooms_dict, rooms, rooms_var, current_room, current_room_var
        username = tk.StringVar()
        rooms_dict = {str(i): (f"Room {i}", f"Host {i}") for i in range(1, 21)}
        rooms = [(k, v[0], v[1]) for k, v in rooms_dict.items()]
        room_names = [r[1] for r in rooms]
        rooms_var = tk.StringVar(value=room_names)
        current_room = None
        current_room_var = tk.StringVar()

        global users_in_room_dict, users_in_room, users_in_room_var
        users_in_room_dict = {i: f"User {i}" for i in range(1, 11)}
        users_in_room = [(k, v) for k, v in users_in_room_dict.items()]
        users_in_room_names = [u[1] for u in users_in_room]
        users_in_room_var = tk.StringVar(value=users_in_room_names)

        global music_names, music_names_var, current_song, current_song_length
        music_names = os.listdir("music/")
        music_names_var = tk.StringVar(value=music_names)
        current_song = tk.StringVar()
        current_song_length = None

        global is_playing
        is_playing = False

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
                         font=MEDIUMFONT, bg=COLORS[3], fg='white')
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
        self.listbox = None
        self.get_welcome_frame()
        self.get_listbox_frame()
        self.get_buttons(controller)
        self.get_host_frame(controller)

    def join_selected_room(self, controller):
        val = self.listbox.curselection()
        if not val:
            return
        val = val[0]
        print("JOINED to room:", rooms[val][1])
        current_room_var.set(rooms[val][1])
        if song_listbox_frame:
            song_listbox_frame.pack_forget()
        controller.show_frame(Page2)

    def refresh_rooms(self):
        # todo implement
        global rooms, rooms_var, current_room, currrent_room_var
        room_names = [r[1] for r in rooms]
        rooms_var.set(room_names)

    def host_room(self, controller):
        global rooms, rooms_var, current_room, currrent_room_var, created_room_ip, ourIP
        val = self.host_name_entry.get()
        if not val:
            return
        created_room_ip = ourIP
        current_room_var.set(val)
        song_listbox_frame.pack()
        controller.show_frame(Page2)

    def get_host_frame(self, controller):
        f = tk.Frame(self)
        f.configure(bg=COLORS[3])
        l = tk.Label(f, text='New Room Name', font=SMALLFONT, bg=COLORS[3], fg='white')
        l.grid(row=0, column=0, padx=5, pady=5)
        self.host_name_entry = tk.Entry(f, width=15)
        b = tk.Button(f, width=15, text="Create Room", command=lambda: self.host_room(controller))
        self.host_name_entry.grid(row=0, column=1, padx=5, pady=5)
        b.grid(row=0, column=2, padx=5, pady=5)
        f.pack()

    def get_buttons(self, controller):
        buttons_frame = tk.Frame(self)
        buttons_frame.configure(bg=COLORS[3])
        buttons = [
            tk.Button(buttons_frame, width=15, text="Join Room", command=lambda: self.join_selected_room(controller)),
            tk.Button(buttons_frame, width=15, text="Refresh", command=self.refresh_rooms),
            tk.Button(buttons_frame, width=15, text="Quit", command=lambda: controller.show_frame(StartPage))]
        for i, button in enumerate(buttons):
            button.grid(row=0, column=i, padx=25, pady=10)
        buttons_frame.pack()

    def get_listbox_frame(self):
        lbl = tk.Label(self, text="Available Rooms", font=MEDIUMFONT, bg=COLORS[3], fg='white')
        lbl.pack(padx=5, pady=5)
        listbox_frame = tk.Frame(self)
        listbox_frame.configure(bg=COLORS[3])
        global rooms_var, rooms
        self.listbox = tk.Listbox(listbox_frame, width=100, height=10, selectbackground=COLORS[1],
                                  selectforeground='black', activestyle="none", listvariable=rooms_var)
        self.listbox.pack(side=tk.LEFT)
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)
        listbox_frame.pack()

    def get_welcome_frame(self):
        welcome_frame = tk.Frame(self)
        global username
        label1 = tk.Label(welcome_frame, text='Welcome', font=MEDIUMFONT, bg=COLORS[3], fg='white')
        label1.grid(row=0, column=0)
        label2 = tk.Label(welcome_frame, textvariable=username, font=MEDIUMFONT, bg=COLORS[3], fg='white')
        label2.grid(row=0, column=1)
        welcome_frame.pack(pady=(30, 20))


class Page2(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.slider_hold = False
        self.configure(bg=COLORS[3])
        self.get_room_title_frame()
        self.get_listbox_frame()
        self.get_buttons(controller)
        self.get_songlistbox_frame()


    def get_room_title_frame(self):
        room_title_frame = tk.Frame(self)
        global current_room_var
        label1 = tk.Label(room_title_frame, text='Room: ', font=MEDIUMFONT, bg=COLORS[3], fg='white')
        label1.grid(row=0, column=0)
        label2 = tk.Label(room_title_frame, textvariable=current_room_var, font=MEDIUMFONT, bg=COLORS[3], fg='white')
        label2.grid(row=0, column=1)
        room_title_frame.pack(pady=10)

    def get_listbox_frame(self):
        global listbox_frame
        listbox_frame = tk.Frame(self)
        listbox_frame.configure(bg=COLORS[3])
        lbl = tk.Label(listbox_frame, text="Users in room", font=MEDIUMFONT, bg=COLORS[3], fg='white')
        lbl.pack(padx=5, pady=5)
        global users_in_room, users_in_room_var
        self.listbox = tk.Listbox(listbox_frame, width=100, height=5, state=tk.DISABLED,
                                  listvariable=users_in_room_var)
        self.listbox.pack(side=tk.LEFT)
        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)
        listbox_frame.pack()

    def get_songlistbox_frame(self):

        global song_listbox_frame
        song_listbox_frame = tk.Frame(self)
        song_listbox_frame.configure(bg=COLORS[3])
        lbl = tk.Label(song_listbox_frame, text="Music files in your library", font=MEDIUMFONT, bg=COLORS[3], fg='white')
        lbl.pack(padx=5, pady=5)
        global music_names, music_names_var
        self.songlistbox = tk.Listbox(song_listbox_frame, width=100, height=5, selectbackground=COLORS[1],
                                      selectforeground='black', activestyle="none", listvariable=music_names_var)
        self.songlistbox.pack(side=tk.LEFT)
        scrollbar = tk.Scrollbar(song_listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.songlistbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)
        song_listbox_frame.pack()

    def update_slider(self):
        if self.slider_hold:
            self.slider.after(1000, self.update_slider)
        else:
            if not pygame.mixer.music.get_busy():
                return
            pos = self.slider.get()
            self.slider.config(value=pos + 1)
            self.slider.after(1000, self.update_slider)

    def mute(self):
        if pygame.mixer.music.get_volume():
            pygame.mixer.music.set_volume(0)
        else:
            pygame.mixer.music.set_volume(1)

    def play(self):
        global created_room_ip
        if not created_room_ip.strip():
            return
        global music_names, music_names_var, current_song, current_song_length
        chosen_song = music_names[self.songlistbox.curselection()[0]] if self.songlistbox.curselection() else None
        if not chosen_song:
            return
        if current_song != chosen_song:
            current_song = chosen_song
            mut = MP3(MUSIC_LIBRARY_PATH + current_song)
            current_song_length = mut.info.length
            self.slider.config(to=current_song_length, value=0)
            # print(current_song, current_song_length)
            pygame.mixer.music.load(MUSIC_LIBRARY_PATH + current_song)
            pygame.mixer.music.play(0, self.slider.get())
            self.update_slider()
        else:
            if pygame.mixer.music.get_busy():
                return
            else:
                pygame.mixer.music.play(0, self.slider.get())
                self.update_slider()

    def pause(self):
        global created_room_ip
        if not created_room_ip.strip():
            return
        pygame.mixer.music.pause()

    def stop(self):
        global created_room_ip
        if not created_room_ip.strip():
            return
        pygame.mixer.music.stop()
        self.slider.config(value=0)
        global current_song
        current_song = None

    def reset(self):
        global created_room_ip
        if not created_room_ip.strip():
            return
        pygame.mixer.music.rewind()
        self.slider.config(value=0)

    def slider_release(self, event):
        global created_room_ip
        if not created_room_ip.strip():
            return
        if pygame.mixer.music.get_busy():
            pos = self.slider.get()
            pygame.mixer.music.set_pos(pos)

        self.slider_hold = False

    def slider_click(self, event):
        global created_room_ip
        if not created_room_ip.strip():
            return
        self.slider_hold = True

    def exit(self, controller):
        global current_song
        current_song = None
        self.slider.config(value=0)
        pygame.mixer.music.stop()
        controller.show_frame(Page1)

        global created_room_ip
        created_room_ip = ''

    def get_buttons(self, controller):
        global button_images
        button_images = [tk.PhotoImage(file="res/circled-pause.png"),
                         tk.PhotoImage(file="res/circled-play.png"),
                         tk.PhotoImage(file="res/recurring-appointment.png"),
                         tk.PhotoImage(file="res/mute.png"),
                         tk.PhotoImage(file="res/stop-circled.png")]

        buttons_frame = tk.Frame(self)
        buttons_frame.configure(bg=COLORS[3])
        s = ttk.Style()
        s.configure('Horizontal.TScale', background=COLORS[3])
        self.slider = ttk.Scale(buttons_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                value=0, length=650, style='Horizontal.TScale')
        self.slider.bind("<Button-1>", self.slider_click)
        self.slider.bind("<ButtonRelease-1>", self.slider_release)

        self.slider.grid(row=0, column=0, columnspan=6, padx=0, pady=10)
        buttons = [tk.Button(buttons_frame, text="Mute", command=self.mute,
                             image=button_images[3], bg=COLORS[3], borderwidth=0),
                   tk.Button(buttons_frame, text="Play", command=self.play,
                             image=button_images[1], bg=COLORS[3], borderwidth=0),
                   tk.Button(buttons_frame, text="Pause", command=self.pause,
                             image=button_images[0], bg=COLORS[3], borderwidth=0),
                   tk.Button(buttons_frame, text="Stop", command=self.stop,
                             image=button_images[4], bg=COLORS[3], borderwidth=0),
                   tk.Button(buttons_frame, text="Reset", command=self.reset,
                             image=button_images[2], bg=COLORS[3], borderwidth=0),
                   tk.Button(buttons_frame, width=15, text="Leave Room", command=lambda: self.exit(controller))]
        for i, button in enumerate(buttons):
            button.grid(row=1, column=i, padx=25, pady=10)
        buttons_frame.pack()


pygame.mixer.init()
app = TkinterApp()
app.mainloop()
