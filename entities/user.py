from neuralNet.nerualNet import CryptoNetwork, init_vector, HIDDEN_NEURONS_AMOUNT, INPUT_NEURON_AMOUNT, WEIGHT_LIMIT
from tools.Converter import convert_collection_to_string, VECTOR_HEADER, WEIGHT_HEADER, get_int_length, SYNC_HEADER, \
    COMMON_HEADER, HEADER_LENGTH, FORMAT, INIT_HEADER, SYNC_COMPLETE_HEADER


class User:

    def __init__(self, nickname, socket):
        self.nickname = nickname
        self.socket = socket
        self.crypto = CryptoNetwork(INPUT_NEURON_AMOUNT, HIDDEN_NEURONS_AMOUNT, WEIGHT_LIMIT)

    def send_message(self, data, main_header, nickname="system"):
        if main_header not in [INIT_HEADER, SYNC_HEADER, VECTOR_HEADER, WEIGHT_HEADER, COMMON_HEADER,
                               SYNC_COMPLETE_HEADER]:
            print(f"Unrecognized header: {main_header}. Terminate session")
            self.socket.close()
            exit(1)

        if isinstance(data, int):
            data_header = f"{get_int_length(data):<{HEADER_LENGTH}}".encode(FORMAT)
            data = str(data).encode(FORMAT)
        else:
            data_header = f"{len(data):<{HEADER_LENGTH}}".encode(FORMAT)
            data = data.encode(FORMAT)

        if main_header != COMMON_HEADER:
            self.socket.send(main_header +
                             data_header + data)
        else:
            username_header = f"{len(nickname):<{HEADER_LENGTH}}".encode(FORMAT)
            username = nickname.encode(FORMAT)
            self.socket.send(main_header +
                             username_header + username +
                             data_header + data)

    def receive_message(self):
        main_header = self.socket.recv(HEADER_LENGTH)
        if main_header not in [INIT_HEADER, SYNC_HEADER, VECTOR_HEADER, WEIGHT_HEADER, COMMON_HEADER,
                               SYNC_COMPLETE_HEADER]:
            print(f"Unrecognized header: {main_header}. Terminate session")
            self.socket.close()
            exit(1)
        if main_header != COMMON_HEADER:
            data_header = self.socket.recv(HEADER_LENGTH).decode(FORMAT)
            data_length = int(data_header)
            data = self.socket.recv(data_length).decode(FORMAT)

            return {"main_header": main_header,
                    "data_header": data_header, "data": data}
        else:
            username_header = self.socket.recv(HEADER_LENGTH).decode(FORMAT)
            username_length = int(username_header)
            username = self.socket.recv(username_length).decode(FORMAT)

            data_header = self.socket.recv(HEADER_LENGTH).decode(FORMAT)
            data_length = int(data_header)
            data = self.socket.recv(data_length).decode(FORMAT)

            return {"main_header": main_header,
                    "username_header": username_header, "username": username,
                    "data_header": data_header, "data": data}

    def share_vector(self):
        shared_vector = init_vector(INPUT_NEURON_AMOUNT, HIDDEN_NEURONS_AMOUNT)
        self.crypto.inputs = shared_vector

        shared_vector_string = convert_collection_to_string(shared_vector)
        self.send_message(shared_vector_string, VECTOR_HEADER)

    def share_weights(self):
        shared_weights_string = convert_collection_to_string(self.crypto.weights)
        self.send_message(shared_weights_string, WEIGHT_HEADER)
