class MinHeap:
    
    def __init__(self):
        self.heap = []
    
    def parent(self, i):
        return (i - 1) // 2
    
    def left_child(self, i):
        return 2 * i + 1
    
    def right_child(self, i):
        return 2 * i + 2
    
    def get_min(self):
        if len(self.heap) > 0:
            return self.heap[0]
        return None
    
    def extract_min(self):
        if len(self.heap) == 0:
            return None
        
        min_element = self.heap[0]
        
        
        last_element = self.heap.pop()
        if len(self.heap) > 0:
            self.heap[0] = last_element
            self._heapify_down(0)
        
        return min_element
    
    def insert(self, element):
        self.heap.append(element)
        self._heapify_up(len(self.heap) - 1)
    
    def _heapify_up(self, i):
        
        current = self.heap[i]
        current_priority = self._get_priority_key(current)
        
        
        while i > 0:
            parent_idx = self.parent(i)
            parent = self.heap[parent_idx]
            parent_priority = self._get_priority_key(parent)
            
            if current_priority >= parent_priority:
                break
            
            
            self.heap[i], self.heap[parent_idx] = self.heap[parent_idx], self.heap[i]
            i = parent_idx
    
    def _heapify_down(self, i):
        smallest = i
        left = self.left_child(i)
        right = self.right_child(i)
        heap_size = len(self.heap)
        
        
        if left < heap_size and self._get_priority_key(self.heap[left]) < self._get_priority_key(self.heap[smallest]):
            smallest = left
        
        
        if right < heap_size and self._get_priority_key(self.heap[right]) < self._get_priority_key(self.heap[smallest]):
            smallest = right
        
        
        if smallest != i:
            self.heap[i], self.heap[smallest] = self.heap[smallest], self.heap[i]
            self._heapify_down(smallest)
    
    def _get_priority_key(self, element):
        if isinstance(element, dict):
            priority_value = element.get('priority', 999)  
            date_value = element.get('date', '9999-12-31')  
            time_value = element.get('time', '23:59')  
            
            
            return (priority_value, date_value, time_value)
        
        
        return element
    
    def heapify(self, array):
        self.heap = array.copy()
        
        
        for i in range(len(self.heap) // 2, -1, -1):
            self._heapify_down(i)
    
    def size(self):
        return len(self.heap)
    
    def is_empty(self):
        return len(self.heap) == 0
    
    def get_all(self):
        return self.heap
    
    def get_all_sorted(self):
        
        temp_heap = MinHeap()
        temp_heap.heapify(self.heap)
        
        sorted_elements = []
        while not temp_heap.is_empty():
            sorted_elements.append(temp_heap.extract_min())
        
        return sorted_elements
