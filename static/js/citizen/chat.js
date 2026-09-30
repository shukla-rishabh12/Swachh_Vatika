(function () {
  let conversationId = null;

  async function init() {
    const user = await window.auth.load();
    if (!window.auth.requireRole('CITIZEN')) return;

    window.navigation.build('CITIZEN');
    window.notif.updateBadge();
    document.getElementById('user-email').textContent = user.email || '';

    // Try to load an existing conversation, else create
    try {
      const res = await window.api.get('/ai/conversations?page=1&page_size=1');
      const items = res.data.items || [];
      if (items.length > 0) {
        conversationId = items[0].id;
        await loadMessages();
      }
    } catch (e) { /* ignore */ }

    document.getElementById('new-chat-btn').addEventListener('click', () => startNewChat());

    document.getElementById('chat-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const input = document.getElementById('chat-input');
      const msg = input.value.trim();
      if (!msg) return;

      input.value = '';
      appendMessage('USER', msg);
      await sendMessage(msg);
    });
  }

  async function startNewChat() {
    try {
      const res = await window.api.post('/ai/conversations', {});
      conversationId = res.data.conversation_id;
      document.getElementById('chat-messages').innerHTML =
        '<div class="chat-placeholder">New conversation started.</div>';
    } catch (e) {
      window.utils.toast('Could not start new chat.', 'error');
    }
  }

  async function loadMessages() {
    try {
      const res = await window.api.get(`/ai/conversations/${conversationId}/messages`);
      const msgs = res.data || [];
      const box = document.getElementById('chat-messages');
      box.innerHTML = '';
      if (msgs.length === 0) {
        box.innerHTML = '<div class="chat-placeholder">Ask me anything.</div>';
        return;
      }
      msgs.forEach(m => appendMessage(m.sender_type, m.message));
    } catch (e) { /* ignore */ }
  }

  async function sendMessage(msg) {
    const box = document.getElementById('chat-messages');
    const typing = document.createElement('div');
    typing.className = 'chat-bubble chat-ai typing';
    typing.textContent = 'Thinking...';
    box.appendChild(typing);
    box.scrollTop = box.scrollHeight;

    const sendBtn = document.getElementById('send-btn');
    sendBtn.disabled = true;

    try {
      const res = await window.api.post('/ai/chat', {
        conversation_id: conversationId,
        message: msg,
      });
      if (!conversationId && res.data.conversation_id) {
        conversationId = res.data.conversation_id;
      }
      typing.remove();
      appendMessage('AI', res.data.message);
    } catch (err) {
      typing.remove();
      appendMessage('AI', err.message || 'AI assistant is unavailable right now.');
    } finally {
      sendBtn.disabled = false;
    }
  }

  function appendMessage(sender, text) {
    const box = document.getElementById('chat-messages');
    const placeholder = box.querySelector('.chat-placeholder');
    if (placeholder) placeholder.remove();

    const el = document.createElement('div');
    el.className = `chat-bubble ${sender === 'USER' ? 'chat-user' : 'chat-ai'}`;
    el.textContent = text;
    box.appendChild(el);
    box.scrollTop = box.scrollHeight;
  }

  document.addEventListener('DOMContentLoaded', init);
})();