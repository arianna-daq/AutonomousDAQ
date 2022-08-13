import numpy as np

# Not Supposed to be Set should come from config file
fDac = np.array([[21488, 25681], [21488, 25681], [21488, 25681],
                 [21488, 25681], [21488, 25681], [21488, 25681],
                 [21488, 25681], [21488, 25681]])



def GetDac(ch, dc):
    return fDac[ch][dc]