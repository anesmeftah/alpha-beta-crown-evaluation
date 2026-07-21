import pandas as pd

columns = [
    "benchmark",
    "onnx_path",
    "vnnlib_path",
    "total_time",
    "result",
    "solver_time",
]

results = pd.read_csv('data/official/a-b-CROWN.csv' , names=columns)

benchmarks = ['cifar10_resnet' , 'cifar2020']


cifar2020 = results[results.benchmark == benchmarks[1]].copy()
cifar10 = results[results.benchmark == benchmarks[0]].copy()

cifar2020.to_csv('data/official/cifar2020.csv', index=False)
cifar10.to_csv('data/official/cifar10.csv', index=False)


