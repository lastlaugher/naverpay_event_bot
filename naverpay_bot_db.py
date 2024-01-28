import pickle
import os
from dataclasses import dataclass

@dataclass
class NaverPayBotProperties:
    id = ''
    pw = ''
    once_event_schedule = ''
    daily_event_list = []

class NaverPayBotDB:
    def __init__(self):
        self.properties = NaverPayBotProperties()
        self.filename = 'naverpaybotdb.pickle'
    
    def save(self):
        pickle.dump(self.properties, open(self.filename, 'wb'))
    
    def load(self):
        if os.path.exists(self.filename):
            self.properties = pickle.load(open(self.filename, 'rb'))
            return True
        else:
            return False
