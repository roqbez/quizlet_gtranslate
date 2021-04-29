import re

import requests
import urllib
import csv
import json
import os
import re

USER_AGENT_GOOGLE_TRANSLATE = "com.google.Translate/6.14.59216 iSL/3.3 iPhone/14.2 hw/iPhone9_3 (gzip)"

def get_google_oauth_token(refresh_token):

    headers = {
        "User-Agent": USER_AGENT_GOOGLE_TRANSLATE,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    params = {
        "client_id": "936475272427.apps.googleusercontent.com",
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }

    with requests.post("https://www.googleapis.com/oauth2/v4/token",
                       headers=headers,
                       data=urllib.parse.urlencode(params)) as res:
        if res.status_code == 200:
            return res.json()['access_token']


def get_google_translate_oauth_token(user_oauth_token):

    headers = {
        "User-Agent": USER_AGENT_GOOGLE_TRANSLATE,
        "Authorization": "Bearer " + user_oauth_token,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    params = {
        "app_id": "com.google.Translate",
        "client_id": "1039733656850-2nfe3esd1tujdghpqr8adlu0cb7ar5vs.apps.googleusercontent.com",
        #       "device_id": "B42BB31F-4F00-40E4-AEFF-B9D27C145DEA",
        "hl": "pt-BR",
        "lib_ver": "3.3",
        "response_type": "token",
        "scope": "https://www.googleapis.com/auth/translate"
    }

    with requests.post("https://oauthaccountmanager.googleapis.com/v1/issuetoken",
                       headers=headers,
                       data=urllib.parse.urlencode(params)) as res:
        if res.status_code == 200:
            return res.json()['token']


def get_terms_from_google_translate(oauth_token):
    result = []

    headers = {
        "User-Agent": USER_AGENT_GOOGLE_TRANSLATE,
        "Authorization": "Bearer " + oauth_token
    }

    with requests.post("https://translate.google.com/translate_a/sg?client=at&cm=g&process=sync",
                       headers=headers) as res:

        i = 1

        if res.status_code == 200:
            for p in re.findall(r'\[("[^"]+","[^"]+","[^"]+","[^"]+","[^"]+",\d+)\]', res.text):
                s = p.split(',')
                source_language = s[1].replace('"', '')
                dest_language = s[2].replace('"', '')

                if source_language == "en":
                    term = s[3].replace('"', '')
                    translation = s[4].replace('"', '')
                elif source_language == "pt":
                    term = s[4].replace('"', '')
                    translation = s[3].replace('"', '')

                result.append({"term": term.lower().strip(), "translation": translation})

    return result


def get_terms_from_google_translate_sheet(sheet_id):
    result = []

    with requests.get(f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv", stream=True) as res:
        lines = (line.decode("UTF-8") for line in res.iter_lines(delimiter=b"\r\n"))

        for line in csv.reader(lines, delimiter=',', quotechar='"'):

            if line[0] == "Inglês":
                term = line[2]
                translation = line[3]
            elif line[0] == "Português":
                term = line[3]
                translation = line[2]

            translation = translation.replace("\n", " / ")

            result.append({"term": term.lower().strip(), "translation": translation})

        return result
