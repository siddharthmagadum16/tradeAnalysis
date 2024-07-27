import time
from auth import kite
from utils import changeDate, writeOp


# print(kite.profile())
# exit()

def getCandleColor(open, close):
  return 'G' if open < close else 'R'

def hasVolIncreased(dayVol, day1Vol):
  return dayVol < day1Vol

def getSuccessPer(greenTrades, redTrades):
  successPercent = int(round(100*greenTrades/(greenTrades + redTrades + 0.00001), 0))
  return successPercent

def getGRratio(greenTrades, redTrades):
  return round(greenTrades / (redTrades+0.1), 2)

def instruments():
  resp = kite.instruments(exchange=kite.EXCHANGE.NSE)
  writeOp(resp)
  return list(resp)
# instruments()

def getInstrumentToken(tradingSymbol):
  instrumentList = instruments()

  for instrumet in instrumentList:
    if (instrumet['tradingsymbol'] == tradingSymbol):
        return instrumet['instrument_token']
  return "no_instrument_found"



def historical(tradingSymbol, fromDate, toDate, interval):
  instrumentToken = getInstrumentToken(tradingSymbol)
  res = kite.historical_data(instrument_token=instrumentToken, from_date=fromDate, to_date=toDate, interval=interval)
  # writeOp(res)
  return res


def getAllPatternsForDays(days):
  ans = list()
  def solve(index, res):
    if (index == days):
      return ans.append(res)
    solve(index + 1, res + 'G')
    solve(index + 1, res + 'R')
  solve(0, "")
  return ans

def getVolPattern(hist):
  res = []
  for i in range(len(hist)-1):
    res.append('1' if hist[i]['volume'] < hist[i + 1]['volume'] else '0')
  return ''.join(res)

def getCandlePattern(hist):
  res = []
  for i in range(len(hist)):
    res.append(getCandleColor(hist[i]['open'], hist[i]['close']))
  return ''.join(res)

def getPattern(hist):
  volPattern = getVolPattern(hist)
  candlePattern = getCandlePattern(hist)
  pattern = candlePattern + volPattern
  return pattern

def findAllPatternResults(candles, tradingSymbol, fromDate, toDate, interval):

  hist = historical(tradingSymbol, fromDate, toDate, interval)
  # print('#candles', len(hist))
  data = dict()

  for i in range(len(hist) - candles - 1):

    pattern = getPattern(hist[i:i + candles])
    resultColor = getCandleColor(hist[i + candles]['open'], hist[i + candles]['close'])
    if pattern not in data:
      data[pattern] = { 'G': 0, 'R': 0 }

    if resultColor == 'G':
      data[pattern]['G'] += 1
    else:
      data[pattern]['R'] += 1

  for pattern in data:
    # data[pattern]['percent'] = round(100*data[pattern]['G'] / (data[pattern]['R'] + data[pattern]['G']))
    data[pattern]['pnl'] = data[pattern]['G'] - data[pattern]['R']
    data[pattern]['trades'] = data[pattern]['G'] + data[pattern]['R']
    data[pattern]['GRratio'] = getGRratio(data[pattern]['G'], data[pattern]['R'])
    data[pattern]['percent'] = getSuccessPer(data[pattern]['G'], data[pattern]['R'])
  data = dict(sorted(data.items(), key=lambda item: (item[1]['percent'], item[1]['pnl']), reverse=True))

  # print(data['GRRGR0110'])
  with open('./' + tradingSymbol + '.txt', 'w') as file:
    for pattern in data:
      file.write(pattern + ':' + str(data[pattern]) + '\n')
  return data


# findAllPatternResults(5, "TATAMOTORS", '2024-07-22', '2024-07-26', 'minute')

def backTest(candles, tradingSymbol, fromDate, toDate, histDays, minGRratio, minTrades):
  histStartDate = changeDate(fromDate, -histDays)
  histEndDate = changeDate(fromDate, -1)
  hist = historical(tradingSymbol, histStartDate, histEndDate, 'minute')
  time.sleep(1)
  data = findAllPatternResults(candles, tradingSymbol, fromDate, toDate, 'minute')
  cnt = 0
  results = { 'G': 0, 'R': 0 }
  for i in range(len(hist) - candles - 1):
    pattern = getPattern(hist[i:i + candles])
    # print(pattern)
    if pattern not in data:
      continue
    info = data[pattern]
    resultColor = getCandleColor(hist[i + candles]['open'], hist[i + candles]['close'])
    cnt += 1 if info['GRratio'] >= minGRratio else 0
    if (info['GRratio'] >= minGRratio and info['trades'] >= minTrades):
      results[resultColor] += 1
  print(results)
  grRatio = getGRratio(results['G'], results['R'])
  print('Success : ', grRatio)
  print(cnt)
  return results

backTest(4, 'TATAMOTORS', '2024-07-24', '2024-07-26', histDays=10, minGRratio=3, minTrades=5)




