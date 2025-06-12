'''
This file is a calculation example of ethylene-propyl blend system. 
data1_1, data1_2 and data1_3 in the same directory are the solution parameters of 125 molecules 500 frames, 1000 molecules 500 frames and 1000 molecules 1000 frames, respectively.
To use./lib/data.py, update the content to: "from data1_1 import *" or others
'''

from time import time

from lib.divideFiles import divideDump, divideBond
from lib.dump2dataFull import getFullDataPre, getFullData
from lib.calChainChange import getPointPair
from lib.relactionSumup import getReactions, addReactions, getReactionType, write_reaction_list

def print_time(time1, string = ""): 
    '''
    计时功能
    '''
    print(string, time() - time1)
    return time()

if __name__ == '__main__':
    time1 = time()
    #--------------------------------------------------------------------
    divideDump()
    divideBond()
    time1 = print_time(time1, string = "transform file time: ")

    getFullDataPre()
    getFullData()
    time1 = print_time(time1, string = "write full data file time: ")
    #--------------------------------------------------------------------
    reactInfo = getPointPair()
    time1 = print_time(time1, string = "write all dot time: ")
    #--------------------------------------------------------------------
    reactInfo.getDelPoint()
    reactInfo.delTotalPoint()
    reactInfo.write()
    reactInfo.transSvg()
    time1 = print_time(time1, string = "write final dot and svg time: ")

    reactInfo, reactionId, reactionListAll = getReactions(reactInfo)
    reactionListAll = addReactions(reactInfo, reactionId, reactionListAll)
    reactionDict = getReactionType(reactionListAll)

    write_reaction_list(reactionDict)

    time1 = print_time(time1, string = "write reaction list time: ")