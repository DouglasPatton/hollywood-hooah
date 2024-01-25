from ragchat.configs import DEBUG, REFERENCE_FOLDER, DB_NAME, COLLECTION_NAME
from ragchat.doc_store import DocStore

import os
import re
from multiprocessing import Process,Queue
from time import time,sleep
import numpy as np
import pandas as pd
import logging,logging.handlers

class MpLogger:
    def __init__(self,name=None):
        if name is None:
            name='pdf_reader.log'
        else:
            if name[-4:]!='.log':
                name+='.log'
        logdir=os.path.join(os.getcwd(),'log'); 
        if not os.path.exists(logdir):os.mkdir(logdir)
        handlername=os.path.join(logdir,name)
        logging.basicConfig(
            handlers=[logging.handlers.RotatingFileHandler(handlername, maxBytes=10**7, backupCount=100)],
            level=logging.INFO,
            format="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
            datefmt='%Y-%m-%dT%H:%M:%S')
        self.logger = logging.getLogger(handlername)
        
class MpWrapper(Process,MpLogger):
    def __init__(self,q,jobq,run_object):#,pass_args=[],pass_kwargs={}):
        super().__init__()
        self.q=q;
        self.jobq=jobq
        #self.i=i
        self.run_object=run_object
        #self.pass_args=pass_args
        #self.pass_kwargs=pass_kwargs
        
    def run(self):
        MpLogger.__init__(self,'mpwrapper.log')
        while True:
            job=self.jobq.get()
            if type(job) is str: break
            the_obj=self.run_object(*job['args'],**job['kwargs'])
            the_obj.run()
            self.q.put((job['i'],the_obj))

            
class MpHelper(MpLogger):   
    def __init__(self):
        MpLogger.__init__(self,name='mphelper.log')
        
            
    def runAsMultiProc(self,mp_object,args_list,proc_count=12,kwargs_list={},drop_output=True):
        try:
            starttime=time()
            I=len(args_list)
            if type(kwargs_list) is dict:
                kwargs_list=[kwargs_list]*I
            if proc_count==1:
                self.logger.info(f'proc_count: {proc_count}, so no mp for obj type: {type(mp_object)}')
                outlist=[]
                for i in range(I):
                    outlist.append(mp_object(*args_list[i],**kwargs_list[i]))
                    outlist[-1].run()
                return outlist
            
            q=Queue()
            jobq=Queue()
            
            
            #q_args_list=[[q,i,*args_list[i]] for i in range(I)]
            for i in range(I):
                jobq.put({'i':i,'args':args_list[i],'kwargs':kwargs_list[i]})
            #i_todo_list=list(range(I))
            outlist=['empty' for _ in range(I)]
            procs=[]
            for _ in range(proc_count):
                procs.append(MpWrapper(q,jobq,mp_object))
                procs[-1].start()
            countdown=I
        except:
            self.logger.exception('error in runasmultiproc')
            assert False,'unexpected error'
        pct_complete=0
        check_count=0
        while countdown:
            try:
                check_count+=1
                if check_count%5==0:
                    self.logger.info(f'multiproc checking q. countdown:{countdown}')
                try:
                    i,result=q.get(True,20)
                    check_count=0
                except:
                    if not q.empty():
                        self.logger.exception(f'q not empty, but error encountered ')
                    continue
                self.logger.info(f'multiproc has something from the q!')
                if drop_output:
                    outlist[i]=None
                else:
                    outlist[i]=result
                countdown-=1
                completion=100*(I-countdown)/I
                if completion-pct_complete>10:
                    pct_complete=completion
                    self.logger.info(f'{pct_complete}%')
                '''procs[i].terminate()
                procs[i].join()
                if i_todo_list: #start the next process
                    ii=i_todo_list.pop(-1)
                    procs[ii]=MpWrapper(
                        q,ii,mp_object,
                        pass_args=args_list[ii],pass_kwargs=kwargs_list[ii])
                    procs[ii].start()
                '''
                self.logger.info(f'proc completed. countdown:{countdown}')
            except:
                #self.logger.exception('error')
                self.logger.exception('unexpected error')
                assert False, 'halt'
        [jobq.put('close') for _ in procs]
        [proc.join() for proc in procs]
        q.close()
        jobq.close()                             
        self.logger.info(f'all procs joined sucessfully')
        endtime=time()
        self.logger.info(f'pool complete at {endtime}, time elapsed: {(endtime-starttime)/60} minutes')
        return outlist
    