class Queue:
    
    def __init__(self):
        self.items = []
    
    def enqueue(self, item):
        self.items.append(item)
    
    def dequeue(self):
        if self.is_empty():
            return None
        return self.items.pop(0)
    
    def peek(self):
        if self.is_empty():
            return None
        return self.items[0]
    
    def is_empty(self):
        return len(self.items) == 0
    
    def size(self):
        return len(self.items)
    
    def get_all(self):
        return self.items
    
    def clear(self):
        self.items = []
    
    def sort_by_date(self):
        self.items.sort(key=lambda x: x.get('date', '9999-12-31'))
        
    def filter_by_completion(self, completed=False):
        filtered_queue = Queue()
        for item in self.items:
            if item.get('completed', False) == completed:
                filtered_queue.enqueue(item)
        return filtered_queue
    
    def get_upcoming(self, days=7, reference_date=None):
        import datetime
        
        if reference_date is None:
            reference_date = datetime.datetime.now().date()
        elif isinstance(reference_date, str):
            
            reference_date = datetime.datetime.strptime(reference_date, "%Y-%m-%d").date()
        
        upcoming_queue = Queue()
        
        for item in self.items:
            
            if item.get('completed', False):
                continue
                
            
            try:
                item_date = datetime.datetime.strptime(item.get('date', '9999-12-31'), "%Y-%m-%d").date()
                
                
                delta = (item_date - reference_date).days
                
                
                if 0 <= delta <= days:
                    upcoming_queue.enqueue(item)
            except (ValueError, TypeError):
                
                continue
        
        
        upcoming_queue.sort_by_date()
        
        return upcoming_queue
