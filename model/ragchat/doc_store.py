from pymongo import MongoClient
from ragchat.configs import DEBUG

class DocStore:
    def __init__(self,ip='localhost',port=27017, 
                 db_name='docs', collection_name='pdf',
                 keys=['folder','file_name', 'page'],
                 debug=DEBUG
                ):
        self.ip=ip
        self.port=port
        self.db_name=db_name
        self.collection_name=collection_name
        self.keys=keys
        self.debug=debug
        if self.debug:
            #track attempts to insert
            self.insert_responses=[] 
            self.not_new=[]

    # def check_db(self,query):
    #     client = MongoClient(f'{self.ip}:{self.port}')
    #     db=self.client[self.db_name]
    #     coll=db[self.collection_name]
        
        
    def add_to_db(self,things):
        client = MongoClient(f'{self.ip}:{self.port}')
        db=self.client[self.db_name]
        coll=db[self.collection_name]
        not_new=[]
        new=[]
        for thing in things:
            find_dict={key:thing[key] for key in self.keys}
            if len(list(coll.find(find_dict)))>0:
                not_new.append(thing)
            else:
                new.append(thing)  
        response=coll.insert_many(new)
        if self.debug:
            self.insert_responses.append(response)
            self.not_new.append(not_new)
        client.close()
        return

    def yield_from_db(self, query={}, chunk_size=10):
        client = MongoClient(f'{self.ip}:{self.port}')
        db=self.client[self.db_name]
        coll=db[self.collection_name]
        n_docs = coll.count_documents(query)
        n_chunks=-(-n_docs//chunk_size)
        for i in range(n_chunks):
            yield coll.find(query)[i*chunk_size:(i+1)*chunk_size]
        client.close()
        return


        

        
            
            