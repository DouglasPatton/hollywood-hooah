from pymongo import MongoClient
from ragchat.configs import DEBUG, DB_NAME, COLLECTION_NAME, KEYS
from random import seed,shuffle

class DocStore:
    def __init__(self,
                 ip='localhost',
                 # ip='172.18.0.2',
                 port=27017, 
                 db_name=DB_NAME, collection_name=COLLECTION_NAME,
                 keys=KEYS,
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
    def get_client_collection(self):
        client = MongoClient(f'{self.ip}:{self.port}')
        db=client[self.db_name]
        coll=db[self.collection_name]
        return client, coll

    def retrieve_random(self,n=10):
        cli,coll = self.get_client_collection()
        a=list(coll.find({},'_id'))
        seed(n)
        shuffle(a)
        b=[a_['_id'] for a_ in a[:5]]
        results=list(coll.find({"_id": {"$in": b}}))
        cli.close()
        return results
        
        
    def add_to_db(self,things):
        if len(things)==0: return
        client = MongoClient(f'{self.ip}:{self.port}')
        db=client[self.db_name]
        coll=db[self.collection_name]
        not_new=[]
        new=[]
        for thing in things:
            find_dict={key:thing[key] for key in self.keys}
            if len(list(coll.find(find_dict)))>0:
                not_new.append(thing)
            else:
                new.append(thing)  
        if len(new)>0:
            response=coll.insert_many(new)
        else:
            response=f'na b/c nothing new'
        if self.debug:
            self.insert_responses.append(response)
            self.not_new.append(not_new)
        client.close()
        return

    def yield_from_db(self, query={},projection={}, chunk_size=10):
        client = MongoClient(f'{self.ip}:{self.port}')
        db=client[self.db_name]
        coll=db[self.collection_name]
        n_docs = coll.count_documents(query)
        if chunk_size is None:
            n_chunks=1
            chunk_size=n_docs
        else:
            n_chunks=-(-n_docs//chunk_size)
        for i in range(n_chunks):
            yield [dict(q) for q in coll.find(query, projection)[i*chunk_size:(i+1)*chunk_size]]
        client.close()
        return


        

        
            
            