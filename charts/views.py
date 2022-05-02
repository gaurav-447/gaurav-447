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
    def get(self, request, *args, **kwargs):
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

    def get(self, request):
        labels = []
        default_items = {"PE": [], "CE": []}

        labels_next_week = []
        default_items_next_week = {"PE": [], "CE": []}

        change_in_open_interest_pe_next_week = 1
        change_in_open_interest_ce_next_week = 1

        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/61.0.3163.100 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-US,en;q=0.9,hi;q=0.8'}
        url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'}  # This is chrome, you can set whatever browser you like

        proxies = {
              "https" : "bgproxy.bajajallianz.com:8080"
            }
        json_obj = requests.get(url, headers=headers, proxies=proxies, verify=False).json()

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
                change_in_open_interest_pe += key["PE"]["changeinOpenInterest"]
                change_in_open_interest_ce += key["CE"]["changeinOpenInterest"]
            if key["expiryDate"] == expiry_next_week.strftime("%d-%b-%Y") \
                    and underlying_value + 500 >= key["strikePrice"] >= underlying_value - 500:
                labels_next_week.append(key["PE"]["strikePrice"])
                default_items_next_week["PE"].append(key["PE"]["changeinOpenInterest"])
                default_items_next_week["CE"].append(key["CE"]["changeinOpenInterest"])
                change_in_open_interest_pe_next_week += key["PE"]["changeinOpenInterest"]
                change_in_open_interest_ce_next_week += key["CE"]["changeinOpenInterest"]
        pcr = change_in_open_interest_pe / change_in_open_interest_ce
        pcr_next_week = change_in_open_interest_pe_next_week / change_in_open_interest_ce_next_week
        print("PPCCRR", pcr)
        print(pcr_next_week)
        data = {
            "labels": labels,
            "default": default_items,
            "pcr": pcr,
            "labelsnw": labels_next_week,
            "defaultnw": default_items_next_week,
            "pcrnw": pcr_next_week,
            "ltp": underlying_value
        }
        return Response(data)
