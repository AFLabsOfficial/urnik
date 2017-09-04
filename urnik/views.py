from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import urlencode
from django.contrib.auth.decorators import login_required
from .models import *


def zacetna_stran(request):
    smeri = {}
    for letnik in Letnik.objects.all():
        try:
            smer, opis = str(letnik).split(',')
            letnik.opis = opis
            smeri.setdefault(smer, []).append(letnik)
        except:
            pass
    osebe = Oseba.objects.aktivni().exclude(priimek='X')
    ucilnice = Ucilnica.objects.filter(vidna=True).exclude(oznaka='X')
    stolpci_smeri = ([], [])
    for i, (smer, letniki) in enumerate(sorted(smeri.items())):
        stolpci_smeri[i % 2].append({
            'ime': smer,
            'letniki': letniki
        })
    return render(request, 'zacetna_stran.html', {
        'stolpci_smeri': stolpci_smeri,
        'osebe': osebe,
        'ucilnice': ucilnice,
    })


def urnik(request, srecanja, naslov):
    if request.user.is_authenticated and request.session.get('urejanje', False):
        if request.META['QUERY_STRING']:
            next_url = '{}?{}'.format(request.path, request.META['QUERY_STRING'])
        else:
            next_url = request.path
        return render(request, 'urnik.html', {
            'nacin': 'urejanje',
            'naslov': naslov,
            'srecanja': srecanja.urnik(),
            'odlozena_srecanja': Srecanje.objects.odlozena(),
            'prekrivanja_po_tipih': Srecanje.objects.prekrivanja(),
            'next': next_url
        })
    else:
        return render(request, 'urnik.html', {
            'nacin': 'ogled',
            'naslov': naslov,
            'srecanja': srecanja.urnik(),
        })


def urnik_osebe(request, oseba_id):
    oseba = get_object_or_404(Oseba, id=oseba_id)
    naslov = str(oseba)
    return urnik(request, oseba.srecanja.all(), naslov)


def urnik_letnika(request, letnik_id):
    letnik = get_object_or_404(Letnik, id=letnik_id)
    naslov = str(letnik)
    return urnik(request, letnik.srecanja().all(), naslov)


def urnik_ucilnice(request, ucilnica_id):
    ucilnica = get_object_or_404(Ucilnica, id=ucilnica_id)
    naslov = 'Učilnica {}'.format(ucilnica.oznaka)
    return urnik(request, ucilnica.srecanja.all(), naslov)


def urnik_predmeta(request, predmet_id):
    predmet = get_object_or_404(Predmet, id=predmet_id)
    naslov = str(predmet)
    return urnik(request, predmet.srecanja.all(), naslov)


@login_required
def premakni_srecanje(request, srecanje_id):
    srecanje = get_object_or_404(Srecanje, id=srecanje_id)
    if request.method == 'POST':
        dan = int(request.POST['dan'])
        ura = int(request.POST['ura'])
        ucilnica = get_object_or_404(Ucilnica, id=request.POST['ucilnica'])
        srecanje.premakni(dan, ura, ucilnica)
        return redirect(request.POST['next'])
    else:
        return render(request, 'urnik.html', {
            'nacin': 'urejanje',
            'naslov': 'Premikanje srečanja',
            'srecanja': srecanje.povezana_srecanja().urnik(),
            'odlozena_srecanja': Srecanje.objects.odlozena(),
            'prekrivanja_po_tipih': {},
            'prosti_termini': srecanje.prosti_termini(),
            'next': request.META.get('HTTP_REFERER', '/'),
        })


@login_required
def podvoji_srecanje(request, srecanje_id):
    srecanje = get_object_or_404(Srecanje, id=srecanje_id)
    srecanje.podvoji()
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def odlozi_srecanje(request, srecanje_id):
    srecanje = get_object_or_404(Srecanje, id=srecanje_id)
    srecanje.odlozi()
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def nastavi_trajanje_srecanja(request, srecanje_id):
    srecanje = get_object_or_404(Srecanje, id=srecanje_id)
    trajanje = int(request.POST['trajanje'])
    srecanje.nastavi_trajanje(trajanje)
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def preklopi_urejanje(request):
    request.session['urejanje'] = not request.session.get('urejanje', False)
    return redirect(request.META.get('HTTP_REFERER', '/'))