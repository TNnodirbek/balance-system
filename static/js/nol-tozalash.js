document.addEventListener('focusin', function (event) {
    var input = event.target;
    if (input.classList && input.classList.contains('nol-tozalanadigan') && input.value === '0') {
        input.value = '';
    }
});

document.addEventListener('focusout', function (event) {
    var input = event.target;
    if (input.classList && input.classList.contains('nol-tozalanadigan') && input.value.trim() === '') {
        input.value = '0';
    }
});
