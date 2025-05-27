# utils/decode.py

import numpy as np
from config.constants import chars

def fastdecode(y_pred):
    results = ""
    confidence = 0.0
    table_pred = y_pred.reshape(-1, len(chars)+1)
    res = table_pred.argmax(axis=1)
    for i, one in enumerate(res):
        if one < len(chars):
            results += chars[one]
            confidence += table_pred[i][one]
    confidence /= len(results)
    return results, confidence
