import numpy as np
import talib as ta
import matplotlib.pyplot as plt

#close = np.random.random(100)

close = np.random.randint(50000, 60000, 100)
close = np.array(close, dtype=float)
print(close)

ma5 = ta.SMA(close, 5)
ma10 = ta.SMA(close, 10)

rsi14 = ta.SMA(close, timeperiod=14)
macd, macdsignal, macdhist = ta.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)

print(ma5)
print(ma10)

print(ma5[0])
print(ma10[0])

# last array
print(ma5[-1])
print(ma10[-1])
print(rsi14[-1])

for i in range(len(macd)) :
    print("macd macdsignal machhist", i, close[i], macd[i], macdsignal[i], macdhist[i])

plt.figure(figsize=(11,3))
plt.plot(close, "r-")
plt.plot(ma5, "b-")
plt.show()
