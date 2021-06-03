import socket
import select
import threading

from entities.user import User
from tools.Converter import SYNC_HEADER, COMMON_HEADER, WEIGHT_HEADER, \
    convert_string_to_collection, IP, PORT, HEADER_LENGTH, INIT_HEADER, FORMAT, SYNC_COMPLETE_HEADER

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((IP, PORT))
server_socket.listen()

clients = {server_socket: None}


def main():
    while True:
        read_socket, _, exception_socket = select.select(clients, [], clients)

        for notified_socket in read_socket:
            if notified_socket == server_socket:
                client_socket, client_address = server_socket.accept()
                user = register_user(client_socket)

                sync_thread = threading.Thread(target=process_neural_crypt(user))
                sync_thread.start()
                print(f"Accepted new connection from {client_address[0]}:{client_address[1]} "
                      f"username:{user.nickname}")
            else:
                message = clients[notified_socket].receive_message()

                if message is False:
                    print(f"Closed connection from {clients[notified_socket].nickname}")
                    notified_socket.close()
                    del clients[notified_socket]
                    continue

                notified_user = clients[notified_socket]
                print(f"Received message from {notified_user.nickname}: {message['data']}")

                broadcast(message["data"], notified_user)

        for notified_socket in exception_socket:
            del clients[notified_socket]


def process_neural_crypt(user):
    print(f"Started neural synchronization for user: {user.nickname}")
    while True:
        user.share_vector()

        server_net_result = user.crypto.perform()

        user.send_message(server_net_result, SYNC_HEADER)

        user_net_result = int(user.receive_message()["data"])
        if user_net_result * server_net_result > 0:
            user.crypto.learn()

            user.send_message("weight request", WEIGHT_HEADER)

            data_weights = user.receive_message()["data"]
            converted_data_weights = convert_string_to_collection(data_weights)

            if user.crypto.weights == converted_data_weights:
                user.send_message("1", SYNC_COMPLETE_HEADER)
                print(f"Synchronization passed successfully for user: {user.nickname}")
                break


def broadcast(broadcast_message, sender_user):
    for receiver_socket in clients:
        if receiver_socket != sender_user.socket and receiver_socket != server_socket:
            clients[receiver_socket].send_message(broadcast_message, COMMON_HEADER, sender_user.nickname)


def register_user(sender_socket):
    main_header = sender_socket.recv(HEADER_LENGTH)
    if main_header != INIT_HEADER:
        print(f"Unrecognized header: {main_header}. Terminate session")
        sender_socket.close()
        exit(1)

    user_nickname_header = sender_socket.recv(HEADER_LENGTH).decode(FORMAT)
    user_nickname_length = int(user_nickname_header)
    user_nickname = sender_socket.recv(user_nickname_length).decode(FORMAT)

    sender_user = User(user_nickname, sender_socket)
    clients[sender_socket] = sender_user

    return sender_user


if __name__ == "__main__":
    print("Server is running...")
    main()
