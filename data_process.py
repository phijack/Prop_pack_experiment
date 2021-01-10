import csv
import os
import fnmatch

file_names = os.listdir()

for Na in range(3,16):
    for Ne in [10000,20000,30000]:
        for fr in [True]:
            for fc in [True, False]:
                for fw in [True, False]:
                    for gap in[0.02]:
                        with open('prop_pack_data_'+str(Ne)+'_'+str(Na)+'r'+str(fr)+'w'+str(fw)+'c'+str(fc)+'_'+str(gap)+'.csv', 'w', newline='') as csv_file:
                            propwriter = csv.writer(csv_file, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                            file_name_l = fnmatch.filter(file_names,'prop_pack_data_'+str(Ne)+'_'+str(Na)+'r'+str(fr)+'w'+str(fw)+'c'+str(fc)+'_'+str(gap)+'_*.csv')
                            for file_name in file_name_l:
                                with open(file_name,'r') as csvf:
                                    creader = csv.reader(csvf)
                                    for r in creader:
                                        if creader.line_num != 11:
                                            continue
                                        else:
                                            propwriter.writerow(r)



