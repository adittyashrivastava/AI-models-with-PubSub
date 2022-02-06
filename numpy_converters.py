import numpy as np
from json import JSONEncoder, dumps, loads

#Creating a seperate numpy encoder file to enable conversion
#of Numpy Arrays to JSON Serialized objects
class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)

# Serialization
def serialization(numpy_array):
    numpy_data = {"array": numpy_array}
    encoded_numpy_data = dumps(numpy_data, cls=NumpyArrayEncoder)
    return encoded_numpy_data

# Deserialization
def deserialization(encoded_numpy_data):
    decoded_array = loads(encoded_numpy_data)
    final_numpy_array = np.asarray(decoded_array["array"])
    return final_numpy_array
