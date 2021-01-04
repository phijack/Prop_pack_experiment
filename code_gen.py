##======Parameter===========
Na = 10 #number of attributes
Ne = 10000#number of candidate
Nc = [2]*Na#number of categories for each attribute
fc = False#correlated
fw = False#weighted
fr = True#random
gap = 0.02#gap




def paragen(para,n):
    s = ""
    for i in range(n):
        t = ","+para+"_"+str(i+1)
        s = s + t
    return s


def paragenp(para,n,p):
    s = ""
    for i in range(n):
        t = p+para+"_"+str(i+1)
        s = s + t
    return s

def paragenb(para,n,b):
    s = ""
    for i in range(n):
        t = ","+para+"_"+str(i+1)+"_"+str(b)
        s = s + t
    return s

def averagegen(para,n,b,p):
    s = ""
    for i in range(n):
        t = p+"sum("+para+"_"+str(i+1)+"_"+str(b)+")/len("+para+"_"+str(i+1)+"_"+str(b)+")"
        s = s + t
    return s

def paragenbp(para,n,b,p):
    s = ""
    for i in range(n):
        t = p+para+"_"+str(i+1)+"_"+str(b)
        s = s + t
    return s

def change(n):
    s = ""
    s = s+"times = 30\n"
    s = s+"count = 0\n"
    s = s+"delta = 4\n"
    s = s+"def change(s, pack):\n"
    s = s+"\tresult = []\n"
    s = s+"\tfor w,i"+paragen("a",n)+" in s:\n"
    s = s+"\t\ttemp = pack[w,i"+paragen("a",n)+"].getAttr("+'"x"'+")\n"
    s = s+"\t\tresult.append(temp)\n"
    s = s+"\treturn result\n"
    return s




##====================data generate===========================


##====================LP constraint generate==================
def star(n,i):
    s = "'*','*'"
    for j in range(n):
        if j+1 == i:
            s = s + ",i"
        else:
            s = s + ",'*'"
    return s

def LPwrite(flag,n,Nc):
    s = "def "
    if flag:
        s = s+"ILP"
    else:
        s = s+"LP"
    s = s+"(s"+paragen("beta",n)+paragen("alpha",n)+"):\n"
    s = s+"\tm = Model('prop_pack')\n"#start
    s = s+"\tm.setParam(GRB.Param.LogToConsole, 0)\n"
    if flag:
        s = s+"\tm.setParam(GRB.Param.MIPGap, 0.0)\n"
        s = s+"\tm.setParam(GRB.Param.TimeLimit, 300.0)\n"
        s = s+"\tpack = m.addVars(s, ub=1, vtype=GRB.INTEGER, name="+'"pack"'+")\n"
    else:
        s = s+"\tpack = m.addVars(s, ub=1.0, vtype=GRB.CONTINUOUS, name="+'"pack"'+")\n"
    s = s+"\tm.setObjective(quicksum(pack[w,i" + paragen("a",n)+"]*w for w,i"+paragen("a",n)+" in s), GRB.MAXIMIZE)\n"
    for i in range(n):
        s = s + "\tcons_"+str(i+1)+" = m.addConstrs((pack.sum("+star(n,i+1)+") - beta_"+str(i+1)+"[i] * pack.sum("+star(n,0)+") <= 0 for i in range("+str(Nc[i])+")), "+'"cons_'+str(i+1)+'")\n'
        s = s + "\tcons_"+str(n+i+1)+" = m.addConstrs((pack.sum("+star(n,i+1)+") - alpha_"+str(i+1)+"[i] * pack.sum("+star(n,0)+") >= 0 for i in range("+str(Nc[i])+")), "+'"cons_'+str(n+i+1)+'")\n'
    s = s+"\tm.optimize()\n"#end
    if flag:
        s = s+ "\tif m.status == GRB.Status.OPTIMAL:\n"
        s = s+ "\t\tresult = change(s, pack)\n"
        s = s+ "\t\treturn result, m.objVal\n"
        s = s+ "\tif m.status == GRB.Status.TIME_LIMIT:\n"
        s = s+ "\t\treturn 0, -1\n"
    else:
        s = s + "\tif m.status == GRB.Status.OPTIMAL:\n"
        s = s + "\t\treturn m.objVal\n"
    return s

def ite(n,Nc):
    s = "def iterative(s, above, bottom"+paragen("betav", n)+paragen("alphav",n)+paragen("delbetav",n)+", result):\n"
    for i in range(n):
        t_0 = [0]*Nc[i]
        s = s+ "\tbetavl_"+str(i+1)+" = "+ str(t_0)+"\n"
    s = s+ "\tvl = 0\n"
    s = s+"\tm = Model('prop_pack')\n"#start
    s = s+"\tm.setParam(GRB.Param.LogToConsole, 0)\n"
    s = s+"\tpack = m.addVars(s, ub=1.0, vtype=GRB.CONTINUOUS, name="+'"pack"'+")\n"
    s = s+"\tm.setObjective(quicksum(pack[w,i" + paragen("a",n)+"]*w for w,i"+paragen("a",n)+" in s), GRB.MAXIMIZE)\n"
    for i in range(n):
        s = s + "\tcons_"+str(i+1)+" = m.addConstrs((pack.sum("+star(n,i+1)+") <= betav_"+str(i+1)+"[i] for i in range("+str(Nc[i])+") if delbetav_"+str(i+1)+"[i] == 0), "+'"cons_'+str(i+1)+'")\n'
        s = s + "\tcons_"+str(n+i+1)+" = m.addConstrs((pack.sum("+star(n,i+1)+") >= alphav_"+str(i+1)+"[i] for i in range("+str(Nc[i])+") if delbetav_"+str(i+1)+"[i] == 0), "+'"cons_'+str(n+i+1)+'")\n'
    s = s+"\tcons_"+str((2*n+1))+" = m.addConstr(pack.sum("+star(n,0)+") <= above, "+'"con_'+str((2*n+1))+'")\n'
    s = s+"\tcons_"+str((2*n+2))+" = m.addConstr(pack.sum("+star(n,0)+") >= bottom, "+'"con_'+str((2*n+2))+'")\n'
    s = s+"\tm.optimize()\n"
    s = s+"\tif m.status == GRB.Status.OPTIMAL:\n"
    s = s+"\t\tfor w,i" + paragen("a",n)+" in s:\n"
    s = s+"\t\t\tif pack[w,i"+ paragen("a",n)+"].getAttr("+'"x"'+") == 0.0:\n"
    s = s+"\t\t\t\tt = (w,i" + paragen("a",n)+")\n"
    s = s+"\t\t\t\ts.remove(t)\n"
    s = s+"\t\t\telif pack[w,i"+ paragen("a",n)+"].getAttr("+'"x"'+") == 1.0:\n"
    s = s+"\t\t\t\tt = (w,i" + paragen("a",n)+")\n"
    s = s+"\t\t\t\ts.remove(t)\n"
    s = s+"\t\t\t\tresult[i] = 1\n"
    s = s+"\t\t\t\tvl = vl + w\n"
    for i in range(n):
        s = s + "\t\t\t\tbetavl_"+str(i+1)+"[a_"+str(i+1)+"] = betavl_"+str(i+1)+"[a_"+str(i+1)+"] + 1\n"
    s = s + "\t\treturn s, vl" +paragen("betavl",n)+", result\n"
    s = s + "\telse:\n"
    s = s + "\t\treturn -1\n"
    return s

def guess(n,Nc):
    s = "def guessing(s, n"+paragen("beta",n)+paragen("alpha",n)+"):\n"
    s = s+"\tm = Model('prop_pack')\n"#start
    s = s+"\tm.setParam(GRB.Param.LogToConsole, 0)\n"
    s = s+"\tm.setParam(GRB.Param.MIPGap, 0.0)\n"
    s = s+"\tm.setParam(GRB.Param.TimeLimit, 300.0)\n"
    s = s+"\tpack = m.addVars(s, ub=1, vtype=GRB.INTEGER, name="+'"pack"'+")\n"
    s = s+"\tm.setObjective(quicksum(pack[w,i" + paragen("a",n)+"]*w for w,i"+paragen("a",n)+" in s), GRB.MAXIMIZE)\n"
    for i in range(n):
        s = s + "\tcons_"+str(i+1)+" = m.addConstrs((pack.sum("+star(n,i+1)+") <= beta_"+str(i+1)+"[i] * n for i in range("+str(Nc[i])+")), "+'"cons_'+str(i+1)+'")\n'
        s = s + "\tcons_"+str(n+i+1)+" = m.addConstrs((pack.sum("+star(n,0)+") - pack.sum("+star(n,i+1)+") <= (1 - alpha_"+str(i+1)+"[i]) * n for i in range("+str(Nc[i])+")), "+'"cons_'+str(n+i+1)+'")\n'
    s = s+"\tm.optimize()\n"
    s = s+"\tif m.status == GRB.Status.OPTIMAL:\n"
    s = s+"\t\treturn m.objVal\n"
    s = s+"\tif m.status == GRB.Status.TIME_LIMIT:\n"
    s = s+"\t\treturn -1\n"
    return s

def stat(n,Nc):
    s = "def statistical(s, result):\n"
    for i in range(n):
        t_0 = [0]*Nc[i]
        s = s+ "\tbetavlar_"+str(i+1)+" = "+ str(t_0)+"\n"
    s = s+ "\tvlar = 0\n"
    s = s+"\tfor w,i" + paragen("a",n)+" in s:\n"
    s = s+"\t\tif result[i] == 1.0:\n"
    s = s+"\t\t\tvlar = vlar + w\n"
    for i in range(n):
        s = s + "\t\t\tbetavlar_"+str(i+1)+"[a_"+str(i+1)+"] = betavlar_"+str(i+1)+"[a_"+str(i+1)+"] + 1\n"   
    s = s + "\treturn vlar" +paragen("betavlar",n)+"\n"
    return s



##=====================test generate==========================
def testgen(n,Nc,fw):
    s = "def test(n, propwriter, rawwriter"+paragen("beta",n)+paragen("alpha",n)+",norm,s,gap):\n"
    for i in range(n):
        t_0 = [0]*Nc[i]
        s = s+"\tbetavla_"+str(i+1)+" = "+str(t_0)+"\n"
        s = s+"\tdelbetav_"+str(i+1)+" = "+str(t_0)+"\n"
        s = s+"\tdifbeta_"+str(i+1)+"_2 = "+str(t_0)+"\n"
        s = s+"\tdifbeta_"+str(i+1)+"_4 = "+str(t_0)+"\n"
        s = s+"\tdifalpha_"+str(i+1)+"_2 = "+str(t_0)+"\n"
        s = s+"\tdifalpha_"+str(i+1)+"_4 = "+str(t_0)+"\n"
    s = s + "\tvla = 0\n"
    s = s + "\tresult_2 = [0]*n\n"
    s = s + "\tresult_4 = []\n"
    s = s + "\tes,es_copy = datagen(s,fc,fw,Na,Nc,n)\n"
    if not fw:
        s = s + "\tstart_1 = time.clock()\n"
        s = s + "\tresult_1, opt_1 = ILP(es"+paragen("beta",n)+paragen("alpha",n)+")\n"
        s = s + "\ttime_1 = time.clock() - start_1\n"
        s = s + "\topt_1 = round(opt_1)\n"
    s = s + "\tstart_2 = time.clock()\n"
    s = s + "\ttem = LP(es"+paragen("beta",n)+paragen("alpha",n)+")\n"
    s = s + "\ttime_2 = time.clock() - start_2\n"
    s = s + "\tcap = math.ceil(tem)\n"
    s = s + "\tcap_1 = math.floor(tem)\n"
    s = s + "\ttem = cap\n"
    for i in range(n):
        s = s + "\tbetav_"+str(i+1)+" = computecons(cap, beta_"+str(i+1)+", 1)\n"
        s = s + "\talphav_"+str(i+1)+" = computecons(cap_1, alpha_"+str(i+1)+", 0)\n"
    s = s + "\tcount = 0\n"
    s = s + "\tstart_3 = time.clock()\n"
    s = s + "\twhile True:\n"
    for i in range(n):
        t_0 = [0]*Nc[i]
        s = s+"\t\ttbetav_"+str(i+1)+" = "+str(t_0)+"\n"
    s = s + "\t\tes_copy,tvl"+paragen("tbetavl",n)+", result_2 = iterative(es_copy, cap, cap_1"+paragen("betav",n)+paragen("alphav",n)+paragen("delbetav",n)+", result_2)\n"
    s = s + "\t\tvla = vla + tvl\n"
    s = s + "\t\tcap = cap - tvl\n"
    s = s + "\t\tcap_1 = cap_1 - tvl\n"
    for i in range(n):
        s = s + "\t\tfor i in range("+str(Nc[i])+"):\n"
        s = s + "\t\t\tbetavla_"+str(i+1)+"[i] = betavla_"+str(i+1)+"[i] + tbetavl_"+str(i+1)+"[i]\n"
        s = s + "\t\t\tif i < len(betav_"+str(i+1)+"):\n"
        s = s + "\t\t\t\tbetav_"+str(i+1)+"[i] = betav_"+str(i+1)+"[i] + tbetavl_"+str(i+1)+"[i]\n"
        s = s + "\t\t\t\talphav_"+str(i+1)+"[i] = alphav_"+str(i+1)+"[i] + tbetavl_"+str(i+1)+"[i]\n"
    s = s + "\t\tfor w,i"+paragen("a",n)+" in es_copy:\n"
    for i in range(n):
        s = s + "\t\t\ttbetav_"+str(i+1)+"[a_"+str(i+1)+"] = tbetav_"+str(i+1)+"[a_"+str(i+1)+"] + 1\n"
    for i in range(n):
        s = s + "\t\tfor i in range("+str(Nc[i])+"):\n"
        s = s + "\t\t\tif tbetav_"+str(i+1)+"[i] < 2 * delta - 1:\n"
        s = s + "\t\t\t\tdelbetav_"+str(i+1)+"[i] = 1\n"
    s = s + "\t\tcount = count + 1\n"
    s = s + "\t\tif len(es_copy) == 0:\n"
    s = s + "\t\t\tbreak\n"
    s = s + "\topt_2 = vla\n"
    s = s + "\ttime_3 = (time.clock() - start_3) + time_2\n"
    if not fw:
        s = s + "\tstart_4 = time.clock()\n"
        s = s + "\tcap = tem\n"
        s = s + "\tcountg = 0\n"
        s = s + "\twhile True:\n"
        s = s + "\t\tcountg = countg + 1\n"
        s = s + "\t\topt_3 = guessing(es, cap"+paragen("beta",n)+paragen("alpha",n)+")\n"
        s = s + "\t\tif opt_3 < cap:\n"
        s = s + "\t\t\tcap = opt_3\n"
        s = s + "\t\telse:\n"
        s = s + "\t\t\tbreak\n"
        s = s + "\ttime_4 = time.clock() - start_4 + time_2\n"
    s = s + "\tstart_5 = time.clock()\n"
    s = s+"\tm = Model('prop_pack')\n"
    s = s+"\tm.setParam(GRB.Param.LogToConsole, 0)\n"
    s = s+"\tpack = m.addVars(es, ub=1.0, vtype=GRB.CONTINUOUS, name="+'"pack"'+")\n"
    s = s+"\tm.setObjective(quicksum(pack[w,i" + paragen("a",n)+"]*w for w,i"+paragen("a",n)+" in es), GRB.MAXIMIZE)\n"
    for i in range(n):
        s = s + "\tcons_"+str(i+1)+" = m.addConstrs((pack.sum("+star(n,i+1)+") - beta_"+str(i+1)+"[i] * pack.sum("+star(n,0)+") <= 0 for i in range("+str(Nc[i])+")), "+'"cons_'+str(i+1)+'")\n'
        s = s + "\tcons_"+str(n+i+1)+" = m.addConstrs((pack.sum("+star(n,i+1)+") - alpha_"+str(i+1)+"[i] * pack.sum("+star(n,0)+") >= 0 for i in range("+str(Nc[i])+")), "+'"cons_'+str(n+i+1)+'")\n'
    s = s+"\tm.optimize()\n"
    s = s + "\tintecount = 0\n"
    s = s+ "\tif m.status == GRB.Status.OPTIMAL:\n"
    s = s + "\t\tfor w,i"+paragen("a",n)+" in es:\n"
    s = s + "\t\t\tp = pack[w,i"+paragen("a",n)+"].getAttr("+'"x"'+")\n"
    s = s + "\t\t\tif p >= 1.0:\n"
    s = s + "\t\t\t\tp = 1.0\n"
    s = s + "\t\t\t\tintecount = intecount + 1\n"
    s = s + "\t\t\tif p <= 0.0:\n"
    s = s + "\t\t\t\tp = 0.0\n"
    s = s + "\t\t\t\tintecount = intecount + 1\n"
    s = s + "\t\t\ttemp = np.random.binomial(1.0, p, 1)\n"
    s = s + "\t\t\tresult_4.append(temp)\n"
    s = s + "\ttime_5 = time.clock() - start_5\n"
    s = s + "\topt_4"+paragenb("betavlar",n,4)+" = statistical(es, result_4)\n"
    for i in range(n):
        s = s + "\tfor i in range("+str(Nc[i])+"):\n"
        s = s + "\t\tdifbeta_"+str(i+1)+"_2[i] = math.ceil(plus(betavla_"+str(i+1)+"[i] - opt_2 * beta_"+str(i+1)+"[i]))\n"
        s = s + "\t\tdifbeta_"+str(i+1)+"_4[i] = math.ceil(plus(betavlar_"+str(i+1)+"_4[i] - opt_4 * beta_"+str(i+1)+"[i]))\n"
        s = s + "\t\tdifalpha_"+str(i+1)+"_2[i] = math.ceil(plus( - betavla_"+str(i+1)+"[i] + opt_2 * alpha_"+str(i+1)+"[i]))\n"
        s = s + "\t\tdifalpha_"+str(i+1)+"_4[i] = math.ceil(plus( - betavlar_"+str(i+1)+"_4[i] + opt_4 * alpha_"+str(i+1)+"[i]))\n"
    if fw:
        s = s + "\tpropwriter.writerow([n,gap,norm, time_3, time_5,tem, opt_2, opt_4,intecount]"+paragenp("betavla",n,"+")+paragenbp("betavlar",n,4,"+")+paragenbp("difbeta",n,2,"+")+paragenbp("difbeta",n,4,"+")+paragenbp("difalpha",n,2,"+")+paragenbp("difalpha",n,4,"+")+")\n"
        s = s + "\tresult = [n,gap,norm, time_3, time_5,tem, opt_2, opt_4,intecount, (0"+averagegen("difbeta",n,2,"+")+")/Na, (0"+averagegen("difbeta",n,4,"+")+")/Na, (0"+averagegen("difalpha",n,2,"+")+")/Na, (0"+averagegen("difalpha",n,4,"+")+")/Na"+"]\n"
    else:
        s = s + "\tpropwriter.writerow([n,gap,norm,time_1, time_3, time_4, time_5, opt_1, opt_2, opt_3, opt_4,intecount]"+paragenp("betavla",n,"+")+paragenbp("betavlar",n,4,"+")+paragenbp("difbeta",n,2,"+")+paragenbp("difbeta",n,4,"+")+paragenbp("difalpha",n,2,"+")+paragenbp("difalpha",n,4,"+")+")\n"
        s = s + "\tresult = [n,gap,norm, time_1, time_3, time_4, time_5, opt_1, opt_2, opt_3, opt_4,intecount, (0"+averagegen("difbeta",n,2,"+")+")/Na, (0"+averagegen("difbeta",n,4,"+")+")/Na, (0"+averagegen("difalpha",n,2,"+")+")/Na, (0"+averagegen("difalpha",n,4,"+")+")/Na"+"]\n"
    s = s + "\trawwriter.writerow([s, result_1, result_2, result_4])\n"
    s = s + "\treturn result\n"
    return s


##=====================main body==============================

def body(fr,fw,fc,Na,Nc,Ne,gap):
    s = ""
    if fc:
        s = s + "total = product(Nc)\n"
        s = s + "s = gen(total)\n"
        s = s + "sp = rearranges(s,Na,Nc)\n"
    else:
        s = s + "s = ["
        for i in range(Na-1):
            s = s+ "gen("+str(Nc[i])+"),"
        s = s + "gen("+str(Nc[Na-1])+")]\n"
        s = s + "sp = s\n"
    for i in range(Na):
        if fr:
            s = s + "alpha_"+str(i+1)+", beta_"+str(i+1)+", norm_"+str(i+1)+" = genalphabetanorm(Nc["+str(i)+"], sp["+str(i)+"], gap)\n"
        else:
            s = s + "alpha_"+str(i+1)+", beta_"+str(i+1)+", norm_"+str(i+1)+" = genalphabeta(Nc["+str(i)+"], sp["+str(i)+"], gap)\n"
    s = s + "norm = max([0"+paragen("norm",Na)+"])\n"
    s = s + "with open('prop_pack_data_'+str(Ne)+'_'+str(Na)+'r'+str(fr)+'w'+str(fw)+'c'+str(fc)+'_'+str(gap)+'_'+str(norm)+'.csv', 'w', newline='') as csv_file, open('raw_data_'+str(Ne)+'_'+str(Na)+'r'+str(fr)+'w'+str(fw)+'c'+str(fc)+'_'+str(gap)+'_'+str(norm)+'.csv', 'w', newline='') as csv_f:\n"
    s = s + "\tpropwriter = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)\n"
    s = s + "\trawwriter = csv.writer(csv_f, delimiter=',', quoting=csv.QUOTE_MINIMAL)\n"
    s = s + "\tres = []\n"
    s = s + "\tfor i in range(times):\n"
    s = s + "\t\trt = test(n, propwriter, rawwriter"+paragen("beta",Na)+paragen("alpha",Na)+",norm,s,gap)\n"
    s = s + "\t\tres.append(rt)\n"
    s = s + "\tave = []\n"
    s = s + "\tfor i in range(len(res[0])):\n"
    s = s + "\t\tsumt = 0\n"
    s = s + "\t\tfor j in range(times):\n"
    s = s + "\t\t\tsumt = sumt+res[j][i]\n"
    s = s + "\t\tave.append((sumt / times))\n"
    s = s + "\tpropwriter.writerow(ave)\n"
    return s

def code_gen(Na,Ne,Nc,fr,fc,fw,gap):
    s = "from gurobipy import *\n"
    s = s + "import time\n"
    s = s + "import csv\n"
    s = s + "import numpy as np\n"
    s = s + "from prop_pack import *\n"
    s = s + "Na = "+str(Na)+"\n"
    s = s + "n = "+str(Ne)+"\n"
    s = s + "Nc = "+str(Nc)+"\n"
    s = s + "fc = "+str(fc)+"\n"
    s = s + "fw = "+str(fw)+"\n"
    s = s + "gap = "+str(gap)+"\n"
    s = s + "fr = "+str(fr)+"\n"


    with open('solver_'+str(Ne)+'_'+str(Na)+'r'+str(fr)+'w'+str(fw)+'c'+str(fc)+'_'+str(gap)+'.py','w') as pfile:
        pfile.write(s)
        pfile.write(change(Na))
        pfile.write(LPwrite(True,Na,Nc))
        pfile.write(LPwrite(False,Na,Nc))
        pfile.write(ite(Na,Nc))
        pfile.write(guess(Na,Nc))
        pfile.write(stat(Na,Nc))
        pfile.write(testgen(Na,Nc,fw))
        pfile.write(body(fr,fw,fc,Na,Nc,Ne,gap))

#code_gen(Na,Ne,Nc,fr,fc,fw,gap)
with open('prop.bat', 'w') as bfile:
    bfile.write('call C:\\Users\\remote\\Anaconda3\\Scripts\\activate.bat C:\\Users\\remote\\Anaconda3\n')
    bfile.write("cd /d F:\\prop_pack\n")
    for Na in []:
        for Ne in []:
            for fr in [True, False]:
                for fc in [True, False]:
                    for fw in [True, False]:
                        for gap in[]:
                            Nc = [2]*Na
                            code_gen(Na,Ne,Nc,fr,fc,fw,gap)
                            if fr:
                                for i in range(100):
                                    bfile.write("python "+'solver_'+str(Ne)+'_'+str(Na)+'r'+str(fr)+'w'+str(fw)+'c'+str(fc)+'_'+str(gap)+'.py\n')
                            else:
                                bfile.write("python "+'solver_'+str(Ne)+'_'+str(Na)+'r'+str(fr)+'w'+str(fw)+'c'+str(fc)+'_'+str(gap)+'.py\n')