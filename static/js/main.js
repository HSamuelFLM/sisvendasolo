// Funções globais e utilitários
document.addEventListener('DOMContentLoaded', () => {
    console.log('SisVenda iniciado!');
});

// Formatação de moeda
function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);
}

// Formatação de data
function formatarData(data) {
    return new Intl.DateTimeFormat('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    }).format(new Date(data));
}

// Notificações
function mostrarNotificacao(mensagem, tipo = 'success') {
    const cores = {
        success: '#27ae60',
        error: '#e74c3c',
        warning: '#f39c12',
        info: '#3498db'
    };
    
    const notificacao = document.createElement('div');
    notificacao.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${cores[tipo]};
        color: white;
        padding: 1rem 2rem;
        border-radius: 5px;
        z-index: 10000;
        animation: slideInRight 0.3s;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    notificacao.textContent = mensagem;
    
    document.body.appendChild(notificacao);
    
    setTimeout(() => {
        notificacao.style.animation = 'slideOutRight 0.3s';
        setTimeout(() => notificacao.remove(), 300);
    }, 3000);
}

// Animação CSS adicional
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Confirmar antes de sair da página se houver alterações não salvas
let alteracoesNaoSalvas = false;

window.addEventListener('beforeunload', function(e) {
    if (alteracoesNaoSalvas) {
        const mensagem = 'Você tem alterações não salvas. Deseja realmente sair?';
        e.returnValue = mensagem;
        return mensagem;
    }
});
