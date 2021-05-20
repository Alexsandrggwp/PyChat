import math
import random
import secrets

HIDDEN_NEURONS_AMOUNT = 100
INPUT_NEURON_AMOUNT = 50
WEIGHT_LIMIT = 3


def _sign(number):
    if number < 0:
        return -1
    elif number == 0:
        return 0
    else:
        return 1


def init_vector(input_neurons, hidden_neurons):
    vector = []
    for i in range(hidden_neurons):
        vector.append([])
        for j in range(input_neurons):
            while True:
                vector_value = secrets.randbelow(3) - 1
                if vector_value != 0:
                    vector[i].append(vector_value)
                    break
    return vector


class CryptoNetwork:

    def __init__(self,  input_neurons_length, hidden_neurons_length, weight_bound):
        self.input_neurons_length = input_neurons_length
        self.hidden_neurons_length = hidden_neurons_length
        self.weight_bound = weight_bound
        self.weights = self._init_weights()
        self.inputs = []
        self.hidden_neurons_results = []
        self.net_result = 0

    def perform(self):
        hidden_neurons_results = []
        input_results = self._multiply_input_by_weights()

        for i in range(self.hidden_neurons_length):
            hidden_neurons_results.append(_sign(sum(input_results[i])))
            if hidden_neurons_results[i] == 0:
                hidden_neurons_results[i] = 1

        net_result = math.prod(hidden_neurons_results)

        self.hidden_neurons_results = hidden_neurons_results
        self.net_result = net_result

        return net_result

    def learn(self):
        for i in range(self.hidden_neurons_length):
            if self.hidden_neurons_results[i] == self.net_result:
                for j in range(self.input_neurons_length):
                    self.weights[i][j] = self._tetta(self.weights[i][j] + (self.inputs[i][j] * self.net_result))

    def _multiply_input_by_weights(self):
        input_results = []

        if len(self.inputs) * len(self.inputs[0]) == len(self.weights) * len(self.weights[0]):
            for i in range(self.hidden_neurons_length):
                input_results.append([])
                for j in range(self.input_neurons_length):
                    input_results[i].append(self.inputs[i][j] * self.weights[i][j])
        else:
            print("oh my, number of inputs of given Vector isn't equal a number of given weights")
            exit(1)

        return input_results

    def _init_weights(self):
        self.weights = []

        for i in range(self.hidden_neurons_length):
            self.weights.append([])
            for j in range(self.input_neurons_length):
                self.weights[i].append(random.randint(-self.weight_bound, self.weight_bound))

        return self.weights

    def _tetta(self, number):
        if -self.weight_bound < number < self.weight_bound:
            return number
        else:
            return _sign(number) * self.weight_bound
