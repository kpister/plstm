import random

neg = open('text/neg.txt').read().split('\n')
pos = open('text/pos.txt').read().split('\n')


quant = 500000
w = open('text/blended.txt', 'w')

for k in range(10):
    out = []
    nw = random.sample(neg, quant)
    pw = random.sample(pos, quant)
    for i in range(quant):
        out.append(f'{nw[i].strip()} {pw[i].strip()}')
        out.append(f'{pw[i].strip()} {nw[quant-1-i].strip()}')
    w.write('\n'.join(out))





