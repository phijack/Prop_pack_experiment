from random import *
import math



def product(l):
    p = 1
    for i in l:
        p *= i
    return p

def tablegen(n,Nc,total):
    table = []
    for i in range(total):
        l = []
        q = i
        for j in range(n):
            l.append((q % (Nc[j])))
            q = q//Nc[j]
        t = tuple(l)
        table.append(t)
    return table

def plus(d):
    if d > 0:
        return d
    else:
        return 0

##======================================generate function======================================
def gen(n):
    s = []
    sum = 0
    for i in range(n):
        t = choice(range(1, 11, 1))
        s.append(t)
        sum = sum + t
    s.append(sum)
    return s

def rearranges(arr,n,Nc):
    s = []
    total = product(Nc)
    for i in range(n):
        t = [0]*Nc[i]
        t.append(arr[total])
        s.append(t)
    table = tablegen(n,Nc,total)
    for i in range(total):
        index = table[i]
        for j in range(n):
            s[j][index[j]] = s[j][index[j]] + arr[i]
    return s



def genalphabeta(n,arr,gap):
    alpha = []
    beta = []
    norm = 0
    for i in range(n):
        temp = arr[i] / arr[len(arr) - 1]
        alpha.append((temp - gap))
        beta.append((temp + gap))
    return alpha, beta, norm


def genalphabetanorm(n, arr, gap):
    s = []
    alpha = []
    beta = []
    sum = 0
    norm = 0
    for i in range(n):
        t = choice(range(1, 11, 1))
        s.append(t)
        sum = sum + t
    for i in range(n):
        temp = s[i] / sum
        temp1 = arr[i] / arr[len(arr) - 1]
        norm = norm + abs(temp - temp1)
        alpha.append((temp - gap))
        beta.append((temp + gap))
    return alpha, beta, norm


def ge_type(s):
    n = len(s)
    te = choice(range(s[n - 1]))
    typethre = 0
    for i in range(n - 1):
        typethre = typethre + s[i]
        if te < typethre:
            return i


##===============================auxiliary function================================
def betaviolatestats(s, sumvio, maxvio):
    for i in range(len(s)):
        if s[i] > 0:
            sumvio[i] = sumvio[i] + s[i]
            if s[i] > maxvio[i]:
                maxvio[i] = s[i]
    return sumvio, maxvio


def alphaviolatestats(s, sumvio, maxvio):
    for i in range(len(s)):
        if s[i] < 0:
            sumvio[i] = sumvio[i] + s[i]
            if s[i] < maxvio[i]:
                maxvio[i] = s[i]
    return sumvio, maxvio


def computecons(cap, beta,flag):
    betav = []
    if flag:
        for i in range(len(beta)):
            t = math.ceil(cap*beta[i])
            betav.append(t)
    else:
        for i in range(len(beta)):
            t = math.floor(cap*beta[i])
            betav.append(t)
    return betav


def datagen(s,fc,fw,n,Nc,Ne):
    es = []
    es_copy = []
    for i in range(Ne):
        if fc:
            total = product(Nc)
            table = tablegen(n,Nc,total)
            t = table[ge_type(s)]
        else:
            l = []
            for j in range(n):
                l.append(ge_type(s[j]))
            t = tuple(l)
        if fw:
            w = randint(0,100)
        else:
            w = 1
        temp = (w,i)+t
        es.append(temp)
        es_copy.append(temp)
    return es, es_copy



