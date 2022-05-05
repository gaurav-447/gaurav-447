from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import View
import requests
from rest_framework.views import APIView
from rest_framework.response import Response

User = get_user_model()


class HomeView(View):
    @staticmethod
    def get(request, *args, **kwargs):
        return render(request, 'charts.html', {"customers": 10})


def get_data(request, *args, **kwargs):
    data = {
        "sales": 100,
        "customers": 10,
    }
    return JsonResponse(data)  # http response


class ChartData(APIView):
    authentication_classes = []
    permission_classes = []

    @staticmethod
    def get(request):
        json_obj = ChartData.get_nifty()
        nifty_data = ChartData.filter_nifty(json_obj)

        bn_json_obj = ChartData.get_bank_nifty()
        bank_nifty_data = ChartData.filter_bank_nifty(bn_json_obj)
        data = {
            "nifty_data": nifty_data,
            "bank_nifty_data": bank_nifty_data
        }
        return Response(data)

    @staticmethod
    def get_nifty():
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/61.0.3163.100 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8'}
        url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
        json_obj = requests.get(url, headers=headers).json()
        return json_obj

    @staticmethod
    def get_bank_nifty():
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/61.0.3163.100 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8'}
        url = "https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY"
        json_obj = requests.get(url, headers=headers).json()
        return json_obj

    @staticmethod
    def filter_nifty(json_obj):
        labels = []
        default_items = {"PE": [], "CE": []}
        print("in get")
        labels_next_week = []
        default_items_next_week = {"PE": [], "CE": []}
        change_in_open_interest_pe_next_week = 1
        change_in_open_interest_ce_next_week = 1
        underlying_value = json_obj["records"]["underlyingValue"]
        change_in_open_interest_pe = 1
        change_in_open_interest_ce = 1
        now = datetime.now()
        expiry = now - timedelta(days=now.weekday()) + timedelta(days=3)
        expiry_next_week = now - timedelta(days=now.weekday()) + timedelta(days=10)
        print("expiry", expiry.strftime("%d-%b-%Y"))
        print(expiry_next_week.strftime("%d-%b-%Y"))
        for key in json_obj["records"]["data"]:
            if key["expiryDate"] == expiry.strftime("%d-%b-%Y") \
                    and underlying_value + 500 >= key["strikePrice"] >= underlying_value - 500:
                labels.append(key["PE"]["strikePrice"])
                default_items["PE"].append(key["PE"]["changeinOpenInterest"])
                default_items["CE"].append(key["CE"]["changeinOpenInterest"])

            if key["expiryDate"] == expiry.strftime("%d-%b-%Y"):
                change_in_open_interest_pe += abs(key["PE"]["changeinOpenInterest"])
                change_in_open_interest_ce += abs(key["CE"]["changeinOpenInterest"])

            if key["expiryDate"] == expiry_next_week.strftime("%d-%b-%Y") \
                    and underlying_value + 500 >= key["strikePrice"] >= underlying_value - 500:
                labels_next_week.append(key["PE"]["strikePrice"])
                default_items_next_week["PE"].append(key["PE"]["changeinOpenInterest"])
                default_items_next_week["CE"].append(key["CE"]["changeinOpenInterest"])

            if key["expiryDate"] == expiry_next_week.strftime("%d-%b-%Y"):
                change_in_open_interest_pe_next_week += abs(key["PE"]["changeinOpenInterest"])
                change_in_open_interest_ce_next_week += abs(key["CE"]["changeinOpenInterest"])

        pcr = change_in_open_interest_pe / change_in_open_interest_ce
        pcr_next_week = change_in_open_interest_pe_next_week / change_in_open_interest_ce_next_week
        print("PPCCRR", pcr)
        print(pcr_next_week)
        data = {
            "expiry": expiry.strftime("%d-%b-%Y"),
            "expiry_next_week": expiry_next_week.strftime("%d-%b-%Y"),
            "expiry_data": {"labels": labels,
                            "default": default_items,
                            "pcr": pcr},
            "expiry_next_week_data": {"labelsnw": labels_next_week,
                                      "defaultnw": default_items_next_week,
                                      "pcrnw": pcr_next_week},
            "ltp": underlying_value
        }
        return data

    @staticmethod
    def filter_bank_nifty(json_obj):
        labels = []
        default_items = {"PE": [], "CE": []}
        print("in get")
        labels_next_week = []
        default_items_next_week = {"PE": [], "CE": []}
        change_in_open_interest_pe_next_week = 1
        change_in_open_interest_ce_next_week = 1
        underlying_value = json_obj["records"]["underlyingValue"]
        change_in_open_interest_pe = 1
        change_in_open_interest_ce = 1
        now = datetime.now()
        expiry = now - timedelta(days=now.weekday()) + timedelta(days=3)
        expiry_next_week = now - timedelta(days=now.weekday()) + timedelta(days=10)
        print("expiry", expiry.strftime("%d-%b-%Y"))
        print(expiry_next_week.strftime("%d-%b-%Y"))
        for key in json_obj["records"]["data"]:
            if key["expiryDate"] == expiry.strftime("%d-%b-%Y") \
                    and underlying_value + 1000 >= key["strikePrice"] >= underlying_value - 1000:
                labels.append(key["PE"]["strikePrice"])
                default_items["PE"].append(key["PE"]["changeinOpenInterest"])
                default_items["CE"].append(key["CE"]["changeinOpenInterest"])

            if key["expiryDate"] == expiry.strftime("%d-%b-%Y"):
                change_in_open_interest_pe += abs(key["PE"]["changeinOpenInterest"])
                change_in_open_interest_ce += abs(key["CE"]["changeinOpenInterest"])

            if key["expiryDate"] == expiry_next_week.strftime("%d-%b-%Y") \
                    and underlying_value + 1000 >= key["strikePrice"] >= underlying_value - 1000:
                labels_next_week.append(key["PE"]["strikePrice"])
                default_items_next_week["PE"].append(key["PE"]["changeinOpenInterest"])
                default_items_next_week["CE"].append(key["CE"]["changeinOpenInterest"])

            if key["expiryDate"] == expiry_next_week.strftime("%d-%b-%Y"):
                change_in_open_interest_pe_next_week += abs(key["PE"]["changeinOpenInterest"])
                change_in_open_interest_ce_next_week += abs(key["CE"]["changeinOpenInterest"])

        pcr = change_in_open_interest_pe / change_in_open_interest_ce
        pcr_next_week = change_in_open_interest_pe_next_week / change_in_open_interest_ce_next_week
        print("PPCCRR", pcr)
        print(pcr_next_week)
        data = {
            "expiry": expiry.strftime("%d-%b-%Y"),
            "expiry_next_week": expiry_next_week.strftime("%d-%b-%Y"),
            "expiry_data": {"labels": labels,
                            "default": default_items,
                            "pcr": pcr},
            "expiry_next_week_data": {"labelsnw": labels_next_week,
                                      "defaultnw": default_items_next_week,
                                      "pcrnw": pcr_next_week},
            "ltp": underlying_value
        }
        return data