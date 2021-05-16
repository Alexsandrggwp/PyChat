from neuralNet.nerualNet import CryptoNetwork, init_vector, HIDDEN_NEURONS_AMOUNT, INPUT_NEURON_AMOUNT, WEIGHT_LIMIT
from tools.Helper import convert_collection_to_string, VECTOR_HEADER, WEIGHT_HEADER, get_int_length, SYNC_HEADER, \
    COMMON_HEADER, HEADER_LENGTH, FORMAT, INIT_HEADER


def receive_message(sender_socket):
    main_header = sender_socket.recv(HEADER_LENGTH)
    if main_header not in [INIT_HEADER, SYNC_HEADER, VECTOR_HEADER, WEIGHT_HEADER, COMMON_HEADER]:
        print(f"Unrecognized header: {main_header}. Terminate session")
        sender_socket.close()
        raise NameError
    data_header = sender_socket.recv(HEADER_LENGTH).decode(FORMAT)
    data_length = int(data_header)
    data = sender_socket.recv(data_length).decode(FORMAT)

    return {"main_header": main_header, "data_header": data_header, "data": data}


def send_message(receiver_socket, data, main_header):
    if main_header not in [INIT_HEADER, SYNC_HEADER, VECTOR_HEADER, WEIGHT_HEADER, COMMON_HEADER]:
        print(f"Unrecognized header: {main_header}. Terminate session")
        receiver_socket.close()
        raise NameError
    if isinstance(data, int):
        data_header = f"{get_int_length(data):<{HEADER_LENGTH}}".encode(FORMAT)
        data = str(data).encode()
    else:
        data_header = f"{len(data):<{HEADER_LENGTH}}".encode(FORMAT)
        data = data.encode()

    receiver_socket.send(main_header + data_header + data)


class User:

    def __init__(self, nickname_header, nickname, socket):
        self.nickname_header = nickname_header
        self.nickname = nickname
        self.socket = socket
        self.crypto = CryptoNetwork(INPUT_NEURON_AMOUNT, HIDDEN_NEURONS_AMOUNT, WEIGHT_LIMIT)

    def share_vector(self):
        shared_vector = init_vector(INPUT_NEURON_AMOUNT, HIDDEN_NEURONS_AMOUNT)
        self.crypto.inputs = shared_vector

        shared_vector_string = convert_collection_to_string(shared_vector)
        send_message(self.socket, shared_vector_string, VECTOR_HEADER)

    def share_weights(self):
        shared_weights_string = convert_collection_to_string(self.crypto.weights)
        send_message(self.socket, shared_weights_string, WEIGHT_HEADER)
