import pandas as pd

class Colecao:
    def __init__(self, objs):
        self.collection = [arg for arg in objs]

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index < len(self.collection):
            obj = self.collection[self._index]
            self._index += 1
            return obj
        else:
            raise StopIteration

    def iterrows(self):
        for index, obj in enumerate(self.collection):
            yield index, obj

    def to_dataframe(self):
        data = []
        for obj in self.collection:
            data.append(obj.to_dict())
        return pd.DataFrame(data)

    def __len__(self):
        return len(self.collection)

    def is_empty(self):
        return len(self.collection) == 0    