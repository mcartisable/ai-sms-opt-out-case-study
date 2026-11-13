#!/usr/bin/env python3
"""Build a deterministic synthetic dataset of customer replies to marketing SMS.

Standard library only. Seeded, so re-running produces identical output.
Writes replies.csv next to this script and prints a count table.
"""

import csv
import os
import random
import re
from collections import Counter

SEED = 20261112
OUT_NAME = "replies.csv"
COLUMNS = ["id", "text", "label", "category", "language", "has_keyword"]

# Opt-out keywords used for the has_keyword flag (whole-word, case-insensitive).
KEYWORD_RE = re.compile(
    r"\b(stop|stopall|unsubscribe|unsub|opt[\s-]?out|optout|cancel|end|quit|стоп|baja)\b",
    re.IGNORECASE,
)
# Substrings that soft_refusal and frustrated rows must never contain.
FORBIDDEN_SUBSTRINGS = [
    "stop", "unsubscribe", "unsub", "opt out", "opt-out", "optout", "cancel", "end", "quit",
]


def has_keyword(text):
    return bool(KEYWORD_RE.search(text))


# ---------------------------------------------------------------- variation

PREFIXES = {
    "en": ["", "", "", "hey ", "hi, ", "ok so ", "hello, ", "listen, "],
    "ru": ["", "", "эй, ", "ну ", "слушайте, "],
    "es": ["", "", "oye, ", "hola, ", "mira, "],
}
BASE_SUFFIXES = {
    "en": ["", "", ".", "!", "!!", "...", " pls", " thx", " :)"],
    "ru": ["", "", ".", "!", "!!", "...", " пожалуйста", " плиз", " :)"],
    "es": ["", "", ".", "!", "!!", "...", " por favor", " porfa", " :)"],
}
KEYWORD_SUFFIXES = ["", ".", "!", "!!", "...", " :)"]


def add_typo(text, rng):
    """Swap two adjacent letters at a random interior position."""
    idx = [i for i in range(1, len(text) - 1)
           if text[i].isalpha() and text[i + 1].isalpha()]
    if not idx:
        return text
    i = rng.choice(idx)
    return text[:i] + text[i + 1] + text[i] + text[i + 2:]


def vary(base, sp, rng):
    text = rng.choice(sp["prefixes"]) + base
    mode = rng.choices(["asis", "lower", "cap", "upper"], weights=[4, 2, 2, 1])[0]
    if mode == "lower":
        text = text.lower()
    elif mode == "cap":
        text = text[:1].upper() + text[1:].lower()
    elif mode == "upper":
        text = text.upper()
    suffix = rng.choice(sp["suffixes"])
    if suffix and text and text[-1] in "?!." and suffix[0] in "?!.":
        suffix = ""
    text = text + suffix
    if sp["typo"] and rng.random() < 0.12:
        text = add_typo(text, rng)
    return text


def spec(label, category, lang, quota, bases, *, expect_kw=False, strict=False,
         typo=True, extra=(), prefixes=None, suffixes=None):
    return {
        "label": label,
        "category": category,
        "lang": lang,
        "quota": quota,
        "bases": list(bases),
        "expect_kw": expect_kw,
        "strict": strict,
        "typo": typo,
        "prefixes": prefixes or PREFIXES[lang],
        "suffixes": suffixes or (BASE_SUFFIXES[lang] + list(extra)),
    }


# ---------------------------------------------------------------- phrase pools

KEYWORD_EN = [
    "STOP", "stop", "Stop", "STOP ALL", "stop all", "UNSUBSCRIBE", "unsubscribe",
    "Unsubscribe", "Unsubscribe me", "Opt out", "OPT OUT", "opt-out", "OPTOUT",
    "cancel", "Cancel", "CANCEL", "end", "END", "quit", "QUIT", "Quit", "unsub",
    "STOPALL", "please stop", "Please STOP", "stop texting", "STOP texting me",
    "pls unsubscribe", "cancel subscription", "stop sending", "reply STOP",
    "END ALL", "quit alerts", "STOP TEXTS", "stop messages", "Stop the texts",
    "Opt-out please", "unsubscribe pls", "cancel my texts",
]

TRAP_EN = [
    "Please don't stop the sale emails, I love them",
    "Can't stop thinking about that dress",
    "Does the sale end tomorrow?",
    "How do I cancel my order #1234?",
    "Can I cancel my order? I picked the wrong size",
    "Is the sale going to end soon?",
    "Quit being so good at these deals lol",
    "Bus stop is right by your store, what time do you open?",
    "Can I cancel the gift wrap on order 5521?",
    "When does the offer end?",
    "Stop by the store and say hi?",
    "Your last text was so good I can't stop smiling",
    "I want to cancel my pre-order for the boots",
    "Does the code end on Sunday?",
    "Please don't stop sending these deals",
    "How do I cancel an order I placed yesterday?",
    "Can't stop shopping with you guys",
    "Please don't end the rewards program, I love it",
    "Don't stop the restock alerts pls",
    "Can I cancel and reorder in a different size?",
    "Quick question, does the sale end before Friday?",
    "Stop the presses, is the sale on today?",
    "Your end of season sale looks amazing",
    "Is the end-of-season sale on this weekend?",
    "Can't stop refreshing your site for the drop",
    "I need to cancel order #8831 and get a refund",
    "Hey, did the sale really end already?",
    "Quit it with the flash sales lol, my wallet hurts",
    "Stop it with the 50% off banners, I'm obsessed",
    "How do I cancel a backorder?",
    "What time does the flash sale end?",
    "Is it true the sale will stop at midnight?",
    "Can I cancel my Saturday pickup?",
    "Stop being so generous with the discounts",
    "I can't stop checking your new arrivals",
    "Did you guys stop shipping to Ohio?",
    "Please cancel my order, it arrived damaged",
    "Does the offer end when I checkout?",
    "Is the free returns window going to end?",
    "Will the sale end before my paycheck?",
    "Cancel my order and refund me",
    "Can't wait for the end of summer sale",
]

SOFT_EN = [
    "I don't want to receive messages from you anymore",
    "please remove me from your list",
    "remove my number from your list please",
    "take me off this list",
    "take me off this",
    "no more texts please",
    "no more messages, thanks",
    "leave me alone",
    "I never signed up for this, delete my number",
    "this is getting annoying, enough",
    "I don't want these messages anymore",
    "please don't text me again",
    "don't message me anymore",
    "I'm not interested in these texts, remove me",
    "delete my number from your system",
    "please delete me from your database",
    "I did not agree to get texts from you",
    "I have no idea how you got my number, please delete it",
    "Please take my number off your list",
    "I want out of this list",
    "Get me off this list",
    "I'm done with these texts",
    "I'm done getting these messages, remove me",
    "Please don't contact me again",
    "I'm not going to keep receiving these, remove me please",
    "Remove this number from your marketing list",
    "Please remove me from all your texting lists",
    "I don't need any more promos from you, take me off",
    "Too many texts, I'm out",
    "Please just leave me be",
    "Don't text this number anymore",
    "Kindly take me off your mailing list",
    "I didn't ask for these messages. Delete me.",
    "Please erase my number from your records",
    "I'd like to be removed from your messages",
    "no thanks, I'm out, remove my number",
    "I've had enough of these texts, delete my number",
    "Please don't keep messaging me",
    "remove me from the list now",
    "This number doesn't want your promos",
    "Please take me out of your system",
    "Take my name off your mailing list",
    "you can take me off your texting list",
    "What the hell, back off already",
    "Get lost already with your promos",
    "Wow, you people are relentless. Leave me alone",
    "Are you serious right now, delete my number",
    "Piss off with the texts",
    "Freaking annoying, leave me alone",
    "Who the heck keeps texting me? Back off",
    "Unreal. Get your junk off my phone",
]

SOFT_RU = [
    "Не пишите мне больше",
    "Отпишите меня от рассылки",
    "Удалите мой номер из вашей базы",
    "Уберите меня из списка, пожалуйста",
    "Хватит писать мне",
    "Не присылайте больше сообщения",
    "Мне это надоело, не пишите",
    "Я не подписывался на ваши сообщения",
    "Не хочу получать ваши сообщения",
    "Оставьте меня в покое",
]

SOFT_ES = [
    "No quiero recibir más mensajes",
    "Bórrame de la lista",
    "Quítame de la lista",
    "No me manden más textos",
    "Ya no quiero mensajes, déjenme en paz",
    "Por favor no me escriban más",
    "Eliminen mi número de su lista",
    "Dejen de escribirme",
    "No me interesa, ya no me escriban",
    "Sáquenme de esta lista",
]

FRUSTRATED_EN = [
    "This is ridiculous, I never asked for these texts",
    "Seriously?? Who gave you my number",
    "Are you kidding me with these texts",
    "Damn it, not again with these messages",
    "Ugh, this is so annoying",
    "Who the hell gave you my number",
    "I'm sick of this crap",
    "Enough already, you're driving me nuts",
    "Holy crap, another promo? Really?",
    "This is spam and I'm furious",
    "Ridiculous. I've never shopped with you and you keep blowing up my phone",
    "Idiots, I never signed up for this garbage",
    "Oh for crying out loud, another text?",
    "This is harassment, I'm reporting you",
    "WTF is this, who gave you my number",
    "You've got some nerve texting me like this",
    "Enough with the spam already, seriously",
]

FRUSTRATED_RU = [
    "Да сколько можно уже!",
    "Достали со своими сообщениями",
    "Кто вам дал мой номер, блин",
    "Идиоты, я не подписывался на эту чушь",
    "Какого черта вы мне пишете?",
]

FRUSTRATED_ES = [
    "Qué pesados, ya basta",
    "¿Quién les dio mi número? Qué molestia",
    "Ya es el colmo con sus mensajes",
    "Qué fastidio con tanto mensaje",
]

QUESTION_EN = [
    "What time do you close?",
    "What time do you open tomorrow?",
    "Where is my order?",
    "Where is my package?",
    "Is the 20% code still valid?",
    "Does the 20% code work on sale items?",
    "Do you ship to Canada?",
    "Is this store open on Sundays?",
    "Can I return an online order in store?",
    "What are your opening hours?",
    "Did my package ship yet?",
    "When will my order arrive?",
    "Do you have this in medium?",
    "Is there free shipping over $50?",
    "Does the code work on sale items?",
    "Can I pick up in store today?",
    "Where is your nearest location?",
    "Do you accept Apple Pay?",
    "How long does delivery take?",
    "Is the black jacket back in stock?",
    "What's my tracking number?",
    "Do you have this in a size 10?",
    "Can I change my delivery address?",
    "Is the new customer code only for first orders?",
    "How do I redeem a gift card?",
    "What's your return policy?",
    "Is the new collection online yet?",
    "Which store is open late?",
    "Has my refund been processed?",
    "Do you price match?",
    "When does the winter sale start?",
    "Is this available in blue?",
    "What's your support phone number?",
    "Can I get my receipt by email?",
    "Do you do gift wrapping?",
    "How much is shipping to Mexico?",
    "Where can I find the size chart?",
    "Is order #4482 on its way?",
    "Are you open on holidays?",
    "How many points do I have?",
    "Do you have a store in Austin?",
    "Is the student discount still on?",
    "What's the warranty period?",
    "Can I use two codes at once?",
    "Does the Brooklyn store have these in stock?",
    "Can you check my order status?",
    "Do you have a loyalty app?",
    "Is the sale price the final price?",
    "Who do I contact about a damaged item?",
]

QUESTION_RU = [
    "Во сколько вы закрываетесь?",
    "Где мой заказ?",
    "Код на 20% еще действует?",
    "Вы доставляете в Казахстан?",
    "Когда будет доставка?",
]

QUESTION_ES = [
    "¿A qué hora cierran?",
    "¿Dónde está mi pedido?",
    "¿El código del 20% sigue activo?",
    "¿Envían a México?",
    "¿Cuándo llega mi paquete?",
]

POSITIVE_EN = [
    "Thanks!", "Thank you so much", "Love the new collection", "YES", "yes please",
    "Send me the link", "Send the link", "Perfect, thanks", "Awesome", "Love it!",
    "Great, I'll check it out", "Got it, thanks", "Sounds good", "Yes!!", "Yep", "Sure",
    "Please send the code", "I'm in!", "Can't wait for the sale", "Amazing deal, thank you",
    "Just bought the boots, love them", "Thanks for the reminder", "Yay", "Cool", "Nice",
    "Love this!", "Count me in", "Send it over", "Sweet", "Yes send it", "Thx",
    "Loving the new arrivals", "Great deals as always", "Haha thanks",
    "Ooh, show me more", "Yes, please", "Totally want that dress", "Tell me more",
    "Let's go", "I'm excited for the drop", "Wow those look great",
    "Thank you for the discount", "Thanks, got the code", "Send me the details",
    "Yes, send the link please",
]

POSITIVE_RU = [
    "Спасибо!", "Отлично, спасибо", "Да", "Пришлите ссылку", "Люблю новую коллекцию",
]

POSITIVE_ES = [
    "¡Gracias!", "Sí, por favor", "Envíame el enlace", "Me encanta la nueva colección", "¡Genial!",
]

NOISE_EN = [
    "ok", "OK", "okay", "k", "kk", "👍", "👍🙂", "lol", "haha", "ha", "ya", "hmm",
    "ok thx", "sure lol", "🙂", "😂", "ok 👍", "mm", "ahh", "np", "alright", "🤷",
    "ok cool", "ha ha", "lmao", "ok ok", "👌", "yup", "ya ok",
]

NOISE_RU = ["ок", "ага", "ладно", "хорошо"]

NOISE_ES = ["vale", "bien", "jaja", "ok"]

AMBIG_EN = [
    "Not interested", "Maybe later", "Too many messages lately", "wrong number",
    "Wrong number", "Wrong person", "who is this?", "Who is this?", "Not now",
    "not right now", "Maybe", "Hmm, not sure", "Too many texts lately", "Not today",
    "I'll think about it", "Maybe next time", "Who dis?", "Not interested right now",
    "Ask me later", "Try again next month", "Not for me", "Too much lately",
    "Maybe another time", "Check back in a month", "Not right now, too busy",
    "Too many promos lately",
]

AMBIG_RU = ["Не сейчас", "Может позже", "Кто это?", "Неправильный номер", "Не интересно"]

AMBIG_ES = ["Ahora no", "Quizás más tarde", "¿Quién es?", "Número equivocado", "No me interesa"]

KEYWORD_RU = ["СТОП", "Стоп", "стоп!", "СТОП!!"]
KEYWORD_ES = ["BAJA", "baja", "Baja por favor", "BAJA!"]


SPECS = [
    # opt_out
    spec("opt_out", "keyword", "en", 56, KEYWORD_EN, expect_kw=True, typo=False,
         prefixes=[""], suffixes=KEYWORD_SUFFIXES),
    spec("opt_out", "keyword", "ru", 2, KEYWORD_RU, expect_kw=True, typo=False,
         prefixes=[""], suffixes=KEYWORD_SUFFIXES),
    spec("opt_out", "keyword", "es", 2, KEYWORD_ES, expect_kw=True, typo=False,
         prefixes=[""], suffixes=KEYWORD_SUFFIXES),
    spec("opt_out", "soft_refusal", "en", 110, SOFT_EN, strict=True),
    spec("opt_out", "soft_refusal", "ru", 10, SOFT_RU, strict=True),
    spec("opt_out", "soft_refusal", "es", 10, SOFT_ES, strict=True),
    spec("ambiguous", "frustrated", "en", 24, FRUSTRATED_EN, strict=True,
         extra=[" ugh", " seriously", " 😡", " !!!"]),
    spec("ambiguous", "frustrated", "ru", 3, FRUSTRATED_RU, strict=True),
    spec("ambiguous", "frustrated", "es", 3, FRUSTRATED_ES, strict=True),
    # not_opt_out
    spec("not_opt_out", "question", "en", 47, QUESTION_EN),
    spec("not_opt_out", "question", "ru", 4, QUESTION_RU),
    spec("not_opt_out", "question", "es", 4, QUESTION_ES),
    spec("not_opt_out", "positive", "en", 47, POSITIVE_EN, extra=[" 🙌", " 🔥", " 😍"]),
    spec("not_opt_out", "positive", "ru", 4, POSITIVE_RU),
    spec("not_opt_out", "positive", "es", 4, POSITIVE_ES),
    spec("not_opt_out", "keyword_trap", "en", 45, TRAP_EN, expect_kw=True, typo=False),
    spec("not_opt_out", "wrong_number_or_other", "en", 19, NOISE_EN),
    spec("not_opt_out", "wrong_number_or_other", "ru", 3, NOISE_RU),
    spec("not_opt_out", "wrong_number_or_other", "es", 3, NOISE_ES),
    # ambiguous
    spec("ambiguous", "ambiguous", "en", 42, AMBIG_EN),
    spec("ambiguous", "ambiguous", "ru", 4, AMBIG_RU),
    spec("ambiguous", "ambiguous", "es", 4, AMBIG_ES),
]


# ---------------------------------------------------------------- generation

def generate(rng, seen, sp):
    rows = []
    tries = 0
    limit = sp["quota"] * 500
    while len(rows) < sp["quota"]:
        tries += 1
        if tries > limit:
            raise RuntimeError(
                f"could not fill {sp['label']}/{sp['category']}/{sp['lang']}")
        text = vary(rng.choice(sp["bases"]), sp, rng)
        if text in seen:
            continue
        if has_keyword(text) != sp["expect_kw"]:
            continue
        if sp["strict"] and any(f in text.lower() for f in FORBIDDEN_SUBSTRINGS):
            continue
        seen.add(text)
        rows.append({
            "text": text,
            "label": sp["label"],
            "category": sp["category"],
            "language": sp["lang"],
            "has_keyword": has_keyword(text),
        })
    return rows


def verify(rows):
    errors = []
    for r in rows:
        expected_kw = r["category"] in ("keyword", "keyword_trap")
        if r["has_keyword"] != has_keyword(r["text"]) or r["has_keyword"] != expected_kw:
            errors.append(f"has_keyword mismatch id={r['id']}: {r['text']!r}")
        if r["category"] in ("soft_refusal", "frustrated"):
            hits = [f for f in FORBIDDEN_SUBSTRINGS if f in r["text"].lower()]
            if hits:
                errors.append(f"forbidden substring {hits} id={r['id']}: {r['text']!r}")
    if errors:
        raise SystemExit("verification failed:\n" + "\n".join(errors[:20]))
    print("Verification passed: has_keyword matches the category for every row; "
          "no soft_refusal/frustrated row contains a forbidden keyword substring.")


def print_table(rows):
    langs = ["en", "ru", "es"]
    order = []
    for sp in SPECS:
        key = (sp["label"], sp["category"])
        if key not in order:
            order.append(key)
    cnt = Counter((r["label"], r["category"], r["language"]) for r in rows)
    kw = Counter((r["label"], r["category"]) for r in rows if r["has_keyword"])

    header = f"{'label':<12}{'category':<24}{'en':>6}{'ru':>6}{'es':>6}{'total':>8}{'has_kw':>8}"
    print()
    print(header)
    print("-" * len(header))
    for label, cat in order:
        per = [cnt[(label, cat, lang)] for lang in langs]
        total = sum(per)
        print(f"{label:<12}{cat:<24}{per[0]:>6}{per[1]:>6}{per[2]:>6}{total:>8}"
              f"{kw[(label, cat)]:>8}")
    print("-" * len(header))
    grand = [sum(cnt[(l, c, lang)] for (l, c) in order) for lang in langs]
    print(f"{'TOTAL':<12}{'':<24}{grand[0]:>6}{grand[1]:>6}{grand[2]:>6}{len(rows):>8}"
          f"{sum(kw.values()):>8}")
    print()
    for label in ["opt_out", "not_opt_out", "ambiguous"]:
        n = sum(1 for r in rows if r["label"] == label)
        print(f"label {label:<12} {n}")
    print()
    for lang in langs:
        print(f"language {lang}: {sum(1 for r in rows if r['language'] == lang)}")


def main():
    rng = random.Random(SEED)
    seen = set()
    rows = []
    for sp in SPECS:
        rows.extend(generate(rng, seen, sp))
    rng.shuffle(rows)
    for i, r in enumerate(rows, start=1):
        r["id"] = i

    verify(rows)

    out_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, OUT_NAME)
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Wrote {len(rows)} rows to {out_path}")
    print_table(rows)


if __name__ == "__main__":
    main()
