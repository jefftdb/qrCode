
// Função para selecionar o ícone do qrcode
document.querySelectorAll('.icon-option input[type="radio"]').forEach(radio => {
    radio.addEventListener('change', function() {
        document.querySelectorAll('.icon-option').forEach(label => {
            label.classList.remove('selected');
        });
        if (this.checked) {
            this.closest('.icon-option').classList.add('selected');
        }
    });
});

// Função para copiar o código Pix para a área de transferência
document.getElementById('copyButton').addEventListener('click', function() {
    var pixCodeInput = document.getElementById('modalTextoPix');
    
    // Seleciona o conteúdo do input
    pixCodeInput.select();
    pixCodeInput.setSelectionRange(0, 99999); // Para dispositivos móveis

    // Copia o conteúdo selecionado para a área de transferência
    document.execCommand('copy');
    
    // Mostrar mensagem de alerta
    var copyAlert = document.getElementById('copyAlert');
    copyAlert.style.display = 'block';
    setTimeout(function() {
        copyAlert.style.display = 'none';
    }, 2000);
});




