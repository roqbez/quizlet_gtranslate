import json
import urllib
import requests


def get_quizlet_default_headers(oauth_token):
    return {
        "X-QUIZLET-DEVICE-ID": ".....",
        "User-Agent": "QuizletIOS/5.7.2 (QuizletBuild/3; iPhone9,3; iOS 14.2; Scale/2.0)",
        "Authorization": f"Bearer {oauth_token}"
    }


def get_quizlet_set_terms(oauth_token, set_id):
    terms_list = []

    page = 1
    paging_token = None
    per_page = 100

    while True:

        params = {
            "filters[setId]": set_id,
            "include[term][]": "definitionImage",
            "include[term][]": "wordCustomAudio",
            "include[term][]": "definitionCustomAudio",
            "include[term][set][]": "creator",
            "perPage": str(per_page)
        }

        if page > 1:
            params['page'] = page

        if paging_token is not None:
            params['pagingToken'] = paging_token

        repeated_terms = set()

        with requests.get("https://api.quizlet.com/3.5/terms?" + urllib.parse.urlencode(params),
                          headers=get_quizlet_default_headers(oauth_token)) as res:
            if res.status_code == 200:
                json_resp = res.json()['responses'][0]

                terms = json_resp['models']['term']

                # Checking and warning duplicates
                for s in terms_list:
                    if not s.get("isDeleted"):
                        w = s['word'].lower()
                        if w in repeated_terms:
                            print(f"Warning: term '{w}' is duplicated in Quizlet")
                        else:
                            repeated_terms.add(w)

                terms_list.extend(terms)

                paging = json_resp['paging']
                total = paging['total']
                per_page = paging['perPage']
                paging_token = paging['token']

                if len(terms_list) < total:
                    page += 1
                else:
                    break
            else:
                break

    terms_list = list(filter(lambda s: not s.get("isDeleted"), terms_list))

    return {s['word'].lower().strip(): s['definition'] for s in terms_list}


def add_quizlet_set_term(oauth_token, set_id, term_name, term_translation, rank_posi=0):
    headers = get_quizlet_default_headers(oauth_token)
    headers["Content-Type"] = "application/json"

    payload = {
        "data": [
            {
                "setId": set_id,
                "isDeleted": 0,
                "word": term_name,
                "definition": term_translation,
                "rank": rank_posi,
            }
        ],
        "include": {}
    }

    with requests.post("https://api.quizlet.com/3.5/terms/save",
                       headers=headers,
                       data=json.dumps(payload)) as res:
        if res.status_code == 200:
            print(f'Added term {term_name} --> {term_translation} at position {rank_posi}')
        else:
            print(res.text)
