import math
import numpy as np
import statsmodels.api as sm
import pandas as pd
import matplotlib.pyplot as plt

class NSCurveFamily:
    def __init__(self,tau0=1,beta0=1,beta1=1,beta2=1):
        self.tau0 = tau0
        self.beta0 = beta0
        self.beta1 = beta1
        self.beta2 = beta2

    def fitNSModel(self, tau, t_seq, zr_seq):
        t_to_tau = [ t/tau  for t in t_seq] 
        xterm1 = [ (1.0-math.exp(-tt))/tt for tt in t_to_tau]
        xterm2 = [ (1.0-math.exp(-tt))/tt-math.exp(-tt) for tt in t_to_tau]
        x = np.array([xterm1, xterm2]).T
        x = sm.add_constant(x)
        wt=np.append(t_seq[0],np.diff(t_seq))   
        res = sm.WLS(zr_seq, x, wt).fit()
        return (res.params, res.rsquared)    
         
    def estNSParam(self, t_seq, zr_seq):
        tau_univ = [0.1, 0.15, 0.2, 0.3, 0.5, 0.75, 1, 1.5, 2, 3, 5, 7.5, 10]
        rsq_univ = [ self.fitNSModel(tau, t_seq, zr_seq)[1] for tau in tau_univ]
        opt_tau = tau_univ[np.argmax(rsq_univ)]
        opt_param, opt_rsqr = self.fitNSModel(opt_tau, t_seq, zr_seq)
        return (opt_param, opt_tau, opt_rsqr)

    def estimateParam(self, t_seq, zr_seq):    
        param, tau, rsqr = self.estNSParam(t_seq, zr_seq)
        self.beta0, self.beta1, self.beta2=param
        self.tau0, self.rsqr = tau, rsqr
        
    def getSpot(self, t_seq):
        t_to_tau = [ t/self.tau0  for t in t_seq]
        xterm1 = [ (1.0-math.exp(-tt))/tt for tt in t_to_tau]
        xterm2 = [ (1.0-math.exp(-tt))/tt-math.exp(-tt) for tt in t_to_tau]
        param = [self.beta0, self.beta1, self.beta2]
        x = np.array([xterm1, xterm2]).T
        x = sm.add_constant(x)
        return x.dot(param)
        
    def getFwdRate(self, t_seq): 
        t_to_tau = [ t/self.tau0  for t in t_seq]
        xterm1 = [ math.exp(-tt) for tt in t_to_tau]
        xterm2 = [ tt*math.exp(-tt) for tt in t_to_tau]
        param = [self.beta0, self.beta1, self.beta2]
        x = np.array([xterm1, xterm2]).T
        x = sm.add_constant(x)
        return x.dot(param)  

def getData(dataName="test"):
    if dataName=="test":
        testIndex = [0.25,0.333,0.417,0.5,0.75,1,1.5,2,3,4,5,6,7,8,9,10,12,15,17,20,25,30]
        testYield =  [-0.602,-0.6059,-0.6096,-0.613,-0.6215,-0.6279,-0.6341,-0.6327,-0.6106,-0.5694,-0.5161,-0.456,
                      -0.3932,-0.3305,-0.2698,-0.2123,-0.1091,0.0159,0.0818,0.1601,0.2524,0.315]
        return [[testIndex,testYield]]
    else:
        data = pd.read_excel(dataName)
        data = data.iloc[:]
        tIndex = np.array([round(1/12,3),round(1/6,3),1/4,1/2,1,2,3,5,7,10,20,30])
        rows = data.shape[0]
        totalData = [ [tIndex,np.array(data.loc[i][1:].values,dtype="float")] for i in range(rows)]
        return totalData

def runOne(rowNum,dataName):
    tindex,yields = getData(dataName)[rowNum]
    nsm = NSCurveFamily()
    nsm.estimateParam(tindex,yields)
    spots = nsm.getSpot(tindex)
    return nsm.tau0, nsm.beta0, nsm.beta1, nsm.beta2, tindex, yields, spots, rsquare(yields,spots)

def rsquare(y1List,y2List):
    sums = 0
    for i in range(len(y1List)):
        sums += (y2List[i]-y1List[i])**2
    return sums

def trainData(filename):
    df = pd.read_excel(filename)
    df_tail = df.tail(1)[['1 Mo','2 Mo','3 Mo','6 Mo','1 Yr','2 Yr','3 Yr','5 Yr','7 Yr','10 Yr','20 Yr','30 Yr']].values[0]
    rows = df.shape[0]-1
    avgDict = {'t':[],'b0':[],'b1':[],'b2':[]}
    avgDict_Max = {}
    avgDict_Min = {}
    tIndex = np.array([round(1/12,3),round(1/6,3),1/4,1/2,1,2,3,5,7,10,20,30])

    for i in range(rows):
        t,b0,b1,b2, x, y_real, y, rs = runOne(i,filename)
        avgDict.get('t',[]).append(t)
        avgDict.get('b0',[]).append(b0)
        avgDict.get('b1',[]).append(b1)
        avgDict.get('b2',[]).append(b2)

    for k,v in avgDict.items():
        avgDict_Max[k] = np.max(v)
        avgDict_Min[k] = np.min(v)
    
    return avgDict_Min,avgDict_Max,tIndex,df_tail

def adjustParameters(avgDict_Min,avgDict_Max,tIndex,df_tail):
    tempBest = 100
    paras = []
    for i in np.arange(avgDict_Min['t'],avgDict_Max['t'],0.1):
        for j in np.arange(avgDict_Min['b0'],avgDict_Max['b0'],0.1):
            for k in np.arange(avgDict_Min['b1'],avgDict_Max['b1'],0.1):
                for l in np.arange(avgDict_Min['b2'],avgDict_Max['b2'],0.1):
                    nsm = NSCurveFamily(i,j,k,l)
                    rst = rsquare(nsm.getSpot(tIndex),df_tail)
                    if rst<tempBest:
                        tempBest = rst
                        paras = [i,j,k,l]
    return tempBest,paras

def runData(filename,env="developing",paras=""):
    if not paras:
        avgDict_Min,avgDict_Max,tIndex,df_tail = trainData(filename)
        tempBest,paras = adjustParameters(avgDict_Min,avgDict_Max,tIndex,df_tail)
        nsm = NSCurveFamily(*paras)
    else:
        tIndex = np.array([round(1/12,3),round(1/6,3),1/4,1/2,1,2,3,5,7,10,20,30])
        df = pd.read_excel(filename)
        df_tail = df.tail(1)[['1 Mo','2 Mo','3 Mo','6 Mo','1 Yr','2 Yr','3 Yr','5 Yr','7 Yr','10 Yr','20 Yr','30 Yr']].values[0]
        nsm = NSCurveFamily(*paras)
        tempBest = rsquare(nsm.getSpot(tIndex),df_tail)
    if env=="developing":
        print(tempBest,"t-b0-b1-b2",paras)
        plotNSmodel(tIndex,nsm,df_tail)
    else:
        return tempBest,paras,tIndex,nsm.getSpot(tIndex),df_tail

def postOne(filename,params,row):
    params = [ float(i) for i in params]
    tIndex = np.array([round(1/12,3),round(1/6,3),1/4,1/2,1,2,3,5,7,10,20,30])
    df = pd.read_excel(filename)
    df_tail = df.iloc[row][['1 Mo','2 Mo','3 Mo','6 Mo','1 Yr','2 Yr','3 Yr','5 Yr','7 Yr','10 Yr','20 Yr','30 Yr']].values
    nsm = NSCurveFamily(*params)
    tempBest = rsquare(nsm.getSpot(tIndex),df_tail)
    return tempBest,params,tIndex,nsm.getSpot(tIndex),df_tail