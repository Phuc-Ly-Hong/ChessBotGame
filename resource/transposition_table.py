class TTEntry:
    def __init__(self, depth, score, flag):
        self.depth = depth
        self.score = score
        self.flag = flag  # 'EXACT', 'LOWERBOUND', 'UPPERBOUND'

class TranspositionTable:
    def __init__(self):
        self.table = {}

    def store(self, key, entry):
        self.table[key] = entry

    def lookup(self, key, depth, alpha, beta):
        entry = self.table.get(key)
        if entry and entry.depth >= depth:
            if entry.flag == 'EXACT':
                return entry.score
            elif entry.flag == 'LOWERBOUND' and entry.score > alpha:
                return entry.score
            elif entry.flag == 'UPPERBOUND' and entry.score < beta:
                return entry.score
        return None
