

f = open('text/metabolites.xml')

trig = False
names = []
for line in f:
    if '</secondary_accessions>' in line:
        trig = True
    if trig and '<name>' in line:
        name_s = line.find('<name>') + len('<name>')
        name_e = line.find('</name>')
        names.append(line[name_s:name_e])
        trig = False

w = open('text/metabolites.txt', 'w')
w.write('\n'.join(names))
w.close()


