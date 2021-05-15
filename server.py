import math
import socket
import select
import threading

from entities.user import User, receive_message, convert_string_to_collection

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 9090
FORMAT = 'utf-8'

INIT_HEADER = "INITHEADER".encode(FORMAT)
SYNC_HEADER = "SYNCHRONIZ".encode(FORMAT)
VECTOR_HEADER = "VECTORHEAD".encode(FORMAT)
WEIGHT_HEADER = "WEIGHTHEAD".encode(FORMAT)
COMMON_HEADER = "COMMONHEAD".encode(FORMAT)

HIDDEN_NEURONS_AMOUNT = 10
INPUT_NEURON_AMOUNT = 5
WEIGHT_LIMIT = 3

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen()

sockets_list = [server_socket]
clients = {}


def main():
    while True:
        read_socket, _, exception_socket = select.select(sockets_list, [], sockets_list)

        for notified_socket in read_socket:
            if notified_socket == server_socket:
                client_socket, client_address = server_socket.accept()

                user = process_message(client_socket)

                sync_thread = threading.Thread(target=process_neural_crypt(user))
                sync_thread.start()

                print(f"Accepted new connection from {client_address[0]}:{client_address[1]} "
                      f"username:{user.nickname}")
            else:
                message = process_message(notified_socket)

                if message is False:
                    print(f"Closed connection from {clients[notified_socket].nickname}")
                    sockets_list.remove(notified_socket)
                    notified_socket.close()
                    del clients[notified_socket]
                    continue

                notified_user = clients[notified_socket]
                print(f"Received message from {notified_user.nickname}: {message['data']}")

                broadcast(message, notified_user)

        for notified_socket in exception_socket:
            sockets_list.remove(notified_socket)
            del clients[notified_socket]


# if user.socket.recv(HEADER_LENGTH) != SYNC_HEADER:
#    print("Unrecognized header while sync. Terminate session")
#    sockets_list.remove(user.socket)
#    user.socket.close()
#    del clients[user.socket]
#    break
def process_neural_crypt(user):
    count = 0
    while True:
        count += 1
        print(count)
        user.share_vector()

        server_net_result = user.crypto.perform()

        server_net_result_length = f"{get_int_length(server_net_result):<{HEADER_LENGTH}}".encode(FORMAT)

        user.socket.send(SYNC_HEADER +
                         server_net_result_length
                         + str(server_net_result).encode(FORMAT))

        main_header = user.socket.recv(HEADER_LENGTH)
        if main_header == SYNC_HEADER:
            user_net_result = int(receive_message(user.socket)["data"])
            if user_net_result * server_net_result > 0:
                user.crypto.learn()
                data_weights = receive_message(user.socket)["data"]
                converted_data_weights = convert_string_to_collection(data_weights)
                if user.crypto.weights != converted_data_weights:
                    continue
                else:
                    print("CONGRATULATIONS NETS' WEIGHTS ARE EQUAL")
                    print(count)
                    break
            else:
                continue


def process_message(sender_socket):
    try:
        main_header = sender_socket.recv(HEADER_LENGTH)

        if not len(main_header):
            return False

        elif [INIT_HEADER, SYNC_HEADER, VECTOR_HEADER, COMMON_HEADER].count(main_header) == 0:
            print("Unrecognized header. Terminate session")
            sender_socket.close()
            return False

        elif main_header == INIT_HEADER:
            return register_user(sender_socket)

        elif main_header == COMMON_HEADER:
            return receive_message(sender_socket)

    except Exception as err:
        print(f"Something wrong: {err}")
        return False


def broadcast(broadcast_message, sender_user):
    for receiver_socket in clients:
        if receiver_socket != sender_user.socket:
            receiver_socket.send(COMMON_HEADER +
                                 sender_user.nickname_header.encode(FORMAT) + sender_user.nickname.encode(FORMAT) +
                                 broadcast_message['header'].encode(FORMAT) + broadcast_message['data'].encode(FORMAT))


def register_user(sender_socket):
    user_data_map = receive_message(sender_socket)
    sender_user = User(user_data_map["header"], user_data_map["data"], sender_socket)

    sockets_list.append(sender_socket)
    clients[sender_socket] = sender_user

    return sender_user


def get_int_length(digit):
    if digit > 0:
        return str(int(math.log10(digit)) + 1)
    elif digit == 0:
        return "1"
    else:
        return str(int(math.log10(-digit)) + 2)


if __name__ == "__main__":
    print("Server is running...")
    main()
