# -*- coding:utf-8 -*-

from math import sqrt

critics = {'Lisa Rose': {'Lady in the Water': 2.5, 'Snake on a Plane':3.5,
    'Just My Luck':3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5,
    'The Night Listener': 3.0},
    'Gene Seymour': {'Lady in the Water': 3.0, 'Snake on a Plane':3.5,
    'Just My Luck':1.5, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5,
    'The Night Listener': 3.0},
    'Michael Phillips': {'Lady in the Water': 2.5, 'Snake on a Plane':3.0,
    'Superman Returns': 3.5, 'The Night Listener': 4.0},
    'Claudia Puig': {'Snake on a Plane':3.5, 'Just My Luck':3.0,
    'Superman Returns': 4.0, 'You, Me and Dupree': 2.5,
    'The Night Listener': 4.5},
    'Mick LaSalle': {'Lady in the Water': 3.0, 'Snake on a Plane':4.0,
    'Just My Luck':2.0, 'Superman Returns': 3.0, 'You, Me and Dupree': 2.0,
    'The Night Listener': 3.0},
    'Jack Matthews': {'Lady in the Water': 3.0, 'Snake on a Plane':4.0,
    'Superman Returns': 5.0, 'You, Me and Dupree': 3.5,
    'The Night Listener': 3.0},
    'Toby': {'Snake on a Plane':4.5, 'Superman Returns': 4.0,
    'You, Me and Dupree': 1.0}}

customers = {'daixin': {'book': 4.5, 'phone': 4.8, 'ball': 3.5, 'food': 4.0},
             'pds': {'milk': 4.0, 'book': 3.0, 'phone': 4.5, 'cloths': 3.5},
             'lifeng': {'food': 3.5, 'shoes': 4.0, 'cloths': 4.5, 'phone': 4.0}}

def sim_distance(prefs, person1, person2):
    """
    欧几里德距离
    """
    si = {}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1

    if len(si) == 0:
        return 0

    sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2)
        for item in prefs[person1] if item in prefs[person2]])

    return 1 / (1 + sqrt(sum_of_squares))


def sim_pearson(prefs, p1, p2):
    """
    皮尔逊相关度评价
    """
    # 得到双方都曾评价过的物品列表
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item] = 1

    n = float(len(si))
    if n == 0:
        return 1

    # 对所有偏好求和
    sum1 = sum([prefs[p1][it] for it in si])
    sum2 = sum([prefs[p2][it] for it in si])

    # 求平方和
    sq_sum1 = sum([pow(prefs[p1][it], 2) for it in si])
    sq_sum2 = sum([pow(prefs[p2][it], 2) for it in si])

    # 求乘积之和
    p_sum = sum([prefs[p1][it] * prefs[p2][it] for it in si])

    # 计算皮尔逊评价值
    num = p_sum - (sum1 * sum2 / n)
    den = sqrt((sq_sum1 - pow(sum1, 2)/n)*(sq_sum2 - pow(sum2, 2)/n))
    if den == 0:
        return 0
    r = num / den

    return r


def topmatches(prefs, person, n=6, similarity = sim_pearson):
    """
    寻找与指定人员品味相近的人
    """
    scores = [(similarity(prefs, person, other), other) for other in prefs if other != person]
    scores.sort()
    scores.reverse()
    return scores[0:n]


def getRecommendations(prefs, person, similarity=sim_pearson):
    """
    利用所有他人评价值的加权平均，为某人提供建议
    """
    totals = {}
    simSums = {}
    for other in prefs:
        # 不和自己做比较
        if other == person:
            continue
        sim = similarity(prefs, person, other)

        # 忽略评价值为零或小于零的情况
        if sim <= 0:
            continue
        for item in prefs[other]:
            # 只对自己还未曾看过的影片进行评价
            if item not in prefs[person] or prefs[person][item] == 0:
                # 相似度×评价值 总和
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item]*sim
                # 相似度之和
                simSums.setdefault(item, 0)
                simSums[item] += sim

    # 建立一个归一化的列表
    rankings = [(total/simSums[item], item) for item, total in totals.items()]
    # 返回经过排序的列表
    rankings.sort()
    rankings.reverse()
    return rankings


def pairs_sim(pref, similarity=sim_pearson):
    """
    给定的所有人员中两两相关度
    author: daixin 2016-7-28
    """
    name = pref.keys()
    length = len(name)
    # 将一个列表中元素两两组成元组， 想想有没有更简洁的表达
    pairs = [(name[i], name[j]) for i in range(length) for j in range(length) if i < j]
    person_sim = {}
    for item in pairs:
        person_sim[item] = similarity(pref, *item)
    sorted_person_sim = sorted(person_sim.items(), key=lambda x: x[1], reverse=True)
    return sorted_person_sim


def transformPrefs(prefs):
    """
    将字典中人员与物品位置对换
    """
    result = {}
    for person in prefs:
        for item in prefs[person]:
            result.setdefault(item, {})

            # 将物品和人员对调
            result[item][person] = prefs[person][item]
    return result


def calculateSimilarItems(prefs, n=10):
    """计算与所给物品最为相近的所有其他物品"""
    result = {}

    # 以物品为中心对偏好矩阵实行倒置处理
    itemPrefs = transformPrefs(prefs)
    c = 0
    for item in itemPrefs:
        # 针对大数据集更新状态变量
        c += 1
        if c % 100 == 0:
            print "%d / %d" % (c, len(itemPrefs))
        # 寻找最为相近的物品
        scores = topmatches(itemPrefs, item, n=n, similarity=sim_distance)
        result[item] = scores
    return result


def getRecommendedItems(prefs, itemMatch, user):
    """获得推荐物品"""
    userRatings = prefs[user]
    scores = {}
    totalSim = {}
    # 循环遍历由当前用户评分的物品
    for (item, rating) in userRatings.items():
        # 循环遍历与当前物品相近的物品
        for (similarity, item2) in itemMatch[item]:
            # 忽略已做过评价的物品
            if item2 in userRatings:
                continue
            # 评价值与相似度的加权之和
            scores.setdefault(item2, 0)
            scores[item2] += similarity*rating
            # 全部相似度之和
            totalSim.setdefault(item2, 0)
            totalSim[item2] += similarity
    # 将每个合计值除以加权和，求出平均值
    rankings = [(score/totalSim[item], item) for item, score in scores.items()]

    rankings.sort()
    rankings.reverse()
    return rankings


itemsim=calculateSimilarItems(customers)
print getRecommendedItems(customers, itemsim, 'daixin')
