import argparse
import pathlib
import re
import os

import numpy as np
import tensorflow as tf
from tcn import TCN, tcn_full_summary

from scipy.fft import fft
from scipy.signal import lfilter

target = []

def moving_average(arr, N):
    return lfilter(np.ones(N)/N, [1], arr)

def load_file(path):
    arr = np.load(path, allow_pickle=True)
    norm = np.linalg.norm(arr)
    arr = arr/norm
    arr = moving_average(arr, 5)
    if arr.size>230400:
        arr = arr[:230400]
    split = np.split(arr, 40)
    return [np.reshape(fft(s), (1, 45, 128)) for s in split]
def load_files(path):
    file_name_regex = re.compile("^(.*_SIG_II)\.npy$")
    data = {}
    max_filename_length = 0
    for entry in os.scandir(path):
        match = file_name_regex.match(entry.name)
        if entry.is_dir():
            for file in os.scandir(entry.path):
                match = file_name_regex.match(file.name)
                if match and file.is_file():
                    max_filename_length = max(max_filename_length, len(match.groups()[0]))
                    data[match.groups()[0]] = load_file(file.path)
        elif match and entry.is_file():
            max_filename_length = max(max_filename_length, len(match.groups()[0]))
            data[match.groups()[0]] = load_file(entry.path)
    return data, max_filename_length

def load_model(path):
    model = tf.keras.models.Sequential([
        TCN(input_shape=(45,128), kernel_size=3, use_skip_connections=True, nb_filters=64, dilations=[1,2,4,8], return_sequences=True, use_batch_norm=True, dropout_rate=0.05),
        TCN(kernel_size=3, use_skip_connections=True, nb_filters=16, dilations=[1,2,4,8], use_batch_norm=True, dropout_rate=0.05),
        tf.keras.layers.Dense(32, activation="linear"),
        tf.keras.layers.Dense(96, activation="linear"),
        tf.keras.layers.Dense(199, activation="softmax")
    ])
    model.compile(loss="categorical_crossentropy", optimizer="adam")
    model.load_weights(path)
    return model

def check_file(model, data, certainty=0.1):
    global target
    result = []
    for element in data:
        prediction = model.predict(element)
        if len(target)==0:
            target = prediction
        diff = np.sum(np.abs(prediction - target))
        result.append(diff<certainty)
    return result


def main(model_path, data_path, certainty=0.5):
    model = load_model(model_path)
    data, width = load_files(data_path)
    results = []
    for filename, element in data.items():
        result = check_file(model, element, certainty)
        print(f"results for {filename: <{width}}: {result}")
        results.append(any(result))
    print(f"total number of matches found: {sum(results)}")
    
if __name__=="__main__":
    parser = argparse.ArgumentParser(
        description="""This demo takes a path to a folder with data files (in .npy\
                    format) with ecg records and weights from trained model. \
                    For each file it returns information if the ecg belongs to the\
                    person it was trained on (here - I16 from Physionet 2-lead\
                    ecg database)"""
    )
    parser.add_argument(
        "-m",
        "--model",
        default=".\model.h5",
        required=True,
        dest="model",
        type=pathlib.Path,
        help="path to saved model from which the program will load weights"
    )
    parser.add_argument(
        "-d",
        "--data",
        default=".\data",
        required=True,
        dest="data",
        type=pathlib.Path,
        help="path to a folder with data in .npy format"
    )
    parser.add_argument(
        "-c",
        "--certainty",
        default=0.1,
        dest="certainty",
        type=float,
        help="""certainty required to consider a record as belonging to the targ\
                et. Increasing it will decrease the number of false positives, but \
                increase false negatives."""
    )

    args = parser.parse_args(["-m=../input/ecg-biometrics/checkpoints/model.h5", "-d=../input/ecg-lead-2-dataset-physionet-open-access/db_npy/incartdb_npy"])
    main(str(args.model), str(args.data), float(args.certainty))
