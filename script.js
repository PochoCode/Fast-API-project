// Seleciona o botão "Voltar ao Topo"
const botaoVoltarTopo = document.getElementById("voltar-topo");

// URL da API (Backend)
// Para testar no celular, troque '127.0.0.1' pelo IP do seu computador (ex: 192.168.1.X)
const API_BASE_URL = 'http://192.168.1.16:8000'; 

// Definição do Cardápio (Padronização)
const MENU_ITENS = [
    { sabor: "Mussarela", tamanho: "Pequena", preco: 25.00 },
    { sabor: "Mussarela", tamanho: "Grande", preco: 40.00 },
    { sabor: "Calabresa", tamanho: "Pequena", preco: 28.00 },
    { sabor: "Calabresa", tamanho: "Grande", preco: 45.00 },
    { sabor: "Portuguesa", tamanho: "Pequena", preco: 30.00 },
    { sabor: "Portuguesa", tamanho: "Grande", preco: 50.00 },
    { sabor: "Coca-Cola", tamanho: "2L", preco: 12.00 },
    { sabor: "Coca-Cola", tamanho: "Lata", preco: 6.00 }
];


// Adiciona um evento de rolagem na janela
window.onscroll = function() {
    // Se o usuário rolou mais de 100px para baixo
    if (document.body.scrollTop > 100 || document.documentElement.scrollTop > 100) {
        // Mostra o botão
        botaoVoltarTopo.style.display = "block";
    } else {
        // Esconde o botão
        botaoVoltarTopo.style.display = "none";
    }
};

// Validação do Formulário de Registro
const authContainer = document.getElementById('auth-container');
const userArea = document.getElementById('user-area');
const registerForm = document.getElementById('register-form');
const nomeInput = document.getElementById('nome');
const emailInput = document.getElementById('email');
const senhaInput = document.getElementById('senha');

const nomeError = document.getElementById('nome-error');
const emailError = document.getElementById('email-error');
const senhaError = document.getElementById('senha-error');

// Seleciona o formulário de login e seus campos
const loginForm = document.getElementById('login-form');
const loginEmailInput = document.getElementById('login-email');
const loginSenhaInput = document.getElementById('login-senha');
const loginEmailError = document.getElementById('login-email-error');
const loginSenhaError = document.getElementById('login-senha-error');
const logoutButton = document.getElementById('logout-button');

// Adiciona validação em tempo real (ao sair do campo)
nomeInput.addEventListener('blur', validateNome);
emailInput.addEventListener('blur', validateEmail);
senhaInput.addEventListener('blur', validateSenha);

registerForm.addEventListener('submit', async function(event) {
    // Previne o envio do formulário para realizar a validação
    event.preventDefault();

    // Roda todas as validações antes de tentar enviar
    const isNomeValid = validateNome();
    const isEmailValid = validateEmail();
    const isSenhaValid = validateSenha();

    if (isNomeValid && isEmailValid && isSenhaValid) {

        const submitButton = registerForm.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.textContent;
        submitButton.disabled = true;
        submitButton.textContent = 'Criando conta...';

        const formData = {
            nome: nomeInput.value,
            email: emailInput.value,
            senha: senhaInput.value
        };

        try {
            // Para desenvolvimento local, use a URL completa do seu backend
            console.log(formData);

            const response = await fetch(`${API_BASE_URL}/auth/criar_conta`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            const data = await response.json();

            if (response.ok) { // A propriedade .ok é true para status 200-299
                alert(data.mensagem || 'Usuário criado com sucesso!');
                registerForm.reset(); // Limpa o formulário
                clearErrors(); // Limpa as mensagens e bordas de erro
                // Limpa as classes de erro após o envio bem-sucedido
                nomeInput.classList.remove('invalid');
                emailInput.classList.remove('invalid');
                senhaInput.classList.remove('invalid');

                showLoginLink.click(); // Simula um clique para mostrar o formulário de login
            } else if (response.status === 400 || response.status === 422) { // Erro de validação (ex: e-mail já existe)
                let errorMessage = 'Erro ao criar usuário. Verifique os dados.';
                if (data.detail) {
                    if (Array.isArray(data.detail)) {
                        // Para erros de validação do Pydantic, a mensagem está em 'msg'
                        errorMessage = data.detail[0].msg || errorMessage;
                    } else if (typeof data.detail === 'string') {
                        // Para erros de HTTP Exception (como e-mail já existe), a mensagem é uma string
                        errorMessage = data.detail;
                    }
                }
                alert(errorMessage);
            } else {
                alert('Ocorreu um erro inesperado no servidor. Tente novamente.');
            }
        } catch (error) {
            console.error('Erro na requisição:', error);
            alert('Não foi possível conectar ao servidor. Verifique sua conexão e tente novamente.');
        } finally {
            // Restaura o botão ao estado original, independentemente do resultado
            submitButton.disabled = false;
            submitButton.textContent = originalButtonText;
        }
    }
});

// Lógica para o formulário de LOGIN
loginForm.addEventListener('submit', async function(event) {
    event.preventDefault();

    const submitButton = loginForm.querySelector('button[type="submit"]');
    const originalButtonText = submitButton.textContent;
    submitButton.disabled = true;
    submitButton.textContent = 'Entrando...';

    // No login, o backend espera os dados como 'form data', não JSON.
    const formData = new URLSearchParams();
    formData.append('username', loginEmailInput.value); // O backend espera 'username' para o login
    formData.append('password', loginSenhaInput.value);

    try {
        const response = await fetch(`${API_BASE_URL}/auth/login_Auth`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: formData,
        });

        const data = await response.json();

        if (response.ok) {
            // Login bem-sucedido!
            localStorage.setItem('accessToken', data.access_token); // Guarda o token
            loginForm.reset();
            updateUIForAuthState(); // Atualiza a UI para o estado "logado"
        } else {
            // Trata erros de login (ex: senha incorreta)
            let errorMessage = 'Email ou senha incorretos.';
            if (data.detail) {
                // Se 'detail' for um array (erro de validação), pega a primeira mensagem.
                if (Array.isArray(data.detail)) {
                    errorMessage = data.detail[0].msg || errorMessage;
                } else if (typeof data.detail === 'string') { // Se for uma string simples.
                    errorMessage = data.detail;
                }
            }
            alert(errorMessage);
        }

    } catch (error) {
        console.error('Erro na requisição de login:', error);
        alert('Não foi possível conectar ao servidor para fazer login.');
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = originalButtonText;
    }
});

// Lógica para alternar entre os formulários
const showLoginLink = document.getElementById('show-login');
const showRegisterLink = document.getElementById('show-register');

showLoginLink.addEventListener('click', (e) => {
    e.preventDefault();
    registerForm.style.display = 'none';
    loginForm.style.display = 'flex';
});

showRegisterLink.addEventListener('click', (e) => {
    e.preventDefault();
    loginForm.style.display = 'none';
    registerForm.style.display = 'flex';
});

// Lógica de Logout
logoutButton.addEventListener('click', () => {
    localStorage.removeItem('accessToken'); // Remove o token
    updateUIForAuthState(); // Atualiza a UI para o estado "não logado"
});

// Função para atualizar a UI com base no estado de autenticação
function updateUIForAuthState() {
    const token = localStorage.getItem('accessToken');
    if (token) {
        // Usuário está logado
        authContainer.style.display = 'none';
        userArea.style.display = 'block';
        loadUserDashboard(); // Carrega os dados do painel
    } else {
        // Usuário não está logado
        authContainer.style.display = 'block';
        userArea.style.display = 'none';
        userArea.innerHTML = ''; // Limpa o painel ao deslogar
        // Garante que o formulário de registro seja o padrão
        loginForm.style.display = 'none';
        registerForm.style.display = 'flex';
    }
}

// Função para carregar o painel do usuário (Dados + Pedidos)
async function loadUserDashboard() {
    const token = localStorage.getItem('accessToken');
    if (!token) return;

    userArea.innerHTML = '<p>Carregando suas informações...</p>';

    try {
        // 1. Buscar dados do usuário
        const userResponse = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!userResponse.ok) throw new Error('Falha ao carregar usuário');
        const userData = await userResponse.json();

        // 2. Buscar pedidos do usuário
        const ordersResponse = await fetch(`${API_BASE_URL}/ordens/listar/pedidos-usuarios`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const ordersData = await ordersResponse.json();

        // 3. Renderizar o Painel
        renderDashboard(userData, ordersData);

    } catch (error) {
        console.error(error);
        userArea.innerHTML = `
            <p style="color:red">Erro ao carregar dados. Tente fazer login novamente.</p>
            <button id="btn-error-logout" style="margin-top: 10px; padding: 10px; background-color: #007bff; color: white; border: none; cursor: pointer; border-radius: 5px;">
                Voltar para Login
            </button>
        `;
        document.getElementById('btn-error-logout').addEventListener('click', () => {
            localStorage.removeItem('accessToken');
            updateUIForAuthState();
        });
    }
}

function renderDashboard(user, orders) {
    // Cria o HTML do painel
    let html = `
        <div class="dashboard-header">
            <h2>Olá, ${user.nome}!</h2>
            <p>Email: ${user.email}</p>
            <button id="btn-novo-pedido" style="margin-top: 10px; padding: 10px; background-color: #28a745; color: white; border: none; cursor: pointer;">
                + Criar Novo Pedido
            </button>
        </div>
        <hr>
        <h3>Seus Pedidos</h3>
    `;

    if (!orders || orders.length === 0) {
        html += '<p>Você ainda não tem pedidos.</p>';
    } else {
        html += '<ul style="list-style: none; padding: 0;">';
        orders.forEach(order => {
            const statusColor = order.status === 'cancelado' ? 'red' : (order.status === 'FINALIZADO' ? 'green' : 'orange');
            
            // Monta a lista de itens existentes no pedido
            let itensHtml = '';
            if (order.itens && order.itens.length > 0) {
                itensHtml = '<ul style="margin: 10px 0; padding-left: 20px; color: #555;">';
                order.itens.forEach(item => {
                    itensHtml += `<li>${item.quantidade}x ${item.sabor} (${item.tamanho}) - R$ ${item.preco_unico.toFixed(2)}</li>`;
                });
                itensHtml += '</ul>';
            } else {
                itensHtml = '<p style="font-size: 0.9em; color: #888;">Nenhum item adicionado.</p>';
            }

            // Gera as opções do select baseadas no MENU_ITENS
            let optionsHtml = '<option value="">Selecione um item...</option>';
            MENU_ITENS.forEach((item, index) => {
                optionsHtml += `<option value="${index}">${item.sabor} - ${item.tamanho} (R$ ${item.preco.toFixed(2)})</option>`;
            });

            html += `
                <li style="border: 1px solid #ddd; margin-bottom: 10px; padding: 10px; border-radius: 5px;">
                    <strong>Pedido #${order.id}</strong> <br>
                    Status: <span style="color: ${statusColor}; font-weight: bold;">${order.status}</span> <br>
                    Total: R$ ${order.preco.toFixed(2)}
                    ${itensHtml}
                    
                    ${order.status === 'pendente' ? `
                        <div style="margin-top: 10px; background: #f9f9f9; padding: 10px; border-radius: 5px; display: flex; gap: 5px; flex-wrap: wrap;">
                            <select id="menu-select-${order.id}" style="flex: 3; min-width: 150px; padding: 5px;">
                                ${optionsHtml}
                            </select>
                            <input type="number" id="qtd-${order.id}" placeholder="Qtd" value="1" style="width: 50px; padding: 5px;">
                            <button onclick="adicionarItem(${order.id})" style="background-color: #007bff; color: white; border: none; padding: 5px 10px; cursor: pointer; border-radius: 3px;">Add</button>
                        </div>
                        <button onclick="finalizarPedido(${order.id})" style="margin-top: 10px; padding: 8px; background-color: #28a745; color: white; border: none; cursor: pointer; border-radius: 3px; width: 100%;">✅ Finalizar Pedido</button>
                        <button onclick="cancelarPedido(${order.id})" style="margin-top: 5px; color: red; cursor: pointer; border: none; background: none; text-decoration: underline; font-size: 0.9em; width: 100%;">Cancelar Pedido</button>
                    ` : ''}
                </li>
            `;
        });
        html += '</ul>';
    }

    userArea.innerHTML = html;

    // Adiciona evento ao botão de criar pedido
    document.getElementById('btn-novo-pedido').addEventListener('click', criarNovoPedido);
}

async function criarNovoPedido() {
    const token = localStorage.getItem('accessToken');

    try {
        const response = await fetch(`${API_BASE_URL}/ordens/pedido`, {
            method: 'POST',
            headers: { 
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            loadUserDashboard(); // Recarrega a lista
        } else {
            alert("Erro ao criar pedido.");
        }
    } catch (error) {
        console.error("Erro:", error);
    }
}

// Função para adicionar item ao pedido
window.adicionarItem = async function(idPedido) {
    const token = localStorage.getItem('accessToken');
    
    // Pega os valores dos inputs específicos deste pedido
    const menuIndex = document.getElementById(`menu-select-${idPedido}`).value;
    const quantidade = document.getElementById(`qtd-${idPedido}`).value;

    if (menuIndex === "" || !quantidade) {
        alert("Por favor, selecione um item e a quantidade.");
        return;
    }

    const itemSelecionado = MENU_ITENS[menuIndex];

    try {
        const response = await fetch(`${API_BASE_URL}/ordens/pedido/adicionar-item/${idPedido}`, {
            method: 'POST',
            headers: { 
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                sabor: itemSelecionado.sabor,
                tamanho: itemSelecionado.tamanho,
                quantidade: parseInt(quantidade),
                preco_unico: itemSelecionado.preco
            })
        });

        if (response.ok) {
            loadUserDashboard(); // Atualiza a lista para mostrar o novo item e o novo preço total
        } else {
            const data = await response.json();
            alert(data.detail || "Erro ao adicionar item.");
        }
    } catch (error) {
        console.error("Erro:", error);
    }
};

// Função para finalizar o pedido
window.finalizarPedido = async function(id) {
    const token = localStorage.getItem('accessToken');

    try {
        const response = await fetch(`${API_BASE_URL}/ordens/pedido/terminar/${id}`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            loadUserDashboard(); // Recarrega a lista para mostrar como FINALIZADO
        } else {
            const data = await response.json();
            alert(data.detail || "Erro ao finalizar pedido.");
        }
    } catch (error) {
        console.error("Erro:", error);
    }
};

// Função global para ser acessada pelo onclick no HTML injetado
window.cancelarPedido = async function(id) {
    const token = localStorage.getItem('accessToken');

    try {
        const response = await fetch(`${API_BASE_URL}/ordens/pedido/cancelar/${id}`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (response.ok) {
            loadUserDashboard(); // Recarrega a lista
        } else {
            const data = await response.json();
            alert(data.detail || "Erro ao cancelar.");
        }
    } catch (error) {
        console.error("Erro:", error);
    }
};

function clearErrors() {
    nomeError.textContent = '';
    emailError.textContent = '';
    senhaError.textContent = '';
}

function validateNome() {
    if (nomeInput.value.trim() === '') {
        nomeError.textContent = 'O campo nome é obrigatório.';
        nomeInput.classList.add('invalid');
        return false;
    }
    nomeError.textContent = '';
    nomeInput.classList.remove('invalid');
    return true;
}

function validateEmail() {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (emailInput.value.trim() === '' || !emailRegex.test(emailInput.value)) {
        emailError.textContent = 'Por favor, insira um e-mail válido.';
        emailInput.classList.add('invalid');
        return false;
    }
    emailError.textContent = '';
    emailInput.classList.remove('invalid');
    return true;
}

function validateSenha() {
    if (senhaInput.value.trim().length < 6) {
        senhaError.textContent = 'A senha deve ter pelo menos 6 caracteres.';
        senhaInput.classList.add('invalid');
        return false;
    }
    senhaError.textContent = '';
    senhaInput.classList.remove('invalid');
    return true;
}

// Verifica o estado de login assim que a página carrega
document.addEventListener('DOMContentLoaded', updateUIForAuthState);