document.addEventListener('submit', function (event) {
    var forma = event.target;
    if (!(forma instanceof HTMLFormElement) || forma.method.toLowerCase() !== 'post') {
        return;
    }
    // onsubmit="return confirm(...)" bekor qilingan bo'lsa (masalan
    // "Ochirishni tasdiqlaysizmi?" so'ralganda foydalanuvchi bekor qilsa),
    // event shu yerga kelguncha allaqachon preventDefault bo'lgan bo'ladi -
    // bu holda tugmani band qilmaymiz, aks holda u abadiy band bo'lib qoladi.
    if (event.defaultPrevented) {
        return;
    }

    var tugma = forma.querySelector('button[type="submit"], input[type="submit"]');
    if (!tugma || tugma.disabled) {
        return;
    }

    tugma.disabled = true;
    if (tugma.textContent && tugma.textContent.trim()) {
        if (tugma.tagName === 'INPUT') {
            tugma.value = 'Yuborilmoqda...';
        } else {
            tugma.textContent = 'Yuborilmoqda...';
        }
    }
    // Ikonka-tugmalar (matnsiz, masalan o'chirish tugmalari) uchun faqat
    // disabled qo'yiladi, matn o'zgartirilmaydi - aks holda kichik ikonka
    // o'rniga uzun matn sig'may qoladi.
}, false);
