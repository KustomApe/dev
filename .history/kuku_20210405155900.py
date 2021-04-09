# mt = [[None]*9]*9
mt = [[None] * 9 for i in range(9)]
for i in range(9):
    for j in range(9):
        mt[i][j] = (i+1) * (j+1)
        print("%1d " % (mt[i][j]), end=" ")
    # print("1の段の配列 = %s" % mt[0])