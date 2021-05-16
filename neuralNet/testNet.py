from neuralNet.nerualNet import CryptoNetwork, init_vector, HIDDEN_NEURONS_AMOUNT, INPUT_NEURON_AMOUNT, WEIGHT_LIMIT

server_net = CryptoNetwork(HIDDEN_NEURONS_AMOUNT, INPUT_NEURON_AMOUNT, WEIGHT_LIMIT)
client_net = CryptoNetwork(HIDDEN_NEURONS_AMOUNT, INPUT_NEURON_AMOUNT, WEIGHT_LIMIT)

count = 0
while True:
    count += 1

    net_inputs = init_vector(INPUT_NEURON_AMOUNT, HIDDEN_NEURONS_AMOUNT)
    server_net.inputs = net_inputs
    client_net.inputs = net_inputs  # get from a socket

    if server_net.perform() * client_net.perform() > 0:
        server_net.learn()
        client_net.learn()  # it processing at client

        if server_net.weights == client_net.weights:
            print("CONGRATULATIONS NETS' WEIGHTS ARE EQUAL")
            print(count)
            break
