import math

FORMAT = 'utf-8'

HIDDEN_NEURONS_AMOUNT = 20
INPUT_NEURON_AMOUNT = 20

INIT_HEADER = "INITHEADER".encode(FORMAT)
SYNC_HEADER = "SYNCHRONIZ".encode(FORMAT)
VECTOR_HEADER = "VECTORHEAD".encode(FORMAT)
WEIGHT_HEADER = "WEIGHTHEAD".encode(FORMAT)
COMMON_HEADER = "COMMONHEAD".encode(FORMAT)


def convert_collection_to_string(int_2d_collection):
    shared_bytes = ''
    for i in int_2d_collection:
        for j in i:
            jj = str(j)
            shared_bytes += jj

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
