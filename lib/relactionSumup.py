from lib.data import step_num, relations_list_file
from collections import Counter
from lib.dataClass import ReactInfo
def getReactions(reactInfo: ReactInfo):
    '''
    识别带*的中间态分子, 将单反应合成总反应
    如: CO->C*+O*、C*+O2->CO2、O*+CO->CO2 合并为: 2CO+O2->2CO2
    '''    
    reactionId = 0
    reactionListAll = []
    for stepi in range(step_num):
        pointsInfo = reactInfo.totalPoint[stepi]
        points = list(pointsInfo.keys())
        for point in points:
            if point[2] > 0: continue
            pointInfo = reactInfo.totalPoint[stepi][point]
            upPoint, downPoint = pointInfo["up"], pointInfo["down"]
            if len(upPoint) > 1:
                reactionId += 1
                reactInfo.totalPoint[stepi][point]["reactionId"].append(reactionId)
                for upPointk in upPoint:
                    stepu = upPointk[3]
                    reactInfo.totalPoint[stepu][upPointk]["reactionId"].append(reactionId)
                reactionListAll.append([upPoint, [point]])
                
            if len(downPoint) > 1:
                reactionId += 1
                reactInfo.totalPoint[stepi][point]["reactionId"].append(reactionId)
                for downPointk in downPoint:
                    stepd = downPointk[3]
                    reactInfo.totalPoint[stepd][downPointk]["reactionId"].append(reactionId)
                reactionListAll.append([[point], downPoint])
            
    return reactInfo, reactionId, reactionListAll

def addReactions(reactInfo, reactionId, reactionListAll):
    for stepi in range(step_num):
        pointsInfo = reactInfo.totalPoint[stepi]
        points = list(pointsInfo.keys())
        for point in points:
            if point[2] == 0: continue
            pointInfo = reactInfo.totalPoint[stepi][point]
            reactionId += 1
            left, right = [], []
            pointReacts = set(pointInfo["reactionId"])
            for reactionk in pointReacts:
                reactionIndex = reactionk - 1
                left += reactionListAll[reactionIndex][0]
                right += reactionListAll[reactionIndex][1]
                reactionListAll[reactionIndex] = []
                pointsNew = set(left + right)
                for pointNew in pointsNew:
                    stepRe = pointNew[3]
                    listNew = list(set(reactInfo.totalPoint[stepRe][pointNew]["reactionId"]))
                    if reactionk in listNew: listNew.remove(reactionk)
                    listNew.append(reactionId)
                    reactInfo.totalPoint[stepRe][pointNew]["reactionId"] = list(set(listNew))
            reactionListAll.append([left, right])

    reactionNewId = {}
    newId = 0

    for i in range(reactionId):
        if len(reactionListAll[i]) != 0:
            reactionNewId[i + 1] = newId
            newId += 1
    for stepi in range(step_num):
        pointsInfo = reactInfo.totalPoint[stepi]
        pointsi = list(pointsInfo.keys())
        for point in pointsi:
            pointInfo = reactInfo.totalPoint[stepi][point]
            reactInfo.totalPoint[stepi][point]["reactionId"] = [reactionNewId[k] for k in set(pointInfo["reactionId"])]
    for i in range(len(reactionListAll) - 1, -1, -1):
        if len(reactionListAll[i]) == 0:
            reactionListAll.pop(i)
    return reactionListAll

def getReactionType(reactionListAll):
    '''
    获取反应方程式, 按方程式归类
    ''' 
    reactionDict = {}
    reactionTypeId = [0 for _ in reactionListAll]
    for reactionId, reactioni in enumerate(reactionListAll):
        left, right = reactioni
        leftNames, rightNames = [], []
        for point in left:
            if point[2] > 0: continue
            leftNames.append(point[1])            
        for point in right:
            if point[2] > 0: continue
            rightNames.append(point[1])
        leftNames.sort()
        rightNames.sort()
        reactionType = tuple([tuple(leftNames), tuple(rightNames)]) 
        if reactionType not in reactionDict: reactionDict[reactionType] = []
        reactionDict[reactionType].append(reactionId)
        reactionTypeId[reactionId] = list(reactionDict.keys()).index(reactionType)
    return reactionDict

def write_reaction_list(reactionDict):
    '''
    写出所有反应
    ''' 
    fre = open(relations_list_file, 'w')
    for reactioni in reactionDict.keys():
        left, right = reactioni
        dict1, dict2 = Counter(left), Counter(right)
        leftNew, rightNew = [], []
        for i in dict1.keys():
            if dict1[i] == 1: leftNew.append(i)
            else: leftNew.append(f'{dict1[i]} {i}')
        for i in dict2.keys():
            if dict2[i] == 1: rightNew.append(i)
            else: rightNew.append(f'{dict2[i]} {i}')
        fre.write(f"{len(reactionDict[reactioni])} | ")
        fre.write(" + ".join(leftNew))
        fre.write(" -> ")
        fre.write(" + ".join(rightNew))
        fre.write("\n")
    fre.close()
    return