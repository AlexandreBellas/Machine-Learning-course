from sklearn.model_selection import StratifiedKFold

from sklearn.metrics import confusion_matrix, accuracy_score, precision_score

from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier

from sklearn.decomposition import PCA

import pandas as pd

import numpy as np

from sys import platform as sys_pf
if sys_pf == 'darwin':
    import matplotlib
    matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
import seaborn as sns


def get_x_and_y(features_dataset):
    """
    get_x_and_y separates the data set with the hog features in feature vector x and target vector y
    To do so, each line of the data set is considered a different class. So for a given data set row, all
    columns are considered different samples of the same class
    :param features_dataset: a slice of slices containing the feature hogs following the schema below
        [
            [person_1_face1_hog, person_1_face2_hog, person_1_face3_hog],
            [person_2_face1_hog, person_2_face2_hog, person_2_face3_hog],
            [person_3_face1_hog, person_3_face2_hog, person_3_face3_hog]

        ]
    :return: a x numpy array containing the features samples
        [
            [person_1_face1_hog],
            [person_1_face2_hog],
            ...
            [person_20_face10_hog]
        ]
        a y numpy array containing the corresponding target class
        [
            [0],
            [0],
            ...
            [19]
        ]
    """

    x = []
    y = []
    for id, person in zip( range(len(features_dataset)), features_dataset):
        for face_feature in person:
            x.append(face_feature)
            y.append(id)

    return np.array(x), np.array(y)


def get_best_knn(x, y, database_name):
    """
    get_best_knn trains knn models with different k parameter and returns the k that yielded the model with best
    accuracy
    :param x: the feature vector
    :param y: the target vector
    :param database_name: name of the data base used to populate the x and y vectors. It's only used to print the
    graphics with the accuracy report
    :return: the k parameter that yielded the best KNN model along with the best accuracy vector
    """

    # Parameters to be tested
    ks = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    # Use stratified K-fold to compute the accuracy for each model
    skf = StratifiedKFold(n_splits=10)
    knn_accs = []

    for k in ks:
        print("Training with k = ", k)
        accs = []
        for train_index, test_index in skf.split(x, y):
            x_train, x_test = x[train_index], x[test_index]
            y_train, y_test = y[train_index], y[test_index]


            knn = KNeighborsClassifier(n_neighbors=k)
            knn.fit(x_train, y_train)
            accs.append(accuracy_score(y_test, knn.predict(x_test)))

        knn_accs.append(np.mean(accs))

    plt.figure(figsize=(15,10))
    plt.plot(ks, knn_accs)
    plt.title("Variação da Acurácia no Modelo KNN para diferentes valores de K para database %s" % database_name, fontsize=16)
    plt.ylabel("Acurácia", fontsize=12)
    plt.xlabel("K", fontsize=12)
    plt.xticks(ks)
    plt.grid(True)
    # plt.show(True)
    plt.savefig("graphs/knn_accuracy.png")

    return ks[np.argmax(knn_accs)], np.max(knn_accs)


def get_best_mlp(x, y, database_name):
    """
    get_best_mlp trains MLP models with different layer 1 and layer 2 size and returns the layer sizes that yielded the
    model with best accuracy
    :param x: the feature vector
    :param y: the target vector
    :param database_name: name of the data base used to populate the x and y vectors. It's only used to print the
    graphics with the accuracy report
    :return: a slice [layer_1_size, layer_2_size, accuracy] containing the size of the layers the yielded the model
    with the best accuracy along with the best accuracy value
    """
    # layer1_sizes = [20, 30]
    layer1_sizes = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

    momentum = 0.9
    learning_rate = 0.1

    # Score to store the accuracy for each configuration
    scores = []


    # 1 layer MLP
    # Use stratified K-fold to compute the accuracy for each model
    skf = StratifiedKFold(n_splits=10)
    mlp1_accs = []

    for layer1_size in layer1_sizes:
        model_description = "Layer 1 Size: %d" % layer1_size
        print("training model: %s" % (model_description))

        accs = []
        for train_index, test_index in skf.split(x, y):
            x_train, x_test = x[train_index], x[test_index]
            y_train, y_test = y[train_index], y[test_index]

            mlp = MLPClassifier(hidden_layer_sizes=(layer1_size), solver='sgd', momentum=momentum, tol=1e-4, max_iter=2000, random_state=1, learning_rate='adaptive', learning_rate_init=learning_rate)
            mlp.fit(x_train, y_train)
            accs.append(accuracy_score(y_test, mlp.predict(x_test)))


        acc = np.mean(accs)
        mlp1_accs.append(acc)
        scores.append([layer1_size, 0, acc])


    plt.figure(figsize=(15,10))
    plt.title("Variação da acurácia em relação ao tamanho da primeira camada para um MLP de uma camada", fontsize=16)
    plt.xlabel("Tamanho da primeira camada", fontsize=12)
    plt.ylabel("Acurácia", fontsize=12)

    plt.grid(True)
    plt.plot(layer1_sizes, mlp1_accs)

    # plt.show(True)
    plt.savefig("graphs/mlp_1_layer_accs.png")

    ## 2 Layers MLP
    layer1_sizes = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    layer2_sizes = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

    mlp2_accs = dict()

    for layer1_size in layer1_sizes:
        model_description = "Layer 1 Size: %d" % layer1_size
        layer1_accs = []
        for layer2_size in layer2_sizes:
            print("training model: %s, Layer 2 Size: %d" % (model_description, layer2_size))

            # Accuracy for a fixed layer 1 size, varying the size of the second layer
            accs = []
            for train_index, test_index in skf.split(x, y):
                x_train, x_test = x[train_index], x[test_index]
                y_train, y_test = y[train_index], y[test_index]

                mlp = MLPClassifier(hidden_layer_sizes=(layer1_size, layer2_size), solver='sgd', momentum=momentum, tol=1e-4,
                                    max_iter=2000, random_state=1, learning_rate='adaptive',
                                    learning_rate_init=learning_rate)
                mlp.fit(x_train, y_train)
                accs.append(accuracy_score(y_test, mlp.predict(x_test)))

            acc = np.mean(accs)
            layer1_accs.append(acc)
            scores.append([layer1_size, layer2_size, acc])

        mlp2_accs[model_description] = layer1_accs


    plt.figure(figsize=(15, 10))
    plt.title("Variação da acurácia em relação ao tamanho da segunda camada para um MLP de duas camadas", fontsize=16)
    plt.xlabel("Tamanho da segunda camada", fontsize=12)
    plt.ylabel("Acurácia", fontsize=12)

    for model_description, accs in mlp2_accs.items():
        plt.plot(layer2_sizes, accs, label=model_description)

    plt.legend()
    plt.grid(True)
    # plt.show(True)
    plt.savefig("graphs/mlp_2_layers_accs_new.png")

    df = pd.DataFrame(data=scores, columns=['Layer 1 size', 'Layer 2 size', 'Accuracy'])
    # print(df)
    df.to_csv("mlp_scores.csv")

    best_cfg = df.iloc[df['Accuracy'].idxmax()]

    return [int(best_cfg[0]), int(best_cfg[1]), best_cfg[2]]

def get_model_stats(x, y, model, model_name, database_name):
    """
    get_model_stats computes the confusion matrix, accuracy and precision for a given model
    :param x: the feature vector
    :param y: the target vector
    :param model: the model to get the stats from
    :param model_name: a model description to be used in the reports
    :param database_name: a data base description to be used in the reports
    :return: None
    """
    # Use stratified K-fold to compute the stats for each model
    skf = StratifiedKFold(n_splits=10)


    classes_number = len(np.unique(y))
    model_cm = np.zeros((classes_number, classes_number), dtype=int)
    classes_name = range(0, classes_number)

    accs = []
    precision = []
    for train_index, test_index in skf.split(x, y):
        x_train, x_test = x[train_index], x[test_index]
        y_train, y_test = y[train_index], y[test_index]

        model.fit(x_train, y_train)
        y_pred = model.predict(x_test)

        # Compute confusion matrix, accuracy and precision for this model
        model_cm += confusion_matrix(y_test, y_pred, classes_name)
        accs.append(accuracy_score(y_test, y_pred))
        precision.append(precision_score(y_test, y_pred, average='micro'))

    model_acc = np.mean(accs)
    model_precision = np.mean(precision)

    print("Database: %s, Modelo: %s" % (database_name, model_name))
    print("\tAcurácia: %.2f" % model_acc)
    print("\tPrecisão: %.2f" % model_precision)

    plt.figure(figsize=(15,10))
    plt.title("Matriz de Confusão para o modelo %s e database %s" % (model_name, database_name), fontsize=16)
    ax = sns.heatmap(model_cm, annot=True, cbar=False)
    ax.set(xlabel='Classe Predita', ylabel='Verdadeira Classe')
    # print(model_cm)
    # plt.show(True)
    plt.savefig("graphs/matriz_confusão_%s_%s" % (model_name, database_name))


def get_PCA(x):
    """
    get_PCA gets the principal components of the feature vector x that represent 50% of the data variance
    :param x: the feature vector
    :return: principal components that represent 50% of the data variance
    """

    # Increase the PCA dimension until we get 50% of the original data variance
    for n_components in range(1, len(x[0])):
        pca = PCA(n_components=n_components)
        pca.fit(x)

        if np.sum(pca.explained_variance_ratio_) > 0.5:
            print("PCA:")
            print("\tDimensão: ", n_components)
            print("\tVariância recuperada dos dados originais: %2.2f%%" % (np.sum(pca.explained_variance_ratio_)*100))
            return pca.transform(x)