import os
import gtranslate
import os
import quizlet

if __name__ == '__main__':

    QUIZLET_OAUTH_TOKEN = os.getenv("QUIZLET_OAUTH_TOKEN")
    QUIZLET_SET_ID = os.getenv("QUIZLET_SET_ID")

    if QUIZLET_OAUTH_TOKEN is None:
        raise ValueError("Environment variable QUIZLET_OAUTH_TOKEN is required")

    if QUIZLET_SET_ID is None:
        raise ValueError("Environment variable QUIZLET_SET_ID is required")

    GOOGLE_OAUTH_REFRESH_TOKEN = os.getenv("GOOGLE_OAUTH_REFRESH_TOKEN")

    if GOOGLE_OAUTH_REFRESH_TOKEN is None:
        raise ValueError("Environment variable GOOGLE_OAUTH_REFRESH_TOKEN is required")

    # GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
    #
    # if GOOGLE_SHEET_ID is None:
    #     raise ValueError("Environment variable GOOGLE_SHEET_ID is required")

    quizlet_terms = quizlet.get_quizlet_set_terms(QUIZLET_OAUTH_TOKEN, QUIZLET_SET_ID)

    print(f"There are {len(quizlet_terms)} terms in Quizlet set {QUIZLET_SET_ID}")

    oauth_token = gtranslate.get_google_oauth_token(GOOGLE_OAUTH_REFRESH_TOKEN)

    gtranslate_token = gtranslate.get_google_translate_oauth_token(oauth_token)
    gtranslate_terms = gtranslate.get_terms_from_google_translate(gtranslate_token)
    # gtranslate_terms = get_terms_from_google_translate_sheet(GOOGLE_SHEET_ID)

    print(f"There are {len(gtranslate_terms)} terms in Google Translate Phrasebook")

    new_terms = [t for t in filter(lambda t: quizlet_terms.get(t["term"]) is None, gtranslate_terms)]

    print(f"There are {len(new_terms)} new terms to add to Quizlet: {new_terms}")

    #exit(0)

    rank = len(quizlet_terms)

    for t in new_terms:
        quizlet.add_quizlet_set_term(QUIZLET_OAUTH_TOKEN, QUIZLET_SET_ID, t['term'], t['translation'], rank)
        rank += 1
