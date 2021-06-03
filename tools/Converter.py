import math

from neuralNet.nerualNet import HIDDEN_NEURONS_AMOUNT, INPUT_NEURON_AMOUNT

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 9090
FORMAT = 'utf-8'

INIT_HEADER = "INITHEADER".encode(FORMAT)
SYNC_HEADER = "SYNCHRONIZ".encode(FORMAT)
VECTOR_HEADER = "VECTORHEAD".encode(FORMAT)
WEIGHT_HEADER = "WEIGHTHEAD".encode(FORMAT)
COMMON_HEADER = "COMMONHEAD".encode(FORMAT)
SYNC_COMPLETE_HEADER = "SYCOMPLETE".encode(FORMAT)


def convert_collection_to_string(int_2d_collection):
    shared_bytes = ''
    for i in int_2d_collection:
        for j in i:
            shared_bytes += str(j)

    return shared_bytes


def convert_string_to_collection(string_2d_collection):
    result = []
    try:
        for i in range(HIDDEN_NEURONS_AMOUNT):
            result.append([])
            for j in range(INPUT_NEURON_AMOUNT):
                if string_2d_collection[0] in [str(k) for k in range(10)]:
                    result[i].append(int(string_2d_collection[0]))
                    string_2d_collection = string_2d_collection[1:]
                    continue
                if string_2d_collection[0] == '-':
                    result[i].append(int(string_2d_collection[0] + string_2d_collection[1]))
                    string_2d_collection = string_2d_collection[2:]
    except ValueError as err:
        print(f"ValueError: {err}")

    return result


def get_int_length(digit):
    if digit > 0:
        return str(int(math.log10(digit)) + 1)
    elif digit == 0:
        return "1"
    else:
        return str(int(math.log10(-digit)) + 2)
