import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog

from server import COMMON_HEADER, VECTOR_HEADER, SYNC_HEADER, INIT_HEADER, get_int_length
from entities.user import receive_message, User

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 9090
FORMAT = 'utf-8'

HIDDEN_NEURONS_AMOUNT = 10
INPUT_NEURON_AMOUNT = 5
WEIGHT_LIMIT = 3


class Client:

    def __init__(self, host, port):
        nick_window = tkinter.Tk()
        nick_window.withdraw()
        user_nickname = simpledialog.askstring("Nickname", "Please choose a nickname", parent=nick_window)

        user_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.user = User(f"{len(user_nickname):<{HEADER_LENGTH}}", user_nickname, user_socket)
        self.socket_connect(host, port)

        self.gui_done = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.process_message)

        gui_thread.start()
        receive_thread.start()

    def write_message(self):
        message = self.input_area.get('1.0', 'end')
        message_header = f"{len(message):<{HEADER_LENGTH}}"
        self.user.socket.send(COMMON_HEADER +
                              message_header.encode(FORMAT) +
                              message.encode(FORMAT))
        self.view_message(self.user.nickname, message)
        self.input_area.delete('1.0', 'end')

    def process_message(self):
        while self.running:
            try:
                if self.gui_done:
                    main_header = self.user.socket.recv(HEADER_LENGTH)
                    if [SYNC_HEADER, VECTOR_HEADER, COMMON_HEADER].count(main_header) == 0:
                        print(f"Unrecognized header: {main_header}. Terminate session")
                        self.stop()

                    if main_header == COMMON_HEADER:
                        self.view_message(receive_message(self.user.socket)["data"],
                                          receive_message(self.user.socket)["data"])

                    elif main_header == SYNC_HEADER:
                        user_net_result = self.user.crypto.perform()
                        self.user.socket.send(SYNC_HEADER +
                                              f"{get_int_length(user_net_result):<{HEADER_LENGTH}}".encode(FORMAT)
                                              + str(user_net_result).encode(FORMAT))

                        if int(receive_message(self.user.socket)["data"]) * user_net_result > 0:
                            self.user.crypto.learn()

                    elif main_header == VECTOR_HEADER:
                        vector_message_header = self.user.socket.recv(HEADER_LENGTH).decode(FORMAT)
                        vector_message_length = int(vector_message_header)
                        vector_message = self.user.socket.recv(vector_message_length).decode(FORMAT)

                        # self.user.crypto.inputs
                        self.view_message("system", vector_message)
                        self.set_vector_from_message(vector_message)
                        self.view_message("system", self.user.crypto.inputs)

            except ConnectionAbortedError:
                break
            except Exception as err:
                print("Error: " + str(err))
                self.stop()
                break

    def socket_connect(self, host, port):
        self.user.socket.connect((host, port))
        username_header = f"{len(self.user.nickname):<{HEADER_LENGTH}}"
        self.user.socket.send(INIT_HEADER +
                              username_header.encode(FORMAT) +
                              self.user.nickname.encode(FORMAT))

    def set_vector_from_message(self, vector_message):
        self.user.crypto.inputs = []
        for i in range(HIDDEN_NEURONS_AMOUNT):
            self.user.crypto.inputs.append([])
            for j in range(INPUT_NEURON_AMOUNT):
                if vector_message[0] == '1':
                    self.user.crypto.inputs[i].append(int(vector_message[0]))
                    vector_message = vector_message[1:]
                    continue
                if vector_message[0] == '-':
                    self.user.crypto.inputs[i].append(int(vector_message[0] + vector_message[1]))
                    vector_message = vector_message[2:]

    def stop(self):
        self.running = False
        self.win.destroy()
        self.user.socket.close()
        exit(0)

    def view_message(self, name, content):
        self.text_area.config(state='normal')
        self.text_area.insert('end', f"{name} > {content}")
        self.text_area.yview('end')
        self.text_area.config(state='disabled')

    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.configure(bg="lightgray")

        self.chat_label = tkinter.Label(self.win, text="Chat:", bg="lightgray")
        self.chat_label.config(font=("Arial", 16))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win)
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state='disabled')

        self.msg_label = tkinter.Label(self.win, text="Message:", bg="lightgray")
        self.msg_label.config(font=("Arial", 16))
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, height=3)
        self.input_area.pack(padx=20, pady=5)

        self.send_button = tkinter.Button(self.win, text="Send", command=self.write_message)
        self.send_button.config(font=("Arial", 16))
        self.send_button.pack(padx=20, pady=5)

        self.gui_done = True

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()


if __name__ == "__main__":
    client = Client(IP, PORT)
