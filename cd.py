import json
import numpy as np
with open('simulations.json', 'r') as f:
    all_simulations = json.load(f)

activos_finales = {
    'IXC': 0.0444,
    'XLE': 0.0563,
    'CAR': 0.2334,
    'AMZN': 0.1735,
    'BHVN': 0.2340,
    'HTZ': 0.1890,
    'CVX': 0.0354,
    'AMX': 0.0141,
    'SI=F': 0.0100,
    'HG=F': 0.0100
}

af = ['IXC', 'XLE', 'CAR', 'AMZN', 'BHVN']
af2 = ['HTZ', 'CVX', 'AMX', 'SI=F', 'HG=F']

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

all_simulations1 = {k: v for k, v in all_simulations.items() if k in af}
all_simulations2 = {k: v for k, v in all_simulations.items() if k in af2}


with open('simulations1.json', 'w') as archivo_json:
    json.dump(all_simulations1, archivo_json)


with open('simulations2.json', 'w') as archivo_json:
    json.dump(all_simulations2, archivo_json)