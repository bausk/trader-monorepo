import requests


def get_UAH_rate(currency="USD"):
    response = requests.get('https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=3').json()
    result = next((x for x in response if x['ccy'] == currency), 0.0)
    rate = float((float(result['buy']) + float(result['sale'])) / 2)
    return rate
