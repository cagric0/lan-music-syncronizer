#
#
# messageType = {
#     "discover_rooms": "DISCOVER_ROOMS",
#     "respond_rooms": "RESPOND_ROOMS",  # TCP
#     "create_room": "CREATE_ROOM",
#     "enter_room": "ENTER_ROOM",
#     "respond_entering_room": "RESPOND_ENTERING_ROOM",  # TCP
#     "exit_room": "EXIT_ROOM",  # TCP
#     "exit_room_host": "EXIT_ROOM_HOST",
#     "song_file_info": "SONG_FILE_INFO",  # TCP
#     "song_file_request": "SONG_FILE_REQUEST"  # TCP
# }
# SEPARATOR = "<SEPARATOR>"
# BUFFER_SIZE = 4096  # send 4096 bytes each time step
# file_port = 5001
# port = 12345
# bufferSize = 1024
# IPAddr = ""  # 192.168.1.166
# localIPAddr = ""  # 192.168.1
#
# selected_room_ip = ""
# created_room_ip = "192.168.1.131"
# name = "Halas"
# roomName = "Cagri"
# ip_room_dict = {"192.168.1.131": [roomName, name]}  # ip_room_dict[IP] = [room_name, host_name]
# ip_name_dict_in_room = {}  # ip_name_dict_in_room[IP] = user_name
#
# current_song = {"name": "", "size": "", "time": "", "status": ""}  # playing - paused
#
#
# def get_ip():
#     global IPAddr, localIPAddr
#     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     try:
#         s.connect(("8.8.8.8", 80))
#         IPAddr = s.getsockname()[0]
#         parts = IPAddr.split(".")
#         localIPAddr = parts[0] + "." + parts[1] + "." + parts[2] + "."
#     finally:
#         s.close()
#
#
# def showActiveRooms():
#     if (len(ip_room_dict) == 0):
#         print("There is no active room")
#     else:
#         print("Active Rooms:")
#         for key, value in ip_room_dict.items():
#             print(value)
#
#
# # UDP Functions
# def thread_broadcast(message):
#     with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
#         sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
#         sock.bind(("", 0))
#         print("Send UDP:", message)
#         sock.sendto(message.encode(), ("<broadcast>", port))
#
#
# def sendUDP(udpMessage):
#     for i in range(3):
#         dis = threading.Thread(target=thread_broadcast, args=(udpMessage,))
#         dis.start()
#
#
# def createUDPMessage(message_type):
#     message = {
#         "TYPE": message_type,
#     }
#     if message_type == messageType["discover_rooms"]:
#         message["USER_IP"] = IPAddr
#     elif message_type == messageType["create_room"]:
#         # UI dan room create edince ip-name dictionarye
#         # eklenmeli selected room id ye atanmalı
#         message["ROOM_IP"] = created_room_ip  # aynı zamanda host ip
#         message["ROOM_NAME"] = ip_room_dict[created_room_ip][0]
#         message["HOST_NAME"] = ip_room_dict[created_room_ip][1]
#     elif message_type == messageType["exit_room_host"]:
#         # clear all data about the room current_song, ip_name_dict_in_room, selected_room_ip, created_room_ip
#         message["ROOM_IP"] = created_room_ip
#         message["ROOM_NAME"] = ip_room_dict[created_room_ip][0]
#         message["HOST_NAME"] = ip_room_dict[created_room_ip][1]
#     elif message_type == messageType["enter_room"]:
#         # UI dan room seçince dictionary üzerinden
#         # id si bulunup selected room id ye atanmalı
#         message["ROOM_IP"] = selected_room_ip
#         message["USER_NAME"] = name
#         message["USER_IP"] = IPAddr
#     else:
#         print("Wrong message type: " + message_type)
#         return
#
#     return json.dumps(message)
#
#
# # TCP Functions
# def thread_unicast(IP, message):
#     print(message)
#     try:
#         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#             s.settimeout(1)
#             s.connect((IP, port))
#             print("Send TCP:", message)
#             s.sendall(message.encode())
#     except:
#         print(str(IP) + " is unexpectedly offline.")
#         # ip_name_dict.pop(IP, None)
#
#
# def createTCPMessage(message_type):
#     message = {
#         "TYPE": message_type,
#     }
#     if message_type == messageType["respond_rooms"]:
#         # Oda create edildiğinde ismi ile hostun ip si
#         # ip_room_dicte eklenmeli
#         message["ROOM_IP"] = created_room_ip  # aynı zamanda host ip
#         message["ROOM_NAME"] = ip_room_dict[created_room_ip][0]
#         message["HOST_NAME"] = ip_room_dict[created_room_ip][1]
#     elif message_type == messageType["respond_entering_room"]:
#         # message["ROOM_IP"] = selected_room_ip # aynı zamanda host ip
#         message["USER_NAME"] = name
#         message["USER_IP"] = IPAddr
#     elif message_type == messageType["exit_room"]:
#         # clear all data about the room current_song, ip_name_dict_in_room, selected_room_ip
#         message["ROOM_IP"] = selected_room_ip
#         message["USER_NAME"] = name
#         message["USER_IP"] = IPAddr
#     elif message_type == messageType["song_file_info"]:
#         message["ROOM_IP"] = created_room_ip
#         message["SONG_FILE_NAME"] = current_song["name"]
#         message["SONG_FILE_SIZE"] = current_song["size"]
#         message["SONG_CURRENT_TIME"] = current_song["time"]
#         message["SONG_STATUS"] = current_song["status"]
#     elif message_type == messageType["song_file_request"]:
#         message["USER_IP"] = IPAddr
#         message["SONG_FILE_NAME"] = current_song["name"]
#     else:
#         print("Wrong message type: " + message_type)
#         return
#
#     return json.dumps(message)
#
#
# def sendTCP(IP, tcpMessage):
#     dis = threading.Thread(target=thread_unicast, args=(IP, tcpMessage), daemon=True)
#     dis.start()
#
#
# # Listen UDP functions
#
# def listenUDP():
#     while True:
#         with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
#             s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#             s.bind(("", port))
#             s.setblocking(0)
#             result = select.select([s], [], [])
#             msg = result[0][0].recv(bufferSize)
#             output = msg.decode()
#             received_packet = json.loads(output)
#
#         print("Received UDP:", received_packet)
#
#         handle_UDP_incoming(received_packet)
#
#
# def handle_UDP_incoming(received_packet):
#     if "TYPE" not in received_packet:
#         return
#
#     received_packet_type = received_packet["TYPE"]
#
#     if received_packet_type == messageType["discover_rooms"]:
#         print("AAAAAAAAA")
#         handle_discover_rooms(received_packet)
#     elif received_packet_type == messageType["create_room"]:
#         handle_create_room(received_packet)
#     elif received_packet_type == messageType["exit_room_host"]:
#         handle_exit_room_host(received_packet)
#     elif received_packet_type == messageType["enter_room"]:
#         handle_enter_room(received_packet)
#     elif received_packet_type == messageType["exit_room"]:
#         handle_exit_room(received_packet)
#     else:
#         # pass
#         print("UDP unknown type received: ", received_packet_type)
#
#
# def handle_discover_rooms(received_packet):
#     # TODO
#     if created_room_ip.strip():
#         user_ip = received_packet["USER_IP"]
#         respond_message = createTCPMessage(messageType["respond_rooms"])
#         sendTCP(user_ip, respond_message)
#
#
# def handle_create_room(received_packet):
#     global ip_room_dict
#     room_ip = received_packet["ROOM_IP"]
#     room_name = received_packet["ROOM_NAME"]
#     host_name = received_packet["HOST_NAME"]
#     ip_room_dict[room_ip] = [room_name, host_name]
#     # update room list UI
#
#
# def handle_exit_room_host(received_packet):
#     global ip_room_dict, ip_name_dict_in_room, selected_room_ip, current_song
#     room_ip = received_packet["ROOM_IP"]
#     room_name = received_packet["ROOM_NAME"]
#     host_name = received_packet["HOST_NAME"]
#     if room_ip in ip_room_dict:
#         del ip_room_dict[room_ip]
#     if selected_room_ip == room_ip:
#         ip_name_dict_in_room.clear()
#         selected_room_ip = ""
#         current_song = {"name": "", "size": "", "time": "", "status": ""}
#         ## O odadaki tüm kullanıcılar ana menüye yönlendirilir
#
#
# def handle_enter_room(received_packet):
#     global ip_name_dict_in_room
#     room_ip = received_packet["ROOM_IP"]
#     new_user_name = received_packet["USER_NAME"]
#     new_user_ip = received_packet["USER_IP"]
#     if selected_room_ip.strip():
#         if selected_room_ip == room_ip:
#             ip_name_dict_in_room[new_user_ip] = new_user_name
#             respond_message = createTCPMessage(messageType["respond_entering_room"])
#             sendTCP(new_user_ip, respond_message)
#             if created_room_ip.strip():
#                 # sends song info to user that enter the room
#                 respond_message = createTCPMessage(messageType["song_file_info"])
#                 sendTCP(new_user_ip, respond_message)
#
#
# def handle_exit_room(received_packet):
#     global ip_name_dict_in_room
#     room_ip = received_packet["ROOM_IP"]
#     user_name = received_packet["USER_NAME"]
#     user_ip = received_packet["USER_IP"]
#     if selected_room_ip.strip():
#         if selected_room_ip == room_ip:
#             if user_ip in ip_name_dict_in_room:
#                 del ip_name_dict_in_room[user_ip]
#                 # update user list UI in room
#
#
# # Listen TCP functions
# def listenTCP():
#     while (True):
#         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#             s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#             s.bind((IPAddr, port))
#             s.listen()
#             conn, addr = s.accept()
#             with conn:
#                 output = ""
#                 while (True):
#                     data = conn.recv(1024)
#                     if not data:
#                         break
#                     output += data.decode()
#         if (output == "" or output is None):
#             print("There is a problem about your socket you should restart your cmd or computer")
#             break
#         received_packet = json.loads(output)
#         print("Received TCP:", received_packet)
#         handle_TCP_incoming(received_packet)
#
#
# def handle_TCP_incoming(received_packet):
#     if "TYPE" not in received_packet:
#         return
#
#     received_packet_type = received_packet["TYPE"]
#
#     if received_packet_type == messageType["respond_rooms"]:
#         handle_respond_rooms(received_packet)
#     elif received_packet_type == messageType["respond_entering_room"]:
#         handle_respond_entering_room(received_packet)
#     elif received_packet_type == messageType["song_file_info"]:
#         handle_song_file_info(received_packet)
#     elif received_packet_type == messageType["song_file_request"]:
#         handle_song_file_request(received_packet)
#     else:
#         # pass
#         print("UDP unknown type received: ", received_packet_type)
#
#
# def handle_respond_rooms(received_packet):
#     global ip_room_dict
#     room_ip = received_packet["ROOM_IP"]
#     room_name = received_packet["ROOM_NAME"]
#     host_name = received_packet["HOST_NAME"]
#     ip_room_dict[room_ip] = [room_name, host_name]
#
# def handle_respond_entering_room(received_packet):
#     global ip_name_dict_in_room
#     user_name = received_packet["USER_NAME"]
#     user_ip = received_packet["USER_IP"]
#     ip_name_dict_in_room[user_ip] = user_name
#
#
# def handle_song_file_info(received_packet):
#     room_ip = received_packet["ROOM_IP"]
#     if not received_packet["SONG_FILE_NAME"].strip():
#         return
#     if selected_room_ip == room_ip:
#         current_song["name"] = received_packet["SONG_FILE_NAME"]
#         current_song["size"] = received_packet["SONG_FILE_SIZE"]
#         current_song["time"] = received_packet["SONG_CURRENT_TIME"]
#         current_song["status"] = received_packet["SONG_STATUS"]
#         if True : #song exists
#             return# update song status in local
#         else:
#             # send TCP to get song file
#             respond_message = createTCPMessage(messageType["song_file_request"])
#             sendTCP(room_ip, respond_message)
#
#
# def handle_song_file_request(received_packet):
#     user_ip = received_packet["USER_IP"]
#     requested_file_name = received_packet["SONG_FILE_NAME"]
#     if current_song["name"] == requested_file_name:
#         # Start to send file
#         send_song_file(user_ip, requested_file_name)
#     else:
#         # send new song info
#         # sends song info to user that enter the room
#         respond_message = createTCPMessage(messageType["song_file_info"])
#         sendTCP(user_ip, respond_message)
#
#
# def send_song_file(IP, filename):
#     # create the client socket
#     s = socket.socket()
#     print(f"[+] Connecting to {IP}:{file_port}")
#     s.connect((IP, file_port))
#     print("[+] Connected.")
#
#     file_path = "music/" + filename
#     filesize = os.path.getsize(file_path)
#     # send the filename and filesize
#     s.send(f"{filename}{SEPARATOR}{filesize}".encode())
#
#     # start sending the file
#     # progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
#     with open(file_path, "rb") as f:
#         while True:
#             # read the bytes from the file
#             bytes_read = f.read(BUFFER_SIZE)
#             if not bytes_read:
#                 # file transmitting is done
#                 break
#             # we use sendall to assure transimission in
#             # busy networks
#             s.sendall(bytes_read)
#             # update the progress bar
#             # progress.update(len(bytes_read))
#     # close the socket
#     s.close()
#     # TO DO
#     # respond_message = createTCPMessage(messageType["song_file_info"])
#     # sendTCP(IP, respond_message)
#
#
# # Receive File Function
#
# def receive_song_file():
#     while True:
#         # TCP socket
#         s = socket.socket()
#         # bind the socket to our local address
#         s.bind((IPAddr, file_port))
#         # enabling our server to accept connections
#         # 5 here is the number of unaccepted connections that
#         # the system will allow before refusing new connections
#         s.listen()
#         print(f"[*] Listening as {IPAddr}:{file_port}")
#
#         # accept connection if there is any
#         client_socket, address = s.accept()
#         # if below code is executed, that means the sender is connected
#         print(f"[+] {address} is connected.")
#
#         if address != selected_room_ip:
#             # close the client socket
#             client_socket.close()
#             # close the server socket
#             s.close()
#         else:
#             # receive the file infos
#             # receive using client socket, not server socket
#             received = client_socket.recv(BUFFER_SIZE).decode()
#             filename, filesize = received.split(SEPARATOR)
#
#             file_path = "music/" + filename
#             # convert to integer
#             filesize = int(filesize)
#
#             # start receiving the file from the socket
#             # and writing to the file stream
#             # progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
#             with open(file_path, "wb") as f:
#                 while True:
#                     # read 1024 bytes from the socket (receive)
#                     bytes_read = client_socket.recv(BUFFER_SIZE)
#                     if not bytes_read:
#                         # nothing is received
#                         # file transmitting is done
#                         break
#                     # write to the file the bytes we just received
#                     f.write(bytes_read)
#                     # update the progress bar
#                     # progress.update(len(bytes_read))
#
#             # close the client socket
#             client_socket.close()
#             # close the server socket
#             s.close()
#
#
# # get_ip()
# #
# # # receive_song_file()
# # listenFile = threading.Thread(target=receive_song_file, args=(), daemon=True)
# # listenFile.start()
# #
# # listenUdp = threading.Thread(target=listenUDP, args=(), daemon=True)
# # listenUdp.start()
# #
# # listenTcp = threading.Thread(target=listenTCP, args=(), daemon=True)
# # listenTcp.start()
# #
# # # Send File Function
# # if not os.path.exists('music'):
# #     os.makedirs('music')
