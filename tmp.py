lis1 = ['RGGR110','RRRG101','GGRG000','GGRG010','GRRG010','RGGG010','RRGR010','GRRG101','GRGG001','RGRG010','RGRR100','RRGR011','GGGG100','GGRR101','RRRG011','GRGG100','RRRR011','RRRR110','RRGG001']
lis2 = ['GGGG101','GRGG011','RRRR010','GGGR110','RGRR010','GGGG010','RGRG010','RRRG011','GRRR101','GGRR100','GGRG101','GRRG100','GGRG110','GRRR111','RRRG101','RGRR001','GRGG001','RRGG110','RGGG101','RRGR001','RRRG110','RGGG000','GGGR000','GRGR011','RRGG011','RGGR011','GRGG101','GGRG011','RGGR111','GGRR011','RGRR101','GGGG110','GGGR001','GRRR110','RRGR101','RGRR100','GGGR010','RRGR010','RRGR111','GRGR101','RGRG011','RGGR100','RGGR110','RRRR111','GGGG001']

lisLoss = list(set(lis2) - set(lis1))
lisProfit = list(set(lis1) & set(lis2))

print('profit', lisProfit)
print('loss', lisLoss)