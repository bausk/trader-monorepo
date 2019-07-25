from collections import OrderedDict

class ForwardOnceCache():
    def __init__(self, sort_field):
        self.buffer = OrderedDict()
        self.sort_field = sort_field

    def _sort(self, data):
        return sorted(data, key=lambda record: record[self.sort_field])

    def get_hash(self, datapoint):
        return datapoint[self.sort_field]

    def put(self, data):
        """
        Accepts rows of time-sortable data
        """
        if len(data) == 0:
            return []
        new_data = []
        sorted_data = self._sort(data)
        sorted_data_iterator = iter(sorted_data)
        earliest_data = next(sorted_data_iterator)
        earliest_timestamp = self.get_hash(earliest_data)
        new_buffer = OrderedDict()
        try:
            for timestamp in self.buffer:
                if timestamp < earliest_timestamp:
                    pass
                else:
                    while True:
                        if earliest_timestamp in self.buffer:
                            pass
                        else:
                            new_buffer[earliest_timestamp] = True
                            new_data.append(earliest_data)
                        earliest_data = next(sorted_data_iterator)
                        earliest_timestamp = self.get_hash(earliest_data)
                        if timestamp < earliest_timestamp:
                            break
            while True:
                new_buffer[earliest_timestamp] = True
                new_data.append(earliest_data)
                earliest_data = next(sorted_data_iterator)
                earliest_timestamp = self.get_hash(earliest_data)
        except StopIteration:
            pass
        self.buffer = new_buffer
        return new_data
