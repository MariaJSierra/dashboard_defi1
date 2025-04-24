import json
import numpy as np
with open('simulations.json', 'r') as f:
    all_simulations = json.load(f)

activos_finales = {'IXC': 1.030091e-01, 
                   'XRT': 4.725578e-02, 
                   'CAR': 2.218685e-01, 
                   'AMZN': 1.665052e-01, 
                   'BHVN': 2.224662e-01, 
                   'HTZ': 1.807907e-01, 
                   'CVX': 3.891293e-02, 
                   'AMX': 1.919165e-02, 
                   'GC=F': 0.000000e+00, 
                   'HG=F': 2.775558e-17
}
af = ['IXC', 'XRT', 'CAR', 'AMZN', 'BHVN']
af2 = ['HTZ', 'CVX', 'AMX', 'GC=F', 'HG=F']

def convertir_a_ndarray(obj):
    if isinstance(obj, list):
        try:
            return np.array(obj).tolist()
        except:
            return [convertir_a_ndarray(i) for i in obj]
    if isinstance(obj, dict):
        return {k: convertir_a_ndarray(v) for k, v in obj.items()}
    return obj

all_simulations = convertir_a_ndarray(all_simulations)
for a, b in all_simulations.items():
    print(type(b))
all_simulations1 = {k: v for k, v in all_simulations.items() if k in af}
all_simulations2 = {k: v for k, v in all_simulations.items() if k in af2}


with open('simulations1.json', 'w') as archivo_json:
    json.dump(all_simulations1, archivo_json)


with open('simulations2.json', 'w') as archivo_json:
    json.dump(all_simulations2, archivo_json)