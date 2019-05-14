from dataset import get_faces, enhance_data, save_faces
from features import get_hog, get_dataset_hogs, save_hogs_dataset, read_hogs_dataset
from classification import get_x_and_y, get_best_knn, get_model_stats, get_best_mlp, get_PCA

from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier

import random

random.seed(0)

print("================================ PRE PROCESSING ================================")
print("Lendo dados ORL Faces")
orl_faces = get_faces("./datasets/OrlFaces20")
print("ORL FACES:")
print("\tNúmero de pessoas: %d" % len(orl_faces))
print("\tFaces por pessoas: %s" % [len(person) for person in orl_faces])

icmc_faces = get_faces("./datasets/PessoasICMC")
print("Pesosas ICMC:")
print("\tNúmero de pessoas: %d" % len(icmc_faces))
print("\tFaces por pessoas: %s" % [len(person) for person in icmc_faces])

print("---- Gerando faces extras para base Pessoas ICMC ----")
augmented_icmc_faces = enhance_data(icmc_faces)
print("Pesosas ICMC - Extendido:")
print("\tNúmero de pessoas: %d" % len(augmented_icmc_faces))
print("\tFaces por pessoas: %s" % [len(person) for person in augmented_icmc_faces])

print("Salvando Pessoas ICMC - Extendido")
save_faces(augmented_icmc_faces, './datasets/Augmented')

print("================================ HOG EXTRACTION ================================")
read_from_file = False
if read_from_file:
    print("Lendo HOG Features geradas anteriormente")
    icmc_hogs = read_hogs_dataset('icmc_hogs.npy')
    orl_hogs = read_hogs_dataset('orl_hogs.npy')

else:
    print("Gerando novas HOG features")
    icmc_hogs = get_dataset_hogs(augmented_icmc_faces)
    save_hogs_dataset(icmc_hogs, 'icmc_hogs')


    orl_hogs = get_dataset_hogs(orl_faces)
    save_hogs_dataset(orl_hogs, 'orl_hogs')


x, y = get_x_and_y(orl_hogs)
database_name = "ORL"

print("Dimensão Features Originais: ", len(x[0]))
print("===================================== KNN  =====================================")

best_k, best_knn_acc = get_best_knn(x, y, database_name)
# best_k = 1
print("Melhor valor para k: %d com acurácia %2.2f" % (best_k, best_knn_acc*100))

best_knn = KNeighborsClassifier(n_neighbors=best_k)
knn_description = "KNN com k = %s" % best_k

get_model_stats(x, y, best_knn, knn_description, database_name)


print("===================================== MLP  =====================================")
tolerance = 1e-1
activation = 'logistic'

best_learning_rate, best_momentum, best_layer1_size, best_layer2_size, best_acc = get_best_mlp(x, y, database_name)
# best_learning_rate, best_momentum, best_layer1_size, best_layer2_size, best_acc = 1., 1.0, 50, 0, 0.81

print("Melhor configuração para MLP")
print("\tMelhor learning_rate: ", best_learning_rate)
print("\tMelhor momentum: ", best_momentum)
print("\tMelhor layer 1 size: ", best_layer1_size)
print("\tMelhor layer 2 size: ", best_layer2_size)


layers_cfg = [best_layer1_size]
if best_layer2_size > 0:
    layers_cfg.append(best_layer2_size)


best_mlp = MLPClassifier(hidden_layer_sizes=layers_cfg, solver='sgd', momentum=best_momentum, tol=tolerance,
                         max_iter=200, random_state=1, learning_rate='adaptive', learning_rate_init=best_learning_rate,
                         activation=activation)

mlp_description = "MLP: Learning Rate: %.4f, Momentum: %.2f, Layer 1 Size: %d, Layer 2 Size: %d" %\
                  (best_learning_rate, best_momentum, best_layer1_size, best_layer2_size)

get_model_stats(x, y, best_mlp, mlp_description, database_name)

print("===================================== PCA  =====================================")
principal_components = get_PCA(x)


get_model_stats(principal_components, y, best_knn, knn_description, database_name + " PCA")
get_model_stats(principal_components, y, best_mlp, mlp_description, database_name + " PCA")
