import random
import time

class Simulation:
    def __init__(self, treetype, key_size = 4, data_record_size = 100, index_pointer_size = 8,
                 data_pointer_size = 10, block_size = 100,
                 read_percent = 0.5, insert_percent = 0.3, delete_percent = 0.2,
                 steps = 1000, coalesce = True):
        self.key_size = key_size
        self.data_record_size = data_record_size
        self.index_pointer_size = index_pointer_size
        self.data_pointer_size = data_pointer_size
        self.block_size = block_size
        self.read_percent= read_percent
        self.insert_percent = insert_percent
        self.delete_percent = delete_percent
        self.steps = steps
        self.coalesce = coalesce
        self.treetype = treetype
        self.tree = treetype(key_size, data_record_size, index_pointer_size,
                             data_record_size, block_size, coalesce)
        assert read_percent + insert_percent + delete_percent == 1.0

    def alter_parameters(self, **kwargs):
        for k,v in kwargs.items():
            if hasattr(self, k):
                setattr(self, k, v)
                print "setting " + str(k) + " to " + str(v)
            else:
                raise Exception(str(k) + "not in parameters")
        if "insert_percent" in kwargs or "delete_percent" in kwargs or "insert_percent" in kwargs:
            assert self.read_percent + self.insert_percent + self.delete_percent == 1.0

    def execute_insert(self, to_insert):
        print "inserting " + str(to_insert)
        self.tree.insert(to_insert)

    def execute_read(self, to_read):
        print "reading " + str(to_read)
        self.tree.lookup(to_read)

    def execute_delete(self, to_delete):
        print "deleting " + str(to_delete)
        self.tree.delete(to_delete)

    def run(self):
        root = self.treetype(self.key_size, self.data_record_size, self.index_pointer_size,
                             self.data_record_size, self.block_size, self.coalesce)
        t1 = time.clock()
        for idx in range(self.steps):
            r = random.random()
            if (r < self.read_percent):
                self.execute_read(random.choice(range(1,1000)))
            elif (r < self.read_percent + self.insert_percent):
                self.execute_insert(random.choice(range(1,1000)))
            else:
                self.execute_delete(random.choice(range(1,1000)))
        t2 = time.clock()
        print t2, t1, t2 - t1
        
if __name__ == "__main__":
    from BPlus import BPTree
    Simulation(BPTree).run()
