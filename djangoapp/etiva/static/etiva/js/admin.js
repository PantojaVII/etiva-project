// etiva/static/etiva/js/admin.js

document.addEventListener('DOMContentLoaded', function() {
    // Função para aplicar a máscara de CPF
    function mascaraCpf(cpf) {
        return cpf.replace(/\D/g, '') // Remove caracteres não numéricos
                  .replace(/(\d{3})(\d)/, '$1.$2') // Adiciona o primeiro ponto
                  .replace(/(\d{3})(\d)/, '$1.$2') // Adiciona o segundo ponto
                  .replace(/(\d{3})(\d{1,2})$/, '$1-$2'); // Adiciona o hífen
    }

    const cpfInput = document.getElementById('id_cpf');
    if (cpfInput) {
        cpfInput.addEventListener('input', function() {
            this.value = mascaraCpf(this.value);
        });
    }
});
