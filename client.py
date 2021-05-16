import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog

from entities.user import User, receive_message, send_message
from tools.Helper import SYNC_HEADER, VECTOR_HEADER, WEIGHT_HEADER, COMMON_HEADER, INIT_HEADER, \
    convert_string_to_collection, convert_collection_to_string

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 9090
FORMAT = 'utf-8'

HIDDEN_NEURONS_AMOUNT = 20
INPUT_NEURON_AMOUNT = 20
WEIGHT_LIMIT = 3


class Client:

    def __init__(self, host, port):
        #nick_window = tkinter.Tk()
        #nick_window.withdraw()
        #user_nickname = simpledialog.askstring("Nickname", "Please choose a nickname", parent=nick_window)
        user_nickname = "nick"

        user_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.user = User(f"{len(user_nickname):<{HEADER_LENGTH}}", user_nickname, user_socket)
        self.socket_connect(host, port)

        self.gui_done = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.process_message)

        gui_thread.start()
        receive_thread.start()

    def process_message(self):
        while self.running:
            try:
                if self.gui_done:
                    received_message = receive_message(self.user.socket)

                    if received_message["main_header"] == COMMON_HEADER:
                        self.view_message(self.user.nickname, received_message["data"])

                    elif received_message["main_header"] == SYNC_HEADER:
                        user_net_result = self.user.crypto.perform()

                        send_message(self.user.socket, user_net_result, SYNC_HEADER)
                        server_net_result = int(received_message["data"])

                        if server_net_result * user_net_result > 0:
                            self.user.crypto.learn()

                    elif received_message["main_header"] == VECTOR_HEADER:
                        self.user.crypto.inputs = convert_string_to_collection(received_message["data"])

                    elif received_message["main_header"] == WEIGHT_HEADER:
                        weight_message = convert_collection_to_string(self.user.crypto.weights)
                        send_message(self.user.socket, weight_message, WEIGHT_HEADER)

            except ConnectionAbortedError as err:
                print(f"ConnectionAbortedError: {err}")
                break

    def write_message(self):
        message = self.input_area.get('1.0', 'end')
        send_message(self.user.socket, message, COMMON_HEADER)
        self.view_message(self.user.nickname, message)
        self.input_area.delete('1.0', 'end')

    def socket_connect(self, host, port):
        self.user.socket.connect((host, port))
        send_message(self.user.socket, self.user.nickname, INIT_HEADER)

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
