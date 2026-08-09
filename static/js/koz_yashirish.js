var YASHIRIN_KOZ_SVG = '<path d="M2 12S5.5 5 12 5S22 12 22 12S18.5 19 12 19S2 12 2 12Z" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/><circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="1.7"/>';
var YOPIQ_KOZ_SVG = '<path d="M3 3L21 21" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/><path d="M10.6 5.2A10.6 10.6 0 0 1 12 5C18.5 5 22 12 22 12A18.6 18.6 0 0 1 18.4 16.4M6.5 6.9C3.7 8.8 2 12 2 12S5.5 19 12 19A10.3 10.3 0 0 0 15.4 18.4" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/><path d="M9.9 10A3 3 0 0 0 14 14" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>';

function kozYashirishSozla(tugmaId, ikonkaId, qiymatKlassi) {
    var tugma = document.getElementById(tugmaId);
    var ikonka = document.getElementById(ikonkaId);
    if (!tugma || !ikonka) {
        return;
    }

    document.querySelectorAll('.' + qiymatKlassi).forEach(function (el) {
        el.dataset.qiymat = el.textContent;
    });

    var yashirilganMi = false;

    tugma.addEventListener('click', function () {
        yashirilganMi = !yashirilganMi;
        document.querySelectorAll('.' + qiymatKlassi).forEach(function (el) {
            el.textContent = yashirilganMi ? '•••••••' : el.dataset.qiymat;
        });
        ikonka.innerHTML = yashirilganMi ? YOPIQ_KOZ_SVG : YASHIRIN_KOZ_SVG;
    });
}
