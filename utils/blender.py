import random

normal = open('text/trigram_wiki.txt').read().split('\n')
prot = open('text/protein_names.txt').read().split('\n')

out = []
w = open('text/blended.txt', 'w')

quant = 500000
nw = random.sample(normal, quant)
pw = random.sample(prot, quant)

for i in range(quant):
    a = nw[i].strip() + ' ' + pw[i].strip()
    out.append(a)
    a = pw[i].strip() + ' ' + pw[quant-1-i].strip()
    out.append(a)

w.write('\n'.join(out))





