from math import sqrt
from operator import itemgetter  # para ordenar

import matplotlib.pyplot as plt
import numpy as np
import numpy.random
from numpy import mean
from pandas import DataFrame  # para printar bonito
from scipy.stats import expon


def nextMessage(timeline, users, posts_number, elapsed_time):
    # Declara matriz de eventos que acumula os eventos gerados em menor tempo
    events_matrix = []

    for i in range(users * 2):
        if i > 4:
            events_matrix.append([i - users, 0, 0, 0, 0, 0])
        else:
            events_matrix.append([i, 0, 0, 0, 0, 0])

    for i in range(users):
        ############################# CALCULA FAKE NEWS ################################
        message_content = np.random.randint(0, users)  # Gera proximo vizinho aleatorio entre 1 e total de usuarios

        # Caso o random anterior seja o proprio usuario que envia, gera um novo usuario vizinho
        while message_content == i:
            message_content = np.random.randint(0, users)

        events_matrix[i][1] = message_content  # Preenche o campo destino, com o vizinho que recebe a mensagem

        # Considerando fakenews = 1 e goodnews = 0
        if sum(timeline[i]) == posts_number:  # Se so tiver fakenews na timeline, propaga fakenews
            events_matrix[i][2] = 1
        elif sum(timeline[i]) == 0:  # Se so tiver goodnews na timeline, propaga goodnews
            events_matrix[i][2] = 0
        else:
            events_matrix[i][2] = 1

        events_matrix[i][5] = expon.rvs(scale=1)  # Calcula tempo de envio da mensagem
        events_matrix[i][4] = events_matrix[i][5] + elapsed_time  # Calcula tempo total de envios até o momento

        ############################# CALCULA GOOD NEWS ################################
        message_content = np.random.randint(0, users)
        while message_content == i:
            message_content = np.random.randint(0, users)

        events_matrix[users + i][1] = message_content

        # Considerando fakenews = 1 e goodnews = 0
        if sum(timeline[i]) == posts_number:  # Se so tiver fakenews na timeline, propaga fakenews
            events_matrix[users + i][2] = 1
        elif sum(timeline[i]) == 0:  # Se so tiver goodnews na timeline, propaga goodnews
            events_matrix[users + i][2] = 0
        else:
            events_matrix[users + i][2] = 0

        events_matrix[users + i][5] = expon.rvs(scale=1)
        events_matrix[users + i][4] = events_matrix[users + i][5] + elapsed_time

    # Imprime a matriz de eventos organizada
    df = DataFrame(events_matrix,
                   columns=["Source User", "Destination User", "News Type", "Fakenews Total", "Total Elapsed Time",
                            "Elapsed Time"])
    # print(df)

    # Ordena os eventos em ordem crescente, pois o evento de menor tempo acontece primeiro
    return sorted(events_matrix, key=itemgetter(5))[0]


# Gera timelines de diferentes valores iniciais
def initializeTimelines():
    timelines_list = []
    timelines_list.append([[1, 0], [1, 0], [1, 0], [1, 0], [1, 0]])  # todos com 1 fake no top
    timelines_list.append([[0, 1], [0, 1], [0, 1], [0, 1], [0, 1]])  # todos com 1 fake no bot
    timelines_list.append([[1, 0], [0, 0], [0, 0], [0, 0], [0, 0]])  # 1 pessoa com 1 fakenews
    timelines_list.append([[1, 1], [0, 0], [0, 0], [0, 0], [0, 0]])  # 1 pessoa com 2 fakenews
    timelines_list.append([[1, 1], [1, 1], [1, 1], [0, 0], [0, 0]])  # 3 pessoas com 2 fakenews
    timelines_list.append([[1, 1], [1, 1], [1, 1], [1, 1], [0, 0]])  # 4 pessoas com 2 fakenews

    return timelines_list


# Soma todos os valores de uma matriz
def sumMatrixValues(matrix):
    return np.matrix(matrix).sum()


def runSimulation(timeline_number):
    simulation_limit = 200
    posts_number = 2
    users = 5

    timeline = initializeTimelines()[timeline_number]

    counter = 0
    total_time = 0

    events_total = []

    # Loop principal. Roda um numero muito grande de vezes para ter uma caracteristica estacionaria
    # Caso fique 100% com fakenews ou 100% com goodnews, a simulação se encerra
    while ((counter <= simulation_limit) & (sumMatrixValues(timeline) != 0) & (
            sumMatrixValues(timeline) != posts_number * users)):

        next_simulation_event = nextMessage(timeline, users, posts_number, total_time)

        # ####################### FIFO #########################

        # Seguindo o FIFO, o topo recebe a proxima mensagem e os valores fazem um "shift" para a direita,
        # para simular uma entrada no topo e os valores descendo na lista
        for i in range(posts_number):
            timeline[next_simulation_event[1]][1] = timeline[next_simulation_event[1]][1 - 1]
        # Entrada de um evento no topo da timeline
        timeline[next_simulation_event[1]][0] = next_simulation_event[2]
        # para RDN podemos escolher aleatoriamente onde a mensagem vai entrar, entao basicamente vamos soh substituir
        # um post aleatoriamente

        next_simulation_event[3] = sumMatrixValues(timeline)
        total_time = next_simulation_event[4]

        events_total.append(next_simulation_event)

        counter = counter + 1

    return events_total


simulation_repetition_limit = 50

# Loop para rodar todas as variadas timelines geradas anteriormente
for timelines in range(len(initializeTimelines())):
    total_fakenews_sent = []
    total_fakenews_sent2 = []
    plt.figure()
    simulation_times_mean_list = []
    fakenews_percentage_list = []
    total_fakenews_probability_per_time_list = []
    total_goodnews_probability_per_time_list = []

    for i in range(simulation_repetition_limit):

        simulation_times = []
        simulation_final_states = []
        total_simulation_values = []
        number_of_messages = []

        simulation_repetition = 150
        simulation_events = []

        for i in range(simulation_repetition):
            run_simulation = runSimulation(timelines)
            simulation_events.append(run_simulation[-1])
            total_simulation_values.append(run_simulation)
            simulation_times.append(simulation_events[i][4])
            simulation_final_states.append(simulation_events[i][3])

        counter_fakenews = 0
        counter_goodnews = 0
        fakenews_probability_per_time = []
        goodnews_probability_per_time = []
        for message in simulation_final_states:
            if message == 10:
                counter_fakenews += 1
            else:
                counter_goodnews += 1
            fakenews_probability_per_time.append(counter_fakenews / len(simulation_final_states))
            goodnews_probability_per_time.append(counter_goodnews / len(simulation_final_states))

        total_fakenews_probability_per_time_list.append(fakenews_probability_per_time)
        total_goodnews_probability_per_time_list.append(goodnews_probability_per_time)
        arr = numpy.array(total_fakenews_probability_per_time_list)
        arr2 = numpy.array(total_goodnews_probability_per_time_list)

        for simulation in total_simulation_values:
            for events in simulation:
                number_of_messages.append(events[2])

        simulation_times_mean_list.append((mean(simulation_times)))

        # Lista das porcentagens de vezes que teve FakeNews
        fakenews_percentage_list.append((simulation_final_states.count(10) / len(simulation_final_states)))

        total_fakenews_sent.append(((number_of_messages.count(1) / len(number_of_messages)),
                                    simulation_final_states[i]))  # Media de fake news enviadas
        total_fakenews_sent2.append(((len(number_of_messages)), simulation_final_states[i]))

    upper_confidence_interval_of_fakenews = mean(fakenews_percentage_list) + ((1.96 * sqrt(sum(
        (fakenews_percentage_list - mean(fakenews_percentage_list)) ** 2 / (len(fakenews_percentage_list))))) / sqrt(
        len(fakenews_percentage_list)))
    lower_confidence_interval_of_fakenews = mean(fakenews_percentage_list) - ((1.96 * sqrt(sum(
        (fakenews_percentage_list - mean(fakenews_percentage_list)) ** 2 / (len(fakenews_percentage_list))))) / sqrt(
        len(fakenews_percentage_list)))

    print('#### FAKENEWS ####')
    print('Intervalo de confiança inferior de Fakenews')
    print(lower_confidence_interval_of_fakenews)
    print('Media da porcentagem de ocorrer de Fakenews')
    print(mean(fakenews_percentage_list))
    print('Intervalo de confiança superior de Fakenews')
    print(upper_confidence_interval_of_fakenews)
    print('Menor porcentagem de Fakenews')
    print(min(fakenews_percentage_list))
    print('Maior porcentagem de Fakenews')
    print(max(fakenews_percentage_list))

    percentage_of_fakenews_resulting_in_fakenews = 0

    for fakenews_mean_and_simularion_result_pair in total_fakenews_sent:
        if fakenews_mean_and_simularion_result_pair[1] == 10:  # Resulta em uma fakenews
            percentage_of_fakenews_resulting_in_fakenews = mean(fakenews_mean_and_simularion_result_pair[0])

    print('Em media, só foram necessários', percentage_of_fakenews_resulting_in_fakenews,
          '% de Fakenews para terminar em Fakenews')

    sum_m_fk = 0
    sum_m_gd = 0
    for m in total_fakenews_sent2:
        if m[1] == 10:
            sum_m_fk += m[0]
        else:
            sum_m_gd += m[0]

    print('Em media, só foram necessários', sum_m_fk / simulation_repetition,
          'de mensagens de Fakenews para terminar em fakenews')
    print('Em media, só foram necessários', sum_m_gd / simulation_repetition,
          'de mensagens de Goodnews para terminar em Goodnews')


    upper_confidence_interval_of_time_elapsed = mean(simulation_times_mean_list) + ((1.96 * sqrt(sum(
        (simulation_times_mean_list - mean(simulation_times_mean_list)) ** 2 / (
            len(simulation_times_mean_list))))) / sqrt(len(simulation_times_mean_list)))
    lower_confidence_interval_of_time_elapsed = mean(simulation_times_mean_list) - ((1.96 * sqrt(sum(
        (simulation_times_mean_list - mean(simulation_times_mean_list)) ** 2 / (
            len(simulation_times_mean_list))))) / sqrt(len(simulation_times_mean_list)))

    print('Intervalo de confiança inferior da media do tempo de simulação')
    print(lower_confidence_interval_of_time_elapsed)
    print('Media do tempo de simulação')
    print(mean(simulation_times_mean_list))
    print('Intervalo de confiança superior da media do tempo de simulação')
    print(upper_confidence_interval_of_time_elapsed)
    print('Menor tempo medio de simulação')
    print(min(simulation_times_mean_list))
    print('Maior tempo medio de simulação')
    print(max(simulation_times_mean_list))

    if timelines == 0:
        title = "All users with 1 fakenews on top"
    elif timelines == 1:
        title = "All users with 1 fakenews on bottom"
    elif timelines == 2:
        title = "1 user with 1 fakenews"
    elif timelines == 3:
        title = "1 user with 2 fakenews"
    elif timelines == 4:
        title = "3 users with 2 fakenews"
    elif timelines == 5:
        title = "4 users com 2 fakenews"
    elif timelines == 6:
        title = 1

    simulation_times.sort()
    plt.subplot(1, 3, 1)
    plot_total_fakenews_mean = arr.mean(axis=0)
    plt.plot(simulation_times, plot_total_fakenews_mean)
    plot_total_goodnews_mean = arr2.mean(axis=0)
    plt.plot(simulation_times, plot_total_goodnews_mean)

    plt.ylabel("state probability")
    plt.xlabel("time")
    plt.show()

    plt.subplot(1, 3, 2)
    plt.plot(simulation_times_mean_list)
    plt.title(title, loc='center')
    ym = [mean(simulation_times_mean_list)] * len(simulation_times_mean_list)
    y_ic_sup = [upper_confidence_interval_of_time_elapsed] * len(simulation_times_mean_list)
    y_ic_inf = [lower_confidence_interval_of_time_elapsed] * len(simulation_times_mean_list)
    plt.plot(ym)
    plt.plot(y_ic_sup)
    plt.plot(y_ic_inf)
    plt.xlabel("simulations")
    plt.ylabel("mean time")
    plt.show()

    plt.subplot(1, 3, 3)
    plt.plot(fakenews_percentage_list)

    total_goodnews_timeline = [1 - a for a in fakenews_percentage_list]  # Complementar das fakenews timeline
    plt.plot(total_goodnews_timeline)

    fake_m = [mean(fakenews_percentage_list)] * len(simulation_times_mean_list)
    y_ic_sup = [upper_confidence_interval_of_fakenews] * len(simulation_times_mean_list)
    y_ic_inf = [lower_confidence_interval_of_fakenews] * len(simulation_times_mean_list)
    plt.plot(fake_m, 'k')
    plt.plot(y_ic_sup, 'g')
    plt.plot(y_ic_inf, 'r')

    upper_confidence_interval_of_goodnews = mean(total_goodnews_timeline) + ((1.96 * sqrt(
        sum((total_goodnews_timeline - mean(total_goodnews_timeline)) ** 2 / (len(total_goodnews_timeline))))) / sqrt(
        len(total_goodnews_timeline)))
    lower_confidence_interval_of_goodnews = mean(total_goodnews_timeline) - ((1.96 * sqrt(
        sum((total_goodnews_timeline - mean(total_goodnews_timeline)) ** 2 / (len(total_goodnews_timeline))))) / sqrt(
        len(total_goodnews_timeline)))

    good_m = [mean(total_goodnews_timeline)] * len(simulation_times_mean_list)
    y_ic_sup_gd = [upper_confidence_interval_of_goodnews] * len(simulation_times_mean_list)
    y_ic_inf_gd = [lower_confidence_interval_of_goodnews] * len(simulation_times_mean_list)
    plt.plot(good_m, 'k')
    plt.plot(y_ic_sup_gd, 'g')
    plt.plot(y_ic_inf_gd, 'r')

    plt.xlabel("simulations")
    plt.ylabel("state probability")
    plt.show()

