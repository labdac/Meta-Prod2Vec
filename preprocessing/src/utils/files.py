import pickle


def save_to_pickle(a, file_name: str):
    with open(file_name, 'wb') as handle:
        pickle.dump(a, handle, protocol=pickle.HIGHEST_PROTOCOL)

        
def read_from_pickle(file_name: str):
    with open(file_name, 'rb') as handle:
        return pickle.load(handle)

