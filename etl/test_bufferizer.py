from datatypes.cache import ForwardOnceCache


test_series = [
    [
        { 'ts': 1, 'data': '1f' },
        { 'ts': 2, 'data': '1f' },
        { 'ts': 3, 'data': '1f' },
        { 'ts': 6, 'data': '1f' },
        { 'ts': 7, 'data': '1f' },
    ],
    [
        { 'ts': 3, 'data': '1f' },
        { 'ts': 4, 'data': '1f' },
        { 'ts': 6, 'data': '1f' },
        { 'ts': 8, 'data': '1f' },
        { 'ts': 10, 'data': '1f' },
    ],
    [
        { 'ts': 11, 'data': '1f' },
        { 'ts': 12, 'data': '1f' },
        { 'ts': 13, 'data': '1f' },
        { 'ts': 14, 'data': '1f' },
        { 'ts': 15, 'data': '1f' },
    ]
]

test_cryptowatch = [{'price': 10594.48, 'timestamp': 1563618597, 'volume': 0.00464568}, {'price': 10601.95, 'timestamp': 1563618601, 'volume': 0.00449967}, {'price': 10601.26, 'timestamp': 1563618618, 'volume': 0.00431845}, {'price': 10597.37, 'timestamp': 1563618621, 'volume': 0.00431845}, {'price': 10597.39, 'timestamp': 1563618621, 'volume': 0.00602036}, {'price': 10597.39, 'timestamp': 1563618621, 'volume': 0.00820596}, {'price': 10598.75, 'timestamp': 1563618635, 'volume': 0.01704099}, {
    'price': 10598.18, 'timestamp': 1563618647, 'volume': 0.00272364}, {'price': 10598.6, 'timestamp': 1563618660, 'volume': 0.00220718}, {'price': 10602.29, 'timestamp': 1563618662, 'volume': 0.00602036}, {'price': 10602.3, 'timestamp': 1563618662, 'volume': 0.32343777}, {'price': 10602.3, 'timestamp': 1563618662, 'volume': 0.00309907}, {'price': 10604.07, 'timestamp': 1563618669, 'volume': 0.00262965}, {'price': 10604.05, 'timestamp': 1563618711, 'volume': 0.01353468}]


a = ForwardOnceCache('ts')

for data in test_series:
    result = a.work(data)
    print(result)