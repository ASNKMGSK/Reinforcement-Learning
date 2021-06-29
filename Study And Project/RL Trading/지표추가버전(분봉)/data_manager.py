import pandas as pd
import numpy as np
import talib as ta
COLUMNS_CHART_DATA = ['date', 'open', 'high', 'low', 'close', 'volume']

COLUMNS_TRAINING_DATA_V1 = [
    'open_lastclose_ratio', 'high_close_ratio', 'low_close_ratio',
    'close_lastclose_ratio', 'volume_lastvolume_ratio',
    'close_ma5_ratio', 'volume_ma5_ratio',
    'close_ma10_ratio', 'volume_ma10_ratio',
    'close_ma20_ratio', 'volume_ma20_ratio',
    'close_ma60_ratio', 'volume_ma60_ratio',
    'close_ma120_ratio', 'volume_ma120_ratio',
    'aroon_up', 'aroon_down', 'vpci', 'vpcis5', 'vpcis20'
]

COLUMNS_TRAINING_DATA_V1_RICH = [
    'open_lastclose_ratio', 'high_close_ratio', 'low_close_ratio',
    'close_lastclose_ratio', 'volume_lastvolume_ratio',
    'close_ma5_ratio', 'volume_ma5_ratio',
    'close_ma10_ratio', 'volume_ma10_ratio',
    'close_ma20_ratio', 'volume_ma20_ratio',
    'close_ma60_ratio', 'volume_ma60_ratio',
    'close_ma120_ratio', 'volume_ma120_ratio',
    'inst_lastinst_ratio', 'frgn_lastfrgn_ratio',
    'inst_ma5_ratio', 'frgn_ma5_ratio',
    'inst_ma10_ratio', 'frgn_ma10_ratio',
    'inst_ma20_ratio', 'frgn_ma20_ratio',
    'inst_ma60_ratio', 'frgn_ma60_ratio',
    'inst_ma120_ratio', 'frgn_ma120_ratio',
]

COLUMNS_TRAINING_DATA_V2 = [
    'per', 'pbr', 'roe',
    'open_lastclose_ratio', 'high_close_ratio', 'low_close_ratio',
    'close_lastclose_ratio', 'volume_lastvolume_ratio',
    'close_ma5_ratio', 'volume_ma5_ratio',
    'close_ma10_ratio', 'volume_ma10_ratio',
    'close_ma20_ratio', 'volume_ma20_ratio',
    'close_ma60_ratio', 'volume_ma60_ratio',
    'close_ma120_ratio', 'volume_ma120_ratio',
    'market_kospi_ma5_ratio', 'market_kospi_ma20_ratio',
    'market_kospi_ma60_ratio', 'market_kospi_ma120_ratio',
    'bond_k3y_ma5_ratio', 'bond_k3y_ma20_ratio',
    'bond_k3y_ma60_ratio', 'bond_k3y_ma120_ratio'
]


def preprocess(data, ver='v1'):
    windows = [5, 10, 20, 60, 120]
    for window in windows:
        data['close_ma{}'.format(window)] = \
            data['close'].rolling(window).mean()
        data['volume_ma{}'.format(window)] = \
            data['volume'].rolling(window).mean()
        data['close_ma%d_ratio' % window] = \
            (data['close'] - data['close_ma%d' % window]) \
            / data['close_ma%d' % window]
        data['volume_ma%d_ratio' % window] = \
            (data['volume'] - data['volume_ma%d' % window]) \
            / data['volume_ma%d' % window]

        if ver == 'v1.rich':
            data['inst_ma{}'.format(window)] = \
                data['close'].rolling(window).mean()
            data['frgn_ma{}'.format(window)] = \
                data['volume'].rolling(window).mean()
            data['inst_ma%d_ratio' % window] = \
                (data['close'] - data['inst_ma%d' % window]) \
                / data['inst_ma%d' % window]
            data['frgn_ma%d_ratio' % window] = \
                (data['volume'] - data['frgn_ma%d' % window]) \
                / data['frgn_ma%d' % window]

    data['open_lastclose_ratio'] = np.zeros(len(data))
    data.loc[1:, 'open_lastclose_ratio'] = \
        (data['open'][1:].values - data['close'][:-1].values) \
        / data['close'][:-1].values
    data['high_close_ratio'] = \
        (data['high'].values - data['close'].values) \
        / data['close'].values
    data['low_close_ratio'] = \
        (data['low'].values - data['close'].values) \
        / data['close'].values
    data['close_lastclose_ratio'] = np.zeros(len(data))
    data.loc[1:, 'close_lastclose_ratio'] = \
        (data['close'][1:].values - data['close'][:-1].values) \
        / data['close'][:-1].values
    data['volume_lastvolume_ratio'] = np.zeros(len(data))
    data.loc[1:, 'volume_lastvolume_ratio'] = \
        (data['volume'][1:].values - data['volume'][:-1].values) \
        / data['volume'][:-1] \
            .replace(to_replace=0, method='ffill') \
            .replace(to_replace=0, method='bfill').values
    data['aroon_down'], data['aroon_up'] = ta.AROON(data['high'], data['low'], timeperiod=25)

    if ver == 'v1.rich':
        data['inst_lastinst_ratio'] = np.zeros(len(data))
        data.loc[1:, 'inst_lastinst_ratio'] = \
            (data['inst'][1:].values - data['inst'][:-1].values) \
            / data['inst'][:-1] \
                .replace(to_replace=0, method='ffill') \
                .replace(to_replace=0, method='bfill').values
        data['frgn_lastfrgn_ratio'] = np.zeros(len(data))
        data.loc[1:, 'frgn_lastfrgn_ratio'] = \
            (data['frgn'][1:].values - data['frgn'][:-1].values) \
            / data['frgn'][:-1] \
                .replace(to_replace=0, method='ffill') \
                .replace(to_replace=0, method='bfill').values

    return data

def VPCI(data, s, l, ver='v1'):
    data['vpci'] = data['close']*data['volume']
    data['vpci'] = (((data['vpci'].rolling(l).sum())/data['volume'].rolling(l).sum())-data['close'].rolling(l).mean())*(((data['vpci'].rolling(s).sum())/data['volume'].rolling(s).sum())/data['close'].rolling(s).mean())*(data['volume'].rolling(s).mean()/data['volume'].rolling(l).mean())
    return data

def VPCIS(data, ver='v1'):
    data['vpcis5'] = data['vpci'] * data['volume']
    data['vpcis20'] = data['vpci'] * data['volume']
    data['vpcis5'] = (data['vpcis5'].rolling(5).sum())/data['volume'].rolling(5).sum()
    data['vpcis20'] = (data['vpcis20'].rolling(2).sum())/data['volume'].rolling(20).sum()
    return data

def load_data(fpath, date_from, date_to, ver='v2'):
    header = None if ver == 'v1' else 0
    data = pd.read_csv(fpath, thousands=',', header=header,
                       converters={'date': lambda x: str(x)})

    if ver == 'v1':
        data.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    print("---column한후-----")
    print(data)
    # 날짜 오름차순 정렬
    data = data.sort_values(by='date').reset_index()
    print("---오름차순한후-----")
    print(data)
    # 데이터 전처리
    data = preprocess(data)
    print("---전처리후-----")
    print(data)
    data = VPCI(data, 3, 5)
    print("==VPCI==")
    print(data)
    data = VPCIS(data)
    print("==VPCIS==")
    print(data)
    data['date'] = data['date'].astype(str)
    # 기간 필터링
    data['date'] = data['date'].str.replace('-', '')
    data['date'] = data['date'].str.replace(':', '')
    data['date'] = data['date'].str.replace('PM', '')
    data['date'] = data['date'].str.replace('AM', '')
    data['date'] = data['date'].str.replace('  9', '09')
    data['date'] = data['date'].str.replace('  ', '')
    data = data[(data['date'] >= date_from) & (data['date'] <= date_to)]
    data = data.dropna()
    print("---필터링후-----")
    print(data)

    # 차트 데이터 분리
    chart_data = data[COLUMNS_CHART_DATA]
    print("---차트데이터 분리후-----")
    print(chart_data)

    # 학습 데이터 분리
    training_data = None
    if ver == 'v1':
        training_data = data[COLUMNS_TRAINING_DATA_V1]
    elif ver == 'v1.rich':
        training_data = data[COLUMNS_TRAINING_DATA_V1_RICH]
    elif ver == 'v2':
        data.loc[:, ['per', 'pbr', 'roe']] = \
            data[['per', 'pbr', 'roe']].apply(lambda x: x / 100)
        training_data = data[COLUMNS_TRAINING_DATA_V2]
        training_data = training_data.apply(np.tanh)
    else:
        raise Exception('Invalid version.')

    return chart_data, training_data
