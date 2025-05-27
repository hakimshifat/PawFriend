class HashTable:
    
    def __init__(self, size=1024):
        self.size = size
        self.table = [[] for _ in range(size)]
        self.length = 0
    
    def _hash(self, key):
        if isinstance(key, str):
            
            hash_value = 0
            for char in key:
                hash_value += ord(char)
            return hash_value % self.size
        elif isinstance(key, int):
            
            return key % self.size
        else:
            
            return self._hash(str(key))
    
    def insert(self, key, value):
        index = self._hash(key)
        
        
        for i, (k, v) in enumerate(self.table[index]):
            if k == key:
                self.table[index][i] = (key, value)
                return True
        
        
        self.table[index].append((key, value))
        self.length += 1
        return True
    
    def get(self, key, default=None):
        index = self._hash(key)
        
        for k, v in self.table[index]:
            if k == key:
                return v
        
        return default
    
    def delete(self, key):
        index = self._hash(key)
        
        for i, (k, v) in enumerate(self.table[index]):
            if k == key:
                del self.table[index][i]
                self.length -= 1
                return True
        
        return False
    
    def contains(self, key):
        index = self._hash(key)
        
        for k, _ in self.table[index]:
            if k == key:
                return True
        
        return False
    
    def keys(self):
        all_keys = []
        for bucket in self.table:
            for k, _ in bucket:
                all_keys.append(k)
        return all_keys
    
    def values(self):
        all_values = []
        for bucket in self.table:
            for _, v in bucket:
                all_values.append(v)
        return all_values
    
    def items(self):
        all_items = []
        for bucket in self.table:
            all_items.extend(bucket)
        return all_items
    
    def clear(self):
        self.table = [[] for _ in range(self.size)]
        self.length = 0
    
    def __len__(self):
        return self.length
    
    def __str__(self):
        return str(dict(self.items()))
    
    def __contains__(self, key):
        return self.contains(key)
