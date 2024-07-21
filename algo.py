from auth import kite
import datetime
import numpy as np
import pandas as pd


# print(kite.profile())

def getCandleColor(open, close):
  # green=1, red=0
  return 'G' if open < close else 'R'

def hasVolIncreased(dayVol, day1Vol):
  return dayVol < day1Vol

def getPatternIndex(dayColorCode, day1ColorCode):
  res = ("G" if dayColorCode else "R") + ("G" if day1ColorCode else "R");
  return res

def writeOp(data):
  with open('./output-reliance.txt', 'w') as file:
    file.write(str(data))



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



def historical(tradingSymbol):
  instrumentToken = getInstrumentToken(tradingSymbol)
  res = kite.historical_data(instrument_token=instrumentToken, from_date='2024-06-26', to_date='2024-06-28', interval='minute')
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



def findAllPatternResults(days, tradingSymbol=""):

  patterns = getAllPatternsForDays(days)
  # print(patterns)


  hist = historical(tradingSymbol)
  data = dict()

  for i in range(len(hist) - days - 1):
    endPos = i + days
    volPattern = getVolPattern(hist[i:endPos])
    candlePattern = getCandlePattern(hist[i:endPos])


    resultColor = getCandleColor(hist[i + days]['open'], hist[i + days]['close'])
    pattern = candlePattern + volPattern
    if pattern not in data:
      data[pattern] = { 'G': 0, 'R': 0, 'net': 0 }

    if resultColor == 'G':
      data[pattern]['G'] += 1
      data[pattern]['net'] += 1
    else:
      data[pattern]['R'] += 1
      data[pattern]['net'] -= 1

  for pattern in data:
    data[pattern]['percent'] = round(100*data[pattern]['G'] / (data[pattern]['R'] + data[pattern]['G']))
  data = dict(sorted(data.items(), key=lambda item: item[1]['percent'], reverse=True))

  # writeOp(data)
  with open('./output_' + tradingSymbol + '.txt', 'w') as file:
    for pattern in data:
      file.write(pattern + ':' + str(data[pattern]) + '\n')


findAllPatternResults(3, "RELIANCE")

