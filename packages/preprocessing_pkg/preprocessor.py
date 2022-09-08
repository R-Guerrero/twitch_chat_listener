from bs4 import BeautifulSoup
import contractions
import emoji
from functools import reduce
import numpy as np
from num2words import num2words
import re
from string import punctuation
import unicodedata


SLANGS = {
    "$": " dollar ",
    "€": " euro ",
    "4ao": "for adults only",
    "a.m": "before midday",
    "a3": "anytime anywhere anyplace",
    "aamof": "as a matter of fact",
    "acct": "account",
    "adih": "another day in hell",
    "afaic": "as far as concerned",
    "afaict": "as far as i can tell",
    "afaik": "as far as i know",
    "afair": "as far as i remember",
    "afk": "away from keyboard",
    "app": "application",
    "approx": "approximately",
    "apps": "applications",
    "asap": "as soon as possible",
    "asl": "age, sex, location",
    "atk": "at the keyboard",
    "ave.": "avenue",
    "aymm": "are you my mother",
    "ayor": "at your own risk",
    "b&b": "bed and breakfast",
    "b+b": "bed and breakfast",
    "b.c": "before christ",
    "b2b": "business to business",
    "b2c": "business to customer",
    "b4": "before",
    "b4n": "bye for now",
    "b@u": "back at you",
    "bae": "before anyone else",
    "bak": "back at keyboard",
    "bbbg": "bye bye be good",
    "bbc": "british broadcasting corporation",
    "bbias": "be back in a second",
    "bbl": "be back later",
    "bbs": "be back soon",
    "be4": "before",
    "bfn": "bye for now",
    "blvd": "boulevard",
    "bout": "about",
    "brb": "be right back",
    "bros": "brothers",
    "brt": "be right there",
    "bsaaw": "big smile and a wink",
    "btw": "by the way ",
    "bwl": "bursting with laughter",
    "c/o": "care of",
    "cet": "central european time",
    "cf": "compare",
    "cia": "central intelligence agency",
    "csl": "can not stop laughing",
    "cu": "see you",
    "cul8r": "see you later",
    "cv": "curriculum vitae",
    "cwot": "complete waste of time",
    "cya": "see you",
    "cyt": "see you tomorrow",
    "dae": "does anyone else",
    "dbmib": "do not bother me busy",
    "diy": "do it yourself",
    "dm": "direct message",
    "dwh": "during work hours",
    "e123": "easy as one two three",
    "eet": "eastern european time",
    "eg": "example",
    "embm": "early morning business meeting",
    "encl": "enclosed",
    "encl.": "enclosed",
    "etc": "and so on",
    "faq": "frequently asked questions",
    "fawc": "for anyone who cares",
    "fb": "facebook",
    "fc": "fingers crossed",
    "fig": "figure",
    "fimh": "forever in my heart",
    "ft.": "feet",
    "ft": "featuring",
    "ftl": "for the loss",
    "ftw": "for the win",
    "fwiw": "for what it is worth",
    "fyi": "for your information",
    "g9": "genius",
    "gahoy": "get a hold of yourself",
    "gal": "get a life",
    "gcse": "general certificate of secondary education",
    "gfn": "gone for now",
    "gg": "good game",
    "gl": "good luck",
    "glhf": "good luck have fun",
    "gmt": "greenwich mean time",
    "gmta": "great minds think alike",
    "gn": "good night",
    "g.o.a.t": "greatest of all time",
    "goat": "greatest of all time",
    "goi": "get over it",
    "gps": "global positioning system",
    "gr8": "great",
    "gratz": "congratulations",
    "gyal": "girl",
    "h&c": "hot and cold",
    "hp": "horsepower",
    "hr": "hour",
    "hrh": "his royal highness",
    "ht": "height",
    "ibrb": "i will be right back",
    "ic": "i see",
    "icq": "i seek you",
    "icymi": "in case you missed it",
    "idc": "i do not care",
    "idgadf": "i do not give a damn fuck",
    "idgaf": "i don't give a freak",
    "idk": "i do not know",
    "ie": "that is",
    "i.e": "that is",
    "ifyp": "i feel your pain",
    "IG": "instagram",
    "iirc": "if i remember correctly",
    "ilu": "i love you",
    "ily": "i love you",
    "imho": "in my humble opinion",
    "imo": "in my opinion",
    "imu": "i miss you",
    "iow": "in other words",
    "irl": "in real life",
    "j4f": "just for fun",
    "jic": "just in case",
    "jk": "just kidding",
    "jsyk": "just so you know",
    "l8r": "later",
    "lb": "pound",
    "lbs": "pounds",
    "ldr": "long distance relationship",
    "lmao": "laugh my ass off",
    "lmfao": "laughing my freaking ass off",
    "lol": "i am laughing",
    "ltd": "limited",
    "ltns": "long time no see",
    "m8": "mate",
    "mf": "motherfucker",
    "mfs": "motherfuckers",
    "mfw": "my face when",
    "mofo": "motherfucker",
    "mph": "miles per hour",
    "mr": "mister",
    "mrw": "my reaction when",
    "ms": "miss",
    "mte": "my thoughts exactly",
    "nagi": "not a good idea",
    "nbc": "national broadcasting company",
    "nbd": "no big deal",
    "nfs": "not for sale",
    "ngl": "not going to lie",
    "nhs": "national health service",
    "nrn": "no reply necessary",
    "nsfl": "not safe for life",
    "nsfw": "not safe for work",
    "nth": "nice to have",
    "nvr": "never",
    "nyc": "new york city",
    "oc": "original content",
    "og": "original gangster",
    "ohp": "overhead projector",
    "oic": "oh i see",
    "omdb": "over my dead body",
    "omg": "oh my god",
    "omw": "on my way",
    "p.a": "per annum",
    "p.m": "after midday",
    "pm": "private message",
    "poc": "people of color",
    "pov": "point of view",
    "pp": "pages",
    "ppl": "people",
    "prw": "parents are watching",
    "ps": "postscript",
    "pt": "point",
    "ptb": "please text back",
    "pto": "please turn over",
    "qpsa": "what happens",
    "ratchet": "rude",
    "rbtl": "read between the lines",
    "rlrt": "real life retweet",
    "rofl": "i am laughing",
    "roflol": "rolling on the floor laughing out loud",
    "rotflmao": "rolling on the floor laughing my ass off",
    "rt": "retweet",
    "ruok": "are you ok",
    "sfw": "safe for work",
    "sk8": "skate",
    "smh": "shake my head",
    "sq": "square",
    "srsly": "seriously",
    "ssdd": "same stuff different day",
    "tbh": "to be honest",
    "tbs": "tablespooful",
    "tbsp": "tablespooful",
    "tfw": "that feeling when",
    "thks": "thank you",
    "tho": "though",
    "thx": "thanks",
    "tia": "thanks in advance",
    "til": "today i learned",
    "tl;dr": "too long i did not read",
    "tldr": "too long i did not read",
    "tmb": "tweet me back",
    "tntl": "trying not to laugh",
    "ttyl": "talk to you later",
    "u2": "you too",
    "u4e": "yours for ever",
    "utc": "coordinated universal time",
    "w/": "with",
    "w/o": "without",
    "w8": "wait",
    "wassup": "what is up",
    "wb": "welcome back",
    "wtf": "what the freak",
    "wtg": "way to go",
    "wtpa": "where the party at",
    "wuf": "where are you from",
    "wuzup": "what is up",
    "wywh": "wish you were here",
    "yd": "yard",
    "ygtr": "you got that right",
    "ynk": "you never know",
    "zzz": "sleeping bored and tired",
    "ty": "thank you",
    "imy": "i miss you",
    "yolo": "you only live once",
    "fomo": "fear of missing out",
    "ffs": "for freaks sake",
    "w": "with",
    "abt": "about",
    "r": "are",
    "gtg": "going to go",
    "nvm": "never mind",
    "bcoz": "because",
    "coz": "because",
    "bcos": "because",
    "cld": "could",
    "ez": "easy",
    "fbm": "fine by me",
    "ik": "i know",
    "wfh": "work from home",
    "lmk": "let me know",
    "af": "as freak",
    "aight": "alright",
    "awol": "away without leaving",
    "irl ": "in real life",
    "bt": "bad trip",
    "bb": "baby",
    "dgaf": "don't give a freak",
    "tf": "the freak ",
    "dis": "this",
    "dnt": "don't ",
    "dw": "don't worry",
    "enf": "enough",
    "eta": "estimated time of arrival",
    "fu": "freak you",
    "fwm": "fine with me",
    "gm": "good morning",
    "grl": "girl",
    "grw": "get ready with me",
    "h8": "hate",
    "hbd": "happy birthday",
    "hbu": "how about you",
    "hru": "how are you",
    "hw": "homework",
    "idts": "i don't think so",
    "ig": "instagram",
    "ilysm": "i love you so much",
    "k": "okay",
    "l2g": "like to go",
    "ly": "love you",
    "nm": "nothing much",
    "np": "no problem",
    "nw": "no way",
    "ofc": "ofcourse",
    "omfg": "oh my freaking god",
    "ootd": "outfit of the day",
    "otb": "off to bed",
    "otw": "off to work",
    "prob": "probably",
    "qt": "cutie",
    "rly": "really",
    "sh": "same here",
    "sis": "sister",
    "bro": "brother",
    "sry": "sorry",
    "sup": "what's up",
    "thnk": "thank you",
    "ttly": "totally",
    "ur": "you are",
    "whatevs": "whatever",
    "wyd": "what are you doing",
    "wdyk": "what do you know",
    "wru": "where are you",
    "xoxo": "hugs and kisses",
    "xo": "hugs and kisses",
    "y": "why",
    "tryna": "trying to be",
}

# Dictionary sorted by value name lenght.
SLANGS = {slang: SLANGS[slang] for slang in sorted(SLANGS, key=len, reverse=True)}

# from emot.emo_unicode import EMOTICONS_EMO
EMOTICONS = {
    "D‑':": "i am horrified",
    ";‑]": "i am winking",
    "(^O^)／": "i am full of joy",
    "(^o^)": "i am happy",
    ";^)": "i am winking",
    "(^.^)": "i am happy",
    ":-]": "i am happy",
    "(*_*;": "i am amazed",
    ":o": "i am surprised",
    "=/": "i am undecided",
    ">:‑)": "i am evil",
    "X‑D": "i am laughing",
    "(-_-;)": "i am nervous",
    ":‑b": "it is funny",
    ":')": "i am crying of happiness",
    "(^_-)": "i am winking",
    ":‑<": "i am sad",
    "0:‑3": "i am innocent",
    "O:‑)": "i am innocent",
    "0;^)": "i am innocent",
    ":]": "i am happy",
    ":)": "i am happy",
    ":<": "i am sad",
    "(>_<)": "i am frustrated",
    ";]": "i am winking",
    "8D": "i am laughing",
    "(#^.^#)": "i am happy",
    "(^)o(^)": "i am happy",
    "0:3": "i am innocent",
    ":‑x": "i have my lips sealed",
    "X‑P": "it is funny",
    ":c": "i am sad",
    ":‑D": "i am laughing",
    ":‑/": "i am undecided",
    "(^o^)／": "i am full of joy",
    ":P": "it is funny",
    "('_')": "i am crying",
    ":S": "i am confused",
    ":[": "i am sad",
    ":3": "i am happy",
    ":@": "i am sad",
    "=)": "i am happy",
    ";-;": "i am crying",
    "(；一_一)": "this is a shame",
    "<:‑|": "i am making a straight face",
    ">:[": "i am sad",
    "(^^)": "i am happy",
    "^_^": "i am happy",
    "^/^": "i am happy",
    "(^—^）": "i am happy",
    "8‑0": "i am yawning",
    "Q_Q": "i am crying",
    "(-_-)zzz": "i am sleeping",
    "=3": "i am laughing",
    "(^_^.)": "i am happy",
    ":o)": "i am happy",
    "O:)": "i am innocent",
    ":|": "i am making a straight face",
    "=D": "i am laughing",
    "（*^_^*）": "i am happy",
    ";D": "i am winking",
    "(*_*)": "i am amazed",
    "(*^0^*)": "i am excited",
    ":‑c": "i am sad",
    "3:‑)": "i am evil",
    "(-_-)": "this is a shame",
    "(^_^)": "i am happy",
    ":D": "i am laughing",
    ":‑o": "i am surprised",
    ":‑P": "it is funny",
    "<m(__)m>": "i am bowing",
    ":))": "i am very happy",
    ":-}": "i am happy",
    ":-))": "Very happy",
    ":-3": "i am happy",
    ":>": "i am happy",
    "=]": "i am happy",
    ">:P": "it is funny",
    ";n;": "i am crying",
    ":‑|": "i am making a straight face",
    "=p": "it is funny",
    ">:O": "i am yawning",
    ":'(": "i am crying",
    ":$": "i am confused",
    "=(": "i am sad",
    ":}": "i am happy",
    "(^J^)": "i am happy",
    "8-)": "i am happy",
    "(;_:)": "i am crying",
    ":->": "i am happy",
    ":-)": "i am happy",
    "(^_^;)": "i am nervous",
    ">:(": "i am sad",
    ":‑[": "i am sad",
    ":-)))": "i am very very happy",
    "(@_@)": "i am amazed",
    ";_;": "i am crying",
    "(;_;)": "i am crying",
    "(T_T)": "i am crying",
    "0:)": "i am innocent",
    "(^O^)": "i am happy",
    ":^)": "i am happy",
    "(ToT)": "i am crying",
    ":x": "i have my lips sealed",
    "QQ": "i am crying",
    "_(._.)_": "i am bowing",
    "DX": "i am dismayed",
    "(一一)": "this is a shame",
    ":O": "i am surprised",
    "(+_+)": "i am amazed",
    ">:)": "i am evil",
    "(:_;)": "i am crying",
    ":c)": "i am happy",
    "(*^^)v": "Laughing,Cheerful",
    "m(__)m": "i am bowing",
    "(?_?)": "i am confused",
    "*)": "i am winking",
    "XP": "it is funny",
    "(o.o)": "i am surprised",
    "(^_^)/": "i am full of joy",
    ":‑,": "i am winking",
    ":Þ": "it is funny",
    "(*^.^*)": "i am happy",
    ">^_^<": "i am happy",
    "^^": "i am happy",
    "B^D": "i am laughing",
    ":‑Þ": "it is funny",
    "(/_;)": "i am crying",
    ">:/": "i am undecided",
    "(^<^) (^.^)": "i am happy",
    ":/": "i am undecided",
    "D=": "i am dismayed",
    "m(_ _)m": "i am bowing",
    "d:": "it is funny",
    "o.O": "i am surprised",
    ":‑O": "i am surprised",
    "(^_^)v": "Laughing,Cheerful",
    "Q.Q": "i am crying",
    "D:<": "i am disgusted",
    ":b": "it is funny",
    "(-.-)": "this is a shame",
    "D:": "i am sad",
    ";‑)": "i am winking",
    "<^!^>": "i am happy",
    "(ーー;)": "i am worried",
    "*-)": "i am winking",
    ":-0": "i am shocked",
    "}:)": "i am evil",
    ":'‑)": "i am crying of happiness",
    "XD": "i am laughing",
    ":'‑(": "i am crying",
    "0:‑)": "i am innocent",
    "<(_ _)>": "i am bowing",
    "D;": "i am dismayed",
    "((d[-_-]b))": "i am listening to music",
    ":-(": "i am sad",
    ":‑(": "i am sad",
    "(=_=)": "i am tired",
    "3:)": "i am evil",
    "((+_+))": "i am shocked",
    "(-'-)": "i am worried",
    ">;)": "i am evil",
    "T.T": "i am crying",
    "(;O;)": "i am crying",
    "T_T": "i am crying",
    ";)": "i am winking",
    ":{": "i am sad",
    ";;": "i am crying",
    "8‑D": "i am laughing",
    ":(": "i am sad",
    ":‑)": "i am happy",
    ":)))": "i am very very happy",
    ")^o^(": "i am happy",
    "}:‑)": "i am evil",
    "D8": "i am dismayed",
}


# Dictionary sorted by value name lenght.
EMOTICONS = {
    emoticon: EMOTICONS[emoticon]
    for emoticon in sorted(EMOTICONS, key=len, reverse=True)
}


def check_alphanumeric(input_str: str) -> str:
    """
    This function detects if the input string contains alphabets or numbers and,
    in case it has none, converts the string into an empty string.
    """

    if any(x.isalnum() for x in input_str):
        return input_str
    else:
        return ""


def convert_num_to_words(input_str: str) -> list:
    """
    This function converts numbers to text in the input string.
    """

    return " ".join(
        [num2words(word) if word.isdigit() else word for word in input_str.split()]
    )


def convert_url(input_str: str) -> str:
    """
    This function converts all URL addresses to "http" in the input string.
    """

    regex_pattern = r"https?://\S+|www\.\S+"  # \s matches whitespaces (spaces, tabs and newlines); \S is negated \s.

    return re.sub(regex_pattern, "http", input_str)


def convert_user_mentions(input_str: str) -> str:
    """
    This function converts all user mentions to "@user" in the input string.
    """

    regex_pattern = r"(^|\W)(@\w+)"  # Any @ preceded by whitespace (space, tab or newline), followed by one or more letters.

    return re.sub(regex_pattern, " @user", input_str)


def expand_contractions(input_str: str) -> str:
    """
    This function expands all contractions in the input string.
    """

    # \b matches all word boundaries
    input_str = re.sub(r"\bu're\b", "you are", input_str)
    input_str = re.sub(r"\bu'll\b", "you will", input_str)
    input_str = re.sub(r"\bure\b", "you are", input_str)
    input_str = re.sub(r"\bur\b", "your", input_str)

    return contractions.fix(input_str)


def fix_punctuation(input_str: str) -> str:
    """
    This function removes the leading space found
    for every puntuation mark in the input string.
    """

    # One ore more whitespaces (spaces, tabs and newlines) followed by a single puncutation symbol.
    regex_pattern = re.compile(r"\s*([.,;!?])", re.DOTALL)
    output_string = regex_pattern.sub(r"\1", input_str)

    # Two or more consecutive commas.
    output_string = re.sub(r",+", ",", output_string)

    # Two or more consecutive semicolons.
    output_string = re.sub(r";+", ";", output_string)

    return output_string


def remove_accents(input_str: str) -> str:
    """
    This function removes all accented characters in the input string.
    """

    output_str = []

    for word in input_str.split():

        if emoji.is_emoji(word):
            output_str.append(word)

        else:
            output_str.append(
                unicodedata.normalize("NFKD", word)
                .encode("ascii", "ignore")
                .decode("utf-8", "ignore")
            )

    return emoji.emojize(" ".join(output_str))


def remove_extra_whitespaces(input_str: str) -> str:
    """
    This function removes extra spaces found in the input string.
    """

    # The strip() method will remove both trailing and leading newlines from the string.
    # It also removes any whitespaces on both sides of a string.

    regex_pattern = r" +"  # Any combination of more than one space.

    return re.sub(regex_pattern, " ", input_str).strip()


def remove_html_tags(input_str: str) -> str:
    """
    This function removes HTML tags found in the input string.
    """

    return BeautifulSoup(input_str, "html.parser").get_text()


def remove_irrelevant_punctuation(input_str: str) -> str:
    """
    This function removes all irrelevant punctuation in the input string.
    """

    # Only letters, numbers and relevant puctuation.
    regex_pattern = r"[^a-zA-Z0-9.,;!?@]"

    output_str = []

    for word in input_str.split():

        if emoji.is_emoji(word):
            output_str += word

        else:
            output_str.append(re.sub(regex_pattern, f" ", word))

    if len(output_str) > 1:
        return emoji.emojize(" ".join(output_str))

    if output_str:
        return output_str[0]

    return ""


def remove_repetitions(input_str: str) -> str:
    """
    This function removes more than three consecutive repetitions of any character in the input string.
    """

    regex_pattern = re.compile(r"(.)\1{3,}", re.DOTALL)

    return regex_pattern.sub(r"\1\1\1", input_str)


def remove_single_character_words(input_str: str) -> str:
    """
    This function removes single character words in the input string.
    """

    for word in input_str.split():
        # characters_list = list(set(word))
        characters_list = [
            *set(word),
        ]

        if (
            len(characters_list) == 1
            and not word.isnumeric()
            and characters_list[0] not in punctuation
            and not emoji.is_emoji(word)
        ):

            if characters_list[0] in ["a", "i", "u"]:
                input_str = input_str.replace(word, characters_list[0])

            else:
                input_str = input_str.replace(word, "")

    return input_str


def remove_twitch_emotes(input_str: str) -> str:
    """
    This function removes all Twitch emotes in the input string.
    """

    # Emoticons contained in the EMOTICONS dictionary are already tagged with their
    # natural language translation and do not need any specific labeling task.

    # List of streamer emotes, omitting the ones that are stored in EMOTICONS.
    emotes_list = np.setdiff1d(EMOTES, list(EMOTICONS.keys())).tolist()

    # Remove all Twitch emotes from the input string.
    input_str = " ".join(word for word in input_str.split() if word not in emotes_list)

    return input_str


def remove_words_with_nums(input_str: str) -> str:
    """
    This function deletes all words containing numbers
    or special characters in the input string.
    """

    output_str = []

    for word in input_str.split():
        if (
            word.isalpha()
            or word.isdigit()
            or word.startswith("@")
            or word in punctuation
            or emoji.is_emoji(word)
        ):
            output_str.append(word)

    return " ".join(output_str)


def separate_emojis(input_str: str) -> str:
    """
    This function includes leading and trailing spaces for every emoji found
    in the input string, preventing emojis from being be adjacent.
    """

    return "".join((f" {c} ") if emoji.is_emoji(c) else c for c in input_str)


def separate_emoticons(input_str: str) -> str:
    """
    This function includes leading and trailing spaces for every emote found
    in the input string, preventing emotes from being be adjacent.
    """

    str_emoticons = [emoticon for emoticon in EMOTICONS if emoticon in input_str]

    for emoticon in str_emoticons:
        input_str = input_str.replace(emoticon, f" {emoticon} ")

    return input_str


def separate_punctuation(input_str: str) -> str:
    """
    This function includes leading and trailing spaces
    for every puntuation mark in the input string.
    """

    regex_pattern = re.compile(r"\s*([.,;!?])\s*", re.DOTALL)

    return regex_pattern.sub(r" \1 ", input_str)


def translate_emoticons(input_str: str) -> str:
    """
    This function translates all emoticons in the input string.
    """

    output_str = []

    for word in input_str.split():

        if word in EMOTICONS:
            output_str.append(EMOTICONS[word])
        else:
            output_str.append(word)

    return " ".join(output_str)


def translate_labeled_emotes(input_str: str) -> str:
    """
    This function translates all manually labeled emotes with their meanings.
    """

    return " ".join([LABELED_EMOTES.get(word, word) for word in input_str.split()])


def translate_slangs(input_str: str) -> str:
    """
    This function expands all registered abbreviations in the input string.
    """

    return " ".join(
        [SLANGS[word] if word in SLANGS.keys() else word for word in input_str.split()]
    )


TRANSFORMATIONS = [
    translate_labeled_emotes,
    remove_twitch_emotes,
    remove_html_tags,
    convert_url,
    separate_emojis,
    separate_emoticons,
    translate_emoticons,
    expand_contractions,
    separate_punctuation,
    translate_slangs,
    convert_user_mentions,
    remove_accents,
    remove_irrelevant_punctuation,
    remove_words_with_nums,
    remove_single_character_words,
    convert_num_to_words,
    fix_punctuation,
    remove_repetitions,
    remove_extra_whitespaces,
    check_alphanumeric,
]


def BERT_preprocessing(
    input_str: str, streamer_emotes: list, global_emotes: list, labeled_emotes: dict
) -> str:
    """
    This function serves as a pipeline to apply all the previous
    preprocessing functions to the input string.

    Parameters:
    ---------------
        input_str:
            The message to be preprocessed.

        streamer_emotes:
            A list containing the particular Twitch streamer emotes.

        global_emotes:
            A list containing the global Twitch emotes.

    Returns:
    ---------------
        A string with the preprocess functions applied.
    """

    global EMOTES
    global LABELED_EMOTES

    EMOTES = [
        *set(streamer_emotes + global_emotes),
    ]

    LABELED_EMOTES = labeled_emotes

    return reduce(lambda res, f: f(res), TRANSFORMATIONS, input_str.lower())
