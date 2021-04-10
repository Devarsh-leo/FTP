class Que():
    def __init__(self):
        self.q_list = list()
    def push(self,obj):
        self.q_list.append(obj)
    def pop(self):
        if len(self.q_list) >0:
            ret = self.q_list[0]
            del self.q_list[0]
            return ret
        else:
            return False
    def count(self):
        return len(self.q_list)
    def seek(self):
        if len(self.q_list) >0:
            ret = self.q_list[0]
            return ret
        else:
            return False