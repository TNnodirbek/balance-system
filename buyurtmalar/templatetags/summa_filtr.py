from django import template

register = template.Library()

SOM_SOZ = "so'm"


def _guruhlash(son):
    teskari = str(son)[::-1]
    guruhlar = [teskari[i:i + 3] for i in range(0, len(teskari), 3)]
    return '.'.join(guruhlar)[::-1]


@register.filter(name='som_format')
def som_format(qiymat):
    try:
        son = int(round(float(qiymat)))
    except (TypeError, ValueError):
        return qiymat

    manfiy = son < 0
    son = abs(son)

    if son >= 1_000_000:
        mln = son // 1_000_000
        ming = (son % 1_000_000) // 1000
        if ming:
            natija = f"{mln} mln {ming} ming {SOM_SOZ}"
        else:
            natija = f"{mln} mln {SOM_SOZ}"
    elif son >= 1000:
        natija = f"{_guruhlash(son)} {SOM_SOZ}"
    else:
        natija = f"{son} {SOM_SOZ}"

    return f"-{natija}" if manfiy else natija
