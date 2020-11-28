import math
import numpy as np
import statsmodels.api as sm
import pandas as pd
import matplotlib.pyplot as plt
import os

class NSCurveFamily:
    def __init__(self):
        self.HasEstParam = False

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
        self.HasEstParam=True
        
    def getSpot(self, t_seq):
        if self.HasEstParam == False:
            raise Exception('Parameters are not available')
        t_to_tau = [ t/self.tau0  for t in t_seq]
        xterm1 = [ (1.0-math.exp(-tt))/tt for tt in t_to_tau]
        xterm2 = [ (1.0-math.exp(-tt))/tt-math.exp(-tt) for tt in t_to_tau]
        param = [self.beta0, self.beta1, self.beta2]
        x = np.array([xterm1, xterm2]).T
        x = sm.add_constant(x)
        return x.dot(param)
        
    def getFwdRate(self, t_seq):
        if self.HasEstParam == False:
            raise Exception('Parameters are not available')
        t_to_tau = [ t/self.tau0  for t in t_seq]
        xterm1 = [ math.exp(-tt) for tt in t_to_tau]
        xterm2 = [ tt*math.exp(-tt) for tt in t_to_tau]
        param = [self.beta0, self.beta1, self.beta2]
        x = np.array([xterm1, xterm2]).T
        x = sm.add_constant(x)
        return x.dot(param)

def getData(data,usetestData=False):
    # test
    if usetestData:
        testIndex = [0.25,0.333,0.417,0.5,0.75,1,1.5,2,3,4,5,6,7,8,9,10,12,15,17,20,25,30]
        testYield =  [-0.602,-0.6059,-0.6096,-0.613,-0.6215,-0.6279,-0.6341,-0.6327,-0.6106,-0.5694,-0.5161,-0.456,
                  -0.3932,-0.3305,-0.2698,-0.2123,-0.1091,0.0159,0.0818,0.1601,0.2524,0.315]
        return [[testIndex,testYield]]
    
    # real data
    else: 
        tIndex = np.array([round(1/12,3),round(1/6,3),1/4,1/2,1,2,3,5,7,10,20,30])
        rows = data.shape[0]
        totalData = [ [tIndex,np.array(data.loc[i][1:].values,dtype="float")] for i in range(rows)]
        return totalData

def plot(nsm,tindex,yields):
    print('Best fit param: (RSqr=%.3f)' % nsm.rsqr)
    print('tau=%.2f intercept=%.3f beta1=%.3f beta2=%.3f' % (nsm.tau0, nsm.beta0, nsm.beta1, nsm.beta2) )
    # plot
    plt.figure(figsize=(12,5))
    plt.subplot(121)
    plt.plot(tindex, nsm.getSpot(tindex), 'o--', label='NS Model')
    plt.plot(tindex, yields, 'o-', label='Input Data')
    plt.title('Data fit to NS Model')
    plt.xlabel('t(Yr)')
    plt.ylabel('spot rate(%)')
    plt.legend()
    plt.subplot(122)
    plt.plot(tindex, nsm.getFwdRate(tindex), 'o-', label='NS Model')
    plt.title('Forward rate from NS Model')
    plt.xlabel('t(Yr)')
    plt.ylabel('forward rate(%)')
    plt.show()

def run(data,i,usetestData,plotStatus,avgDict):
    tindex,yields = getData(data,usetestData)[i]
    nsm = NSCurveFamily()
    nsm.estimateParam(tindex,yields)
    
    # plot
    if plotStatus:
        plot(nsm,tindex,yields)
    
    # average of parameters
    avgDict['t'] = avgDict.get('t',0) + nsm.tau0
    avgDict['b0'] = avgDict.get('b0',0)+ nsm.beta0
    avgDict['b1'] = avgDict.get('b1',0)+ nsm.beta1
    avgDict['b2'] = avgDict.get('b2',0) + nsm.beta2

    return tindex,yields,nsm.getSpot(tindex)

def test(id):
    base_dir = os.path.dirname(__file__)
    df = pd.read_excel(base_dir+"/data/TB_TERM_STRUCT_1YR.xlsx")
    rows = df.shape[0]
    avgDict = {}

    if id=="test":
        # test
        tindex,yields,spot = run(df,0,True,False,avgDict)
        for k,v in avgDict.items():
            avgDict[k] = v/rows
        return avgDict,tindex,yields,spot
    elif id=="all":
        # produce
        for i in range(rows):
            tindex,yields,spot = run(df,i,False,False,avgDict)
        for k,v in avgDict.items():
            avgDict[k] = v/rows
        return avgDict,[],[],[]
    else:
        try:
            tindex,yields,spot = run(df,int(id),False,False,avgDict)
            for k,v in avgDict.items():
                avgDict[k] = v/rows
        except Exception:
            return "error",[rows],[rows],[rows]
        return avgDict,tindex,yields,spot

if __name__ == "__main__":
    print(test("test"))