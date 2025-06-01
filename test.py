class LiveValue:
    def __init__(self, source, key):
        self._source = source
        self._key = key

    def key(self):
        return self._key

    @property
    def value(self):
        return self._source[self._key]

    @value.setter
    def value(self, val):
        self._source[self._key] = val

    def __repr__(self):
        return f"{self._key}: {self.value}"
        
    def __str__(self):
        return f"{self._key}: {self.value}"

class LiveCopy:
    def __init__(self, source, index_map):
        self.source = source
        self.index_map = index_map

    def __getitem__(self, key):
        src_key = self.index_map[key]
        return LiveValue(self.source, src_key)

    def keys(self):
        return self.index_map.keys()

    def values(self):
        return [{self[k]} for k in self.index_map]

    def items(self):
        return [(k, {self[k]}) for k in self.index_map]

    def __iter__(self):
        return iter(self.index_map)

    def __len__(self):
        return len(self.index_map)
        
    def __repr__(self):
        return f"{self._key}: {self.value}"
    
    def __str__(self):
        return f"{self._key}: {self.value}"
        
    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

original = {
    'preset': 'default',
    'text_case': 'title',
    'text_formats': '',
    'icon': '',
    'color_code': 7,
    'color_theme': 'dark',
    'indent_count': 1
}

y = {
    'preset': {'default': 0},
    'text_case': {'title': 1}
}

index_map = { ''.join([k[0] for k in key.split('_')]): key for key in original }
copy = LiveCopy(original, index_map)

# print("LiveCopy items:")
# for k, v in copy.items():
    # print(f"{k}: {v}")

# print("\nUpdate 'cc':")
# copy['cc'] = 99
# print("Updated original:", original['color_code'])  # 99

# for k, v in copy.items():
    # print(f"{k}: {v}")

print(copy.items())
# print(copy)
# print(original.values())
print(y.items())




