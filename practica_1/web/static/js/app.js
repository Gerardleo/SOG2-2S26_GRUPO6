document.addEventListener('DOMContentLoaded', () => {
    // Referencias al DOM
    const chatMessages = document.getElementById('chatMessages');
    const chatForm = document.getElementById('chatForm');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const clearChatBtn = document.getElementById('clearChatBtn');
    const toggleSidebarBtn = document.getElementById('toggleSidebarBtn');
    const sidebar = document.querySelector('.sidebar');
    const chartsGallery = document.getElementById('chartsGallery');
    const quickPrompts = document.querySelectorAll('.prompt-chip');

    // Modal
    const modal = document.getElementById('imageModal');
    const modalClose = document.getElementById('modalClose');
    const modalImg = document.getElementById('modalImg');
    const modalTitle = document.getElementById('modalTitle');
    const modalDesc = document.getElementById('modalDesc');

    let isGenerating = false;
    let sessionId = 'sesion_' + Math.random().toString(36).substring(2, 9);

    // Ajuste automático de altura de textarea
    userInput.addEventListener('input', () => {
        userInput.style.height = 'auto';
        userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
    });

    // Enviar con Enter (Shift+Enter para salto de línea)
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!isGenerating && userInput.value.trim().length > 0) {
                chatForm.dispatchEvent(new Event('submit'));
            }
        }
    });

    // Enviar formulario de chat
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const text = userInput.value.trim();
        if (!text || isGenerating) return;

        // Agregar mensaje de usuario
        appendMessage('user', text);
        userInput.value = '';
        userInput.style.height = 'auto';
        userInput.focus();

        // Agregar burbuja de respuesta del asistente con indicador de carga
        const assistantMsgEl = appendMessage('assistant', '', true);
        const contentEl = assistantMsgEl.querySelector('.message-content');

        setGeneratingState(true);

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: text,
                    session_id: sessionId
                })
            });

            if (!response.ok) {
                const errData = await response.json().catch(() => ({}));
                throw new Error(errData.detail || `Error HTTP ${response.status}`);
            }

            // Lectura por streaming
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let accumulatedText = '';
            let isFirstChunk = true;

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                const chunk = decoder.decode(value, { stream: true });
                accumulatedText += chunk;

                if (isFirstChunk) {
                    contentEl.innerHTML = '';
                    isFirstChunk = false;
                }

                // Renderizar markdown progresivo
                renderFormattedMarkdown(contentEl, accumulatedText);
                scrollToBottom();
            }

            // Post-procesar para incrustar gráficos referenciados
            enhanceContentWithImages(contentEl);
            scrollToBottom();

        } catch (error) {
            console.error('Error en chat:', error);
            contentEl.innerHTML = `
                <p style="color: #f87171;"><i class="fa-solid fa-triangle-exclamation"></i> 
                <strong>Error al procesar la consulta:</strong> ${error.message}</p>
                <p style="font-size: 0.8rem; color: #94a3b8;">Verifique que su clave de API de Gemini esté activa en el archivo .env o reintente en unos momentos.</p>
            `;
        } finally {
            setGeneratingState(false);
        }
    });

    // Agregar mensaje al historial
    function appendMessage(role, text, isPending = false) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${role}-message`;

        const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        const isUser = role === 'user';

        msgDiv.innerHTML = `
            <div class="avatar">
                <i class="${isUser ? 'fa-solid fa-user' : 'fa-solid fa-robot'}"></i>
            </div>
            <div class="message-body">
                <div class="message-header">
                    <span class="sender-name">${isUser ? 'Tú' : 'Analista IA (Google ADK)'}</span>
                    <span class="message-time">${timeStr}</span>
                </div>
                <div class="message-content">
                    ${isPending ? `
                        <div class="typing-indicator">
                            <span class="typing-dot"></span>
                            <span class="typing-dot"></span>
                            <span class="typing-dot"></span>
                        </div>
                    ` : DOMPurify.sanitize(marked.parse(text))}
                </div>
            </div>
        `;

        chatMessages.appendChild(msgDiv);
        scrollToBottom();
        return msgDiv;
    }

    // Renderizar Markdown seguro
    function renderFormattedMarkdown(element, markdownText) {
        const rawHtml = marked.parse(markdownText);
        element.innerHTML = DOMPurify.sanitize(rawHtml);
    }

    // Detectar menciones de gráficos e incrustar tarjetas interactivas
    function enhanceContentWithImages(element) {
        const chartPatterns = [
            { id: 'g1', file: 'g1_segmentacion_edad_venta.png', title: 'Distribución de Venta por Edad' },
            { id: 'g2', file: 'g2_segmentacion_edad_compras.png', title: 'Compras Promedio por Edad' },
            { id: 'g3', file: 'g3_segmentacion_genero.png', title: 'Comportamiento por Género' },
            { id: 'g4', file: 'g4_segmentacion_boletin_vale.png', title: 'Impacto de Boletines y Vales' },
            { id: 'g5', file: 'g5_correlacion_edad_venta.png', title: 'Correlación Edad vs Venta' },
            { id: 'g6', file: 'g6_correlacion_genero_metodopago.png', title: 'Métodos de Pago por Género' },
            { id: 'g7', file: 'g7_correlacion_boletin_vale.png', title: 'Correlación Boletín y Vales' }
        ];

        const textContent = element.innerText || element.textContent;

        chartPatterns.forEach(chart => {
            if (textContent.includes(chart.file) || textContent.includes(chart.id) || textContent.includes(`salida/graficas/${chart.file}`)) {
                // Verificar que no se haya insertado ya
                if (!element.querySelector(`[data-chart-id="${chart.id}"]`)) {
                    const card = document.createElement('div');
                    card.className = 'embedded-chart-card';
                    card.setAttribute('data-chart-id', chart.id);
                    card.innerHTML = `
                        <img src="/graficas/${chart.file}" alt="${chart.title}" loading="lazy">
                        <div class="embedded-chart-footer">
                            <span><i class="fa-solid fa-chart-line"></i> ${chart.title}</span>
                            <span><i class="fa-solid fa-magnifying-glass-plus"></i> Clic para ampliar</span>
                        </div>
                    `;
                    card.addEventListener('click', () => {
                        openModal(`/graficas/${chart.file}`, chart.title, 'Gráfica de análisis generada para la práctica.');
                    });
                    element.appendChild(card);
                }
            }
        });
    }

    // Scroll al final
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Estado de generación
    function setGeneratingState(generating) {
        isGenerating = generating;
        sendBtn.disabled = generating;
        if (generating) {
            sendBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
        } else {
            sendBtn.innerHTML = '<i class="fa-solid fa-paper-plane"></i>';
        }
    }

    // Consultas Rápidas (Chips)
    quickPrompts.forEach(btn => {
        btn.addEventListener('click', () => {
            const prompt = btn.getAttribute('data-prompt');
            if (prompt && !isGenerating) {
                userInput.value = prompt;
                userInput.style.height = 'auto';
                userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
                chatForm.dispatchEvent(new Event('submit'));
            }
        });
    });

    // Cargar galería de gráficos en la barra lateral
    async function loadChartsGallery() {
        try {
            const res = await fetch('/api/graficas');
            if (!res.ok) return;
            const data = await res.json();
            
            chartsGallery.innerHTML = '';
            data.graficas.forEach(g => {
                const card = document.createElement('div');
                card.className = 'chart-sidebar-card';
                const filename = g.archivo.split('/').pop();
                
                card.innerHTML = `
                    <img src="/graficas/${filename}" alt="${g.titulo}" class="chart-thumb">
                    <div class="chart-info">
                        <h4>${g.titulo}</h4>
                        <span>${g.tipo}</span>
                    </div>
                `;
                card.addEventListener('click', () => {
                    openModal(`/graficas/${filename}`, g.titulo, g.descripcion);
                });
                chartsGallery.appendChild(card);
            });
        } catch (err) {
            console.error('Error cargando galería:', err);
        }
    }

    // Modal para imágenes
    function openModal(imgSrc, title, desc) {
        modalImg.src = imgSrc;
        modalTitle.textContent = title;
        modalDesc.textContent = desc;
        modal.style.display = 'flex';
    }

    modalClose.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });

    // Limpiar chat
    clearChatBtn.addEventListener('click', () => {
        chatMessages.innerHTML = `
            <div class="message assistant-message">
                <div class="avatar">
                    <i class="fa-solid fa-robot"></i>
                </div>
                <div class="message-body">
                    <div class="message-header">
                        <span class="sender-name">Analista IA (Google ADK)</span>
                        <span class="message-time">Ahora</span>
                    </div>
                    <div class="message-content">
                        <p>Conversación reiniciada. ¿Qué análisis de las ventas online 2021 deseas explorar ahora?</p>
                    </div>
                </div>
            </div>
        `;
        sessionId = 'sesion_' + Math.random().toString(36).substring(2, 9);
    });

    // Toggle de Sidebar (Responsive)
    toggleSidebarBtn.addEventListener('click', () => {
        sidebar.classList.toggle('open');
    });

    // Iniciar carga de gráficos
    loadChartsGallery();
});
