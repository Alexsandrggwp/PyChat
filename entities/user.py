from neuralNet.nerualNet import CryptoNetwork, init_vector

HIDDEN_NEURONS_AMOUNT = 10
INPUT_NEURON_AMOUNT = 5
WEIGHT_LIMIT = 3

HEADER_LENGTH = 10
FORMAT = 'utf-8'

VECTOR_HEADER = "VECTORHEAD".encode(FORMAT)
WEIGHT_HEADER = "WEIGHTHEAD".encode(FORMAT)


def receive_message(sender_socket):
    message_header = sender_socket.recv(HEADER_LENGTH).decode(FORMAT)
    message_length = int(message_header)
    message = sender_socket.recv(message_length).decode(FORMAT)

    return {"header": message_header, "data": message}


def _convert_to_bytes(int_collection_2d):
    shared_bytes = b''
    for i in int_collection_2d:
        for j in i:
            jj = str(j).encode(FORMAT)
            shared_bytes += jj

    return shared_bytes


class User:

    def __init__(self, nickname_header, nickname, socket):
        self.nickname_header = nickname_header
        self.nickname = nickname
        self.socket = socket
        self.crypto = CryptoNetwork(HIDDEN_NEURONS_AMOUNT, INPUT_NEURON_AMOUNT, WEIGHT_LIMIT)

    def share_vector(self):
        shared_vector = init_vector(INPUT_NEURON_AMOUNT, HIDDEN_NEURONS_AMOUNT)
        self.crypto.inputs = shared_vector

        shared_vector_bytes = _convert_to_bytes(shared_vector)
        shared_inputs_header = f"{len(shared_vector_bytes):<{HEADER_LENGTH}}".encode(FORMAT)

        self.socket.send(VECTOR_HEADER + shared_inputs_header + shared_vector_bytes)

    def share_weights(self):
        shared_weights_bytes = _convert_to_bytes(self.crypto.weights)
        shared_weights_header = f"{len(shared_weights_bytes):<{HEADER_LENGTH}}".encode(FORMAT)

        self.socket.send(WEIGHT_HEADER + shared_weights_header + shared_weights_bytes)
