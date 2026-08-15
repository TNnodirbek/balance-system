function telefonQiymatiniFormatlash(qiymat) {
    let raqamlar = qiymat.replace(/\D/g, '');
    if (raqamlar.startsWith('998') && raqamlar.length > 9) {
        raqamlar = raqamlar.slice(3);
    }
    raqamlar = raqamlar.slice(0, 9);

    const guruhlar = [];
    if (raqamlar.length > 0) guruhlar.push(raqamlar.slice(0, 2));
    if (raqamlar.length > 2) guruhlar.push(raqamlar.slice(2, 5));
    if (raqamlar.length > 5) guruhlar.push(raqamlar.slice(5, 7));
    if (raqamlar.length > 7) guruhlar.push(raqamlar.slice(7, 9));
    return guruhlar.join('-');
}

function telefonInputgaIshlov(event) {
    const input = event.target;
    const eskiQiymat = input.value;
    const kursorOldin = input.selectionStart;
    const kursorgachaRaqamlar = eskiQiymat.slice(0, kursorOldin).replace(/\D/g, '').length;

    input.value = telefonQiymatiniFormatlash(eskiQiymat);

    let raqamHisoblagich = 0;
    let yangiKursor = input.value.length;
    for (let i = 0; i < input.value.length; i++) {
        if (/\d/.test(input.value[i])) {
            raqamHisoblagich++;
        }
        if (raqamHisoblagich === kursorgachaRaqamlar) {
            yangiKursor = i + 1;
            break;
        }
    }
    if (kursorgachaRaqamlar === 0) {
        yangiKursor = 0;
    }
    input.setSelectionRange(yangiKursor, yangiKursor);
}

document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.telefon-input').forEach(function (input) {
        if (input.value) {
            input.value = telefonQiymatiniFormatlash(input.value);
        }
        input.addEventListener('input', telefonInputgaIshlov);
    });
});
