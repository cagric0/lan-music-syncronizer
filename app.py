import socket
import json
import threading
import select
import os
import tkinter as tk
import tkinter.ttk as ttk
from PIL import Image, ImageTk
import pygame
from mutagen.mp3 import MP3

COLORS = ["#edffec", "#61e786", "#5a5766", "#48435c", "#9792e3"]
LARGEFONT = ("Helvetica", 32)
MEDIUMFONT = ("Helvetica", 16)
SMALLFONT = ("Helvetica", 12)
MUSIC_LIBRARY_PATH = "music/"




messageType = {
    "discover_rooms": "DISCOVER_ROOMS",
    "respond_rooms": "RESPOND_ROOMS",  # TCP
    "create_room": "CREATE_ROOM",
    "enter_room": "ENTER_ROOM",
    "respond_entering_room": "RESPOND_ENTERING_ROOM",  # TCP
    "exit_room": "EXIT_ROOM",  # TCP
    "exit_room_host": "EXIT_ROOM_HOST",
    "song_file_info": "SONG_FILE_INFO",  # TCP
    "song_file_request": "SONG_FILE_REQUEST"  # TCP
}
SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096  # send 4096 bytes each time step
file_port = 5001
port = 12345
bufferSize = 1024
IPAddr = ""  # 192.168.1.166
localIPAddr = ""  # 192.168.1

selected_room_ip = ""
created_room_ip = ""
name = ""

ip_room_dict = {}  # ip_room_dict[IP] = [room_name, host_name]
ip_name_dict_in_room = {}  # ip_name_dict_in_room[IP] = user_name


current_song = {"name": "", "size": "", "time": "", "status": ""}  # playing - paused

page2_global = None
page2_global_controller = None

def get_ip():
    global IPAddr, localIPAddr
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        IPAddr = s.getsockname()[0]
        parts = IPAddr.split(".")
        localIPAddr = parts[0] + "." + parts[1] + "." + parts[2] + "."
    finally:
        s.close()


def showActiveRooms():
    if (len(ip_room_dict) == 0):
        print("There is no active room")
    else:
        print("Active Rooms:")
        for key, value in ip_room_dict.items():
            print(value)


# UDP Functions
def thread_broadcast(message):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind(("", 0))
        print("Send UDP:", message)
        sock.sendto(message.encode(), ("<broadcast>", port))


def sendUDP(udpMessage):
    for i in range(3):
        dis = threading.Thread(target=thread_broadcast, args=(udpMessage,))
        dis.start()


def createUDPMessage(message_type):
    message = {
        "TYPE": message_type,
    }
    if message_type == messageType["discover_rooms"]:
        message["USER_IP"] = IPAddr
    elif message_type == messageType["create_room"]:
        # UI dan room create edince ip-name dictionarye
        # eklenmeli selected room id ye atanmalı DONE
        message["ROOM_IP"] = created_room_ip  # aynı zamanda host ip
        message["ROOM_NAME"] = ip_room_dict[created_room_ip][0]
        message["HOST_NAME"] = ip_room_dict[created_room_ip][1]
    elif message_type == messageType["exit_room_host"]:
        # clear all data about the room current_song, ip_name_dict_in_room, selected_room_ip, created_room_ip
        message["ROOM_IP"] = created_room_ip
        message["ROOM_NAME"] = ip_room_dict[created_room_ip][0]
        message["HOST_NAME"] = ip_room_dict[created_room_ip][1]
    elif message_type == messageType["enter_room"]:
        # UI dan room seçince dictionary üzerinden
        # id si bulunup selected room id ye atanmalı
        message["ROOM_IP"] = selected_room_ip
        message["USER_NAME"] = name
        message["USER_IP"] = IPAddr
    else:
        print("Wrong message type: " + message_type)
        return

    return json.dumps(message)


# TCP Functions
def thread_unicast(IP, message):
    print(message)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect((IP, port))
            print("Send TCP:", message)
            s.sendall(message.encode())
    except:
        print(str(IP) + " is unexpectedly offline.")
        # ip_name_dict.pop(IP, None)


def createTCPMessage(message_type):
    message = {
        "TYPE": message_type,
    }
    if message_type == messageType["respond_rooms"]:
        # Oda create edildiğinde ismi ile hostun ip si
        # ip_room_dicte eklenmeli
        message["ROOM_IP"] = created_room_ip  # aynı zamanda host ip
        message["ROOM_NAME"] = ip_room_dict[created_room_ip][0]
        message["HOST_NAME"] = ip_room_dict[created_room_ip][1]
    elif message_type == messageType["respond_entering_room"]:
        # message["ROOM_IP"] = selected_room_ip # aynı zamanda host ip
        message["USER_NAME"] = name
        message["USER_IP"] = IPAddr
    elif message_type == messageType["exit_room"]:
        # clear all data about the room current_song, ip_name_dict_in_room, selected_room_ip
        message["ROOM_IP"] = selected_room_ip
        message["USER_NAME"] = name
        message["USER_IP"] = IPAddr
    elif message_type == messageType["song_file_info"]:
        message["ROOM_IP"] = created_room_ip
        message["SONG_FILE_NAME"] = current_song["name"]
        message["SONG_FILE_SIZE"] = current_song["size"]
        message["SONG_CURRENT_TIME"] = current_song["time"]
        message["SONG_STATUS"] = current_song["status"]
    elif message_type == messageType["song_file_request"]:
        message["USER_IP"] = IPAddr
        message["SONG_FILE_NAME"] = current_song["name"]
    else:
        print("Wrong message type: " + message_type)
        return

    return json.dumps(message)


def sendTCP(IP, tcpMessage):
    dis = threading.Thread(target=thread_unicast, args=(IP, tcpMessage), daemon=True)
    dis.start()


# Listen UDP functions

def listenUDP():
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("", port))
            s.setblocking(0)
            result = select.select([s], [], [])
            msg = result[0][0].recv(bufferSize)
            output = msg.decode()
            received_packet = json.loads(output)

        print("Received UDP:", received_packet)

        handle_UDP_incoming(received_packet)


def handle_UDP_incoming(received_packet):
    if "TYPE" not in received_packet:
        return

    received_packet_type = received_packet["TYPE"]

    if received_packet_type == messageType["discover_rooms"]:
        handle_discover_rooms(received_packet)
    elif received_packet_type == messageType["create_room"]:
        handle_create_room(received_packet)
    elif received_packet_type == messageType["exit_room_host"]:
        handle_exit_room_host(received_packet)
    elif received_packet_type == messageType["enter_room"]:
        handle_enter_room(received_packet)
    else:
        # pass
        print("UDP unknown type received: ", received_packet_type)


def handle_discover_rooms(received_packet):
    # TODO
    if created_room_ip.strip():
        user_ip = received_packet["USER_IP"]
        respond_message = createTCPMessage(messageType["respond_rooms"])
        sendTCP(user_ip, respond_message)


def handle_create_room(received_packet):
    global ip_room_dict
    room_ip = received_packet["ROOM_IP"]
    room_name = received_packet["ROOM_NAME"]
    host_name = received_packet["HOST_NAME"]
    ip_room_dict[room_ip] = [room_name, host_name]
    # update room list UI DONE
    update_room_ui()

def handle_exit_room_host(received_packet):
    global ip_room_dict, ip_name_dict_in_room, selected_room_ip, current_song, created_room_ip
    room_ip = received_packet["ROOM_IP"]
    room_name = received_packet["ROOM_NAME"]
    host_name = received_packet["HOST_NAME"]
    if room_ip in ip_room_dict:
        del ip_room_dict[room_ip]
    if selected_room_ip == room_ip:
        ip_name_dict_in_room.clear()
        selected_room_ip = ""
        created_room_ip = ""
        current_song = {"name": "", "size": "", "time": "", "status": ""}
        ## o odadaki tüm kullanıcılar ana menüye yönlendirilir
        global page2_global, page2_global_controller
        # TODO test
        page2_global.slider.config(value=0)
        pygame.mixer.music.stop()
        page2_global_controller.show_frame(Page1)


def handle_enter_room(received_packet):
    global ip_name_dict_in_room
    room_ip = received_packet["ROOM_IP"]
    new_user_name = received_packet["USER_NAME"]
    new_user_ip = received_packet["USER_IP"]
    if selected_room_ip.strip():
        if selected_room_ip == room_ip:
            if new_user_ip in ip_name_dict_in_room and ip_name_dict_in_room[new_user_ip] == new_user_name:
                return
            ip_name_dict_in_room[new_user_ip] = new_user_name
            update_userlist_ui()
            respond_message = createTCPMessage(messageType["respond_entering_room"])
            sendTCP(new_user_ip, respond_message)
            if created_room_ip.strip():
                # sends song info to user that enter the room
                respond_message = createTCPMessage(messageType["song_file_info"])
                sendTCP(new_user_ip, respond_message)


def handle_exit_room(received_packet):
    global ip_name_dict_in_room
    room_ip = received_packet["ROOM_IP"]
    user_name = received_packet["USER_NAME"]
    user_ip = received_packet["USER_IP"]
    if selected_room_ip.strip():
        if selected_room_ip == room_ip:
            if user_ip in ip_name_dict_in_room:
                del ip_name_dict_in_room[user_ip]
                update_userlist_ui()


# Listen TCP functions
def listenTCP():
    while (True):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((IPAddr, port))
            s.listen()
            conn, addr = s.accept()
            with conn:
                output = ""
                while (True):
                    data = conn.recv(1024)
                    if not data:
                        break
                    output += data.decode()
        if (output == "" or output is None):
            print("There is a problem about your socket you should restart your cmd or computer")
            break
        received_packet = json.loads(output)
        print("Received TCP:", received_packet)
        handle_TCP_incoming(received_packet)


def handle_TCP_incoming(received_packet):
    if "TYPE" not in received_packet:
        return

    received_packet_type = received_packet["TYPE"]

    if received_packet_type == messageType["respond_rooms"]:
        handle_respond_rooms(received_packet)
    elif received_packet_type == messageType["respond_entering_room"]:
        handle_respond_entering_room(received_packet)
    elif received_packet_type == messageType["song_file_info"]:
        handle_song_file_info(received_packet)
    elif received_packet_type == messageType["song_file_request"]:
        handle_song_file_request(received_packet)
    elif received_packet_type == messageType["exit_room"]:
        handle_exit_room(received_packet)
    else:
        # pass
        print("UDP unknown type received: ", received_packet_type)


def handle_respond_rooms(received_packet):
    global ip_room_dict
    room_ip = received_packet["ROOM_IP"]
    room_name = received_packet["ROOM_NAME"]
    host_name = received_packet["HOST_NAME"]
    ip_room_dict[room_ip] = [room_name, host_name]

def handle_respond_entering_room(received_packet):
    global ip_name_dict_in_room
    user_name = received_packet["USER_NAME"]
    user_ip = received_packet["USER_IP"]
    ip_name_dict_in_room[user_ip] = user_name
    update_userlist_ui()


def handle_song_file_info(received_packet):
    global current_song, page2_global, current_song_length
    room_ip = received_packet["ROOM_IP"]
    if not received_packet["SONG_FILE_NAME"].strip():
        current_song = {"name": "", "size": "", "time": "", "status": ""}

        return
    if selected_room_ip == room_ip:
        song_status = received_packet["SONG_STATUS"]
        current_song["name"] = received_packet["SONG_FILE_NAME"]
        current_song["size"] = received_packet["SONG_FILE_SIZE"]
        current_song["time"] = received_packet["SONG_CURRENT_TIME"]
        current_song["status"] = received_packet["SONG_STATUS"]
        filepath = MUSIC_LIBRARY_PATH + current_song["name"]
        if os.path.exists(filepath):
            if song_status == "stopped":
                pygame.mixer.music.stop()

                page2_global.slider.config(value='0')
                # stop song
            elif song_status == "paused":
                page2_global.slider.config(value=current_song['time'])
                pygame.mixer.music.pause()
                # paused song
            elif song_status == "playing":
                mut = MP3(filepath)
                current_song_length = mut.info.length
                page2_global.slider.config(to=current_song_length, value=current_song['time'])
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.play(0, page2_global.slider.get())
                page2_global.update_slider()
                # play song
        else:
            # send TCP to get song file
            respond_message = createTCPMessage(messageType["song_file_request"])
            sendTCP(room_ip, respond_message)


def handle_song_file_request(received_packet):
    user_ip = received_packet["USER_IP"]
    requested_file_name = received_packet["SONG_FILE_NAME"]
    if current_song["name"] == requested_file_name:
        # Start to send file
        send_song_file(user_ip, requested_file_name)
    else:
        # send new song info
        # sends song info to user that enter the room
        respond_message = createTCPMessage(messageType["song_file_info"])
        sendTCP(user_ip, respond_message)


def send_song_file(IP, filename):
    # create the client socket
    s = socket.socket()
    print(f"[+] Connecting to {IP}:{file_port}")
    s.connect((IP, file_port))
    print("[+] Connected.")

    file_path = MUSIC_LIBRARY_PATH + filename
    filesize = os.path.getsize(file_path)
    # send the filename and filesize
    s.send(f"{filename}{SEPARATOR}{filesize}".encode())

    # start sending the file
    # progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(file_path, "rb") as f:
        while True:
            # read the bytes from the file
            bytes_read = f.read(BUFFER_SIZE)
            if not bytes_read:
                # file transmitting is done
                break
            # we use sendall to assure transimission in
            # busy networks
            s.sendall(bytes_read)
            # update the progress bar
            # progress.update(len(bytes_read))
    # close the socket
    s.close()
    # TO DO
    respond_message = createTCPMessage(messageType["song_file_info"])
    sendTCP(IP, respond_message)


# Receive File Function

def receive_song_file():
    while True:
        # TCP socket
        s = socket.socket()
        # bind the socket to our local address
        s.bind((IPAddr, file_port))
        # enabling our server to accept connections
        # 5 here is the number of unaccepted connections that
        # the system will allow before refusing new connections
        s.listen()
        print(f"[*] Listening as {IPAddr}:{file_port}")

        # accept connection if there is any
        client_socket, address = s.accept()
        # if below code is executed, that means the sender is connected
        print(f"[+] {address} is connected.")

        if address != selected_room_ip:
            # close the client socket
            client_socket.close()
            # close the server socket
            s.close()
        else:
            # receive the file infos
            # receive using client socket, not server socket
            received = client_socket.recv(BUFFER_SIZE).decode()
            filename, filesize = received.split(SEPARATOR)

            file_path = MUSIC_LIBRARY_PATH + filename
            # convert to integer
            filesize = int(filesize)

            # start receiving the file from the socket
            # and writing to the file stream
            # progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
            with open(file_path, "wb") as f:
                while True:
                    # read 1024 bytes from the socket (receive)
                    bytes_read = client_socket.recv(BUFFER_SIZE)
                    if not bytes_read:
                        # nothing is received
                        # file transmitting is done
                        break
                    # write to the file the bytes we just received
                    f.write(bytes_read)
                    # update the progress bar
                    # progress.update(len(bytes_read))

            # close the client socket
            client_socket.close()
            # close the server socket
            s.close()

def sendTCP_users_in_room(message_type):
    global ip_name_dict_in_room
    for ip in ip_name_dict_in_room.keys():
        respond_message = createTCPMessage(message_type)
        sendTCP(ip, respond_message)

def update_room_ui():
    global ip_room_dict, rooms_var, rooms
    rooms = [(k, v[0], v[1]) for k, v in ip_room_dict.items()]
    room_names = [r[1]+" hosted by "+r[2] for r in rooms]
    rooms_var.set(room_names)

def update_userlist_ui():
    global ip_name_dict_in_room, users_in_room, users_in_room_var
    users_in_room = [(k, v) for k, v in ip_name_dict_in_room.items()]
    users_in_room_names = [u[1] for u in users_in_room]
    users_in_room_var.set(users_in_room_names)


class TkinterApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry('700x600+350+100')
        self.resizable(False, False)
        self.title('LAN Music Synchronizer')
        icon = tk.PhotoImage(file='res/logo.png')
        self.iconphoto(False, icon)

        global username, ip_room_dict, rooms, rooms_var, current_room, current_room_var
        username = tk.StringVar()
        rooms = [(k, v[0], v[1]) for k, v in ip_room_dict.items()]
        room_names = [r[1]+" hosted by "+r[2] for r in rooms]
        rooms_var = tk.StringVar(value=room_names)
        current_room = None
        current_room_var = tk.StringVar()

        global ip_name_dict_in_room, users_in_room, users_in_room_var

        users_in_room = [(k, v) for k, v in ip_name_dict_in_room.items()]
        users_in_room_names = [u[1] for u in users_in_room]
        users_in_room_var = tk.StringVar(value=users_in_room_names)

        global music_names, music_names_var, current_song_name_var, current_song_length
        music_names = os.listdir("music/")
        music_names_var = tk.StringVar(value=music_names)
        current_song_name_var = tk.StringVar()
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
            global username, name
            update_userlist_ui()
            name = val
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
        global rooms, current_room_var, selected_room_ip
        val = self.listbox.curselection()
        if not val:
            return
        val = val[0]
        selected_room_ip = rooms[val][0]
        udp_message = createUDPMessage(messageType["enter_room"])
        sendUDP(udp_message)
        print("JOINED to room:", rooms[val][1])
        current_room_var.set(rooms[val][1])
        if song_listbox_frame:
            song_listbox_frame.pack_forget()
        controller.show_frame(Page2)

    def refresh_rooms(self):
        update_room_ui()

    def host_room(self, controller):
        global current_room, currrent_room_var, created_room_ip, IPAddr, ip_room_dict, name, selected_room_ip

        val = self.host_name_entry.get()
        if not val:
            return

        created_room_ip = IPAddr
        selected_room_ip = created_room_ip
        # add new room info to dict
        ip_room_dict[created_room_ip] = [val, name]
        # send message to all user to update their room list ui
        udp_message = createUDPMessage(messageType["create_room"])
        sendUDP(udp_message)

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
        global page2_global, page2_global_controller
        page2_global = self
        page2_global_controller = controller

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
        lbl = tk.Label(song_listbox_frame, text="Music files in your library", font=MEDIUMFONT, bg=COLORS[3],
                       fg='white')
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
            self.slider.after(10, self.update_slider)
        else:
            if not pygame.mixer.music.get_busy():
                return
            pos = self.slider.get()
            self.slider.config(value=pos + 0.01)
            self.slider.after(10, self.update_slider)

    def mute(self):
        if pygame.mixer.music.get_volume():
            pygame.mixer.music.set_volume(0)
        else:
            pygame.mixer.music.set_volume(1)

    def play(self):
        global created_room_ip
        if not created_room_ip.strip():
            return
        global music_names, music_names_var, current_song, current_song_length, current_song_name_var
        chosen_song = music_names[self.songlistbox.curselection()[0]] if self.songlistbox.curselection() else None

        if not chosen_song:
            return
        if current_song["name"] != chosen_song:
            current_song["name"] = chosen_song
            file_path = MUSIC_LIBRARY_PATH + chosen_song
            filesize = os.path.getsize(file_path)
            current_song["size"] = str(filesize)
            current_song["status"] = "playing"
            current_song["time"] = "0"
            current_song_name_var.set(chosen_song)
            mut = MP3(file_path)
            current_song_length = mut.info.length
            sendTCP_users_in_room(messageType["song_file_info"])
            self.slider.config(to=current_song_length, value=0)
            # print(current_song, current_song_length)
            pygame.mixer.music.load(MUSIC_LIBRARY_PATH + chosen_song)
            pygame.mixer.music.play(0, self.slider.get())
            self.update_slider()
        else:
            if pygame.mixer.music.get_busy():
                return
            else:
                current_song["time"] = self.slider.get()
                current_song["status"] = "playing"
                sendTCP_users_in_room(messageType["song_file_info"])
                pygame.mixer.music.play(0, self.slider.get())
                self.update_slider()

    def pause(self):
        global created_room_ip, current_song
        if not created_room_ip.strip():
            return
        pygame.mixer.music.pause()
        current_song["time"] = self.slider.get()
        current_song["status"] = "paused"
        sendTCP_users_in_room(messageType["song_file_info"])

    def stop(self):
        global created_room_ip, current_song
        if not created_room_ip.strip():
            return
        pygame.mixer.music.stop()
        self.slider.config(value=0)
        current_song["status"] = "stopped"
        current_song["time"] = "0"
        sendTCP_users_in_room(messageType["song_file_info"])


    def reset(self):
        global created_room_ip, current_song_length, current_song
        if not created_room_ip.strip():
            return

        if self.slider.get() == current_song_length:
            current_song["status"] = "stopped"
            current_song["time"] = "0"
        else:
            current_song["status"] = "playing"
            current_song["time"] = "0"
        sendTCP_users_in_room(messageType["song_file_info"])
        pygame.mixer.music.rewind()
        self.slider.config(value=0)

    def slider_release(self, event):
        global created_room_ip
        if not created_room_ip.strip():
            return
        if pygame.mixer.music.get_busy():
            pos = self.slider.get()
            current_song["status"] = "playing"
            current_song["time"] = pos
            sendTCP_users_in_room(messageType["song_file_info"])
            pygame.mixer.music.set_pos(pos)

        self.slider_hold = False

    def slider_click(self, event):
        global created_room_ip
        if not created_room_ip.strip():
            return
        self.slider_hold = True

    def exit(self, controller):
        global current_song, created_room_ip, selected_room_ip, ip_name_dict_in_room
        current_song = {"name": "", "size": "", "time": "", "status": ""}
        if created_room_ip.strip():
            udp_message = createUDPMessage(messageType["exit_room_host"])
            sendUDP(udp_message)
            if created_room_ip in ip_room_dict:
                del ip_room_dict[created_room_ip]
        else:
            for ip in ip_name_dict_in_room.keys():
                respond_message = createTCPMessage(messageType["exit_room"])
                sendTCP(ip, respond_message)

        selected_room_ip = ""
        created_room_ip = ""
        ip_name_dict_in_room.clear()
        self.slider.config(value=0)
        pygame.mixer.music.stop()
        controller.show_frame(Page1)
        update_room_ui()

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


get_ip()

# receive_song_file()
listenFile = threading.Thread(target=receive_song_file, args=(), daemon=True)
listenFile.start()

listenUdp = threading.Thread(target=listenUDP, args=(), daemon=True)
listenUdp.start()

listenTcp = threading.Thread(target=listenTCP, args=(), daemon=True)
listenTcp.start()

udp_discover_message = createUDPMessage(messageType["discover_rooms"])
sendUDP(udp_discover_message)

# Send File Function
if not os.path.exists('music'):
    os.makedirs('music')

pygame.mixer.init()
app = TkinterApp()
app.mainloop()
