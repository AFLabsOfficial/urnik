from django.test import TestCase
from urnik.tedenski_urnik import TedenskiUrnik, TedenskiUrnikTermin
from urnik.models import *


class TestTedenskiPogled(TestCase):
    def test_petki(self):
        semester = Semester.objects.create(
            objavljen=True, od=datetime.date(2020, 1, 1),
            do=datetime.date(2021, 1, 1))
        for prof in ['Boris', 'Luka', 'Jože']:
            Oseba.objects.create(ime=prof, priimek=prof)
        letnik = Letnik.objects.create(smer='Smer1',oddelek="M", leto=1,
                                       kratica="BUR")

        ucilnice_data = [
            (Ucilnica.TIP[0], "Matematika 1", "M1", "Klet", 30),
            (Ucilnica.TIP[1], "Fizika 1", "F1", "Fizika", 130),
            (Ucilnica.TIP[0], "Matematika 2", "M2", "Klet", 50),
        ]

        ucilnice = []

        for tip, oznaka, kratka, prostor, velikost in ucilnice_data:
            ucilnice.append(
                Ucilnica.objects.create(
                    tip=tip[0], oznaka=oznaka, kratka_oznaka=kratka,
                    # prostor=prostor,
                    velikost=velikost
                )
            )
        predmeti = []
        for pred in ['Slovenščina', 'Matematika', 'Fizika']:
            predmet = Predmet.objects.create(ime=pred, kratica=pred)
            predmet.letniki.set([letnik])
            predmeti.append(predmet)

        Srecanje.objects.create(ucilnica=ucilnice[0], ura=8 * 4, trajanje=8,
                                semester=semester, predmet=predmeti[0],
                                oznaka=predmeti[0].kratica, dan=5, )
        Srecanje.objects.create(ucilnica=ucilnice[0], ura=8 * 4, trajanje=8,
                                semester=semester, predmet=predmeti[0],
                                oznaka=predmeti[0].kratica, dan=4, )

        Srecanje.objects.create(ucilnica=ucilnice[1], ura=8 * 4, trajanje=8,
                                semester=semester, predmet=predmeti[1],
                                oznaka=predmeti[1].kratica, dan=5, )

        srecanja = Srecanje.objects.all()
        kategorije = Predmet.objects.filter(srecanja__in=srecanja).distinct()
        tedenski_urnik = TedenskiUrnik()
        tedenski_urnik.dodaj_srecanja(srecanja.za_urnik())
        teden = datetime.date.today()
        tedenski_pogled = tedenski_urnik.termini(kategorije)
        self.assertEqual(len(tedenski_pogled), 3)

        srecanja = letnik.srecanja(semester).all()
        srecanja_v_tednu = srecanja.v_tednu_semestra(teden, semester)

        self.assertEqual(len(srecanja_v_tednu), 3)
