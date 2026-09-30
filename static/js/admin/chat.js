/**
 * Admin — AI Chat page
 * URL: /admin/chat.html
 */
(function () {
  let conversationId = null;

  console.log('[admin/chat] Script loaded');

  async function init() {
    try {
      if (!window.api || !window.auth || !window.utils) {
        console.error('Core JS missing');
        return;
      }

      const user = await window.auth.load();
      if (!user) { window.location.href = '/auth/login.html'; return; }
      if (user.role !== 'ADMIN') { window.location.href = '/403.html'; return; }

      try { window.navigation.build('ADMIN'); } catch (e) {}
      try { window.notif.updateBadge(); } catch (e) {}

      const emailEl = document.getElementById('user-email');
      if (emailEl) emailEl.textContent = user.email || '';

      // Try to load an existing conversation, else create new
      try {
        const res = await window.api.get('/ai/conversations?page=1&page_size=1');
        const items = res.data.items || [];
        if (items.length > 0) {
          conversationId = items[0].id;
          await loadMessages();
        }
      } catch (e) {
        console.warn('No existing conversation:', e);
      }

      const newChatBtn = document.getElementById('new-chat-btn');
      if (newChatBtn) {
        newChatBtn.addEventListener('click', startNewChat);
      }

      const form = document.getElementById('chat-form');
      if (form) {
        form.addEventListener('submit', async (e) => {
          e.preventDefault();
          const input = document.getElementById('chat-input');
          const msg = input.value.trim();
          if (!msg) return;

          input.value = '';
          appendMessage('USER', msg);
          await sendMessage(msg);
        });
      }
    } catch (err) {
      console.error('[admin/chat] init error:', err);
      window.utils.toast('Failed to initialize chat.', 'error');
    }
  }

  async function startNewChat() {
    try {
      const res = await window.api.post('/ai/conversations', {
        title: 'Admin conversation'
      });
      conversationId = res.data.conversation_id;
      const box = document.getElementById('chat-messages');
      if (box) {
        box.innerHTML = '<div class="chat-placeholder">New conversation started. Ask anything about platform analytics.</div>';
      }
      window.utils.toast('New conversation started.', 'success');
    } catch (e) {
      window.utils.toast('Could not start new chat.', 'error');
    }
  }

  async function loadMessages() {
    try {
      const res = await window.api.get(`/ai/conversations/${conversationId}/messages`);
      const msgs = res.data || [];
      const box = document.getElementById('chat-messages');
      if (!box) return;

      box.innerHTML = '';
      if (msgs.length === 0) {
        box.innerHTML = '<div class="chat-placeholder">Ask me anything about platform analytics, complaints, workers, or tasks.</div>';
        return;
      }
      msgs.forEach(m => appendMessage(m.sender_type, m.message));
    } catch (e) {
      console.warn('Failed to load messages:', e);
    }
  }

  async function sendMessage(msg) {
    const box = document.getElementById('chat-messages');
    if (!box) return;

    // Typing indicator
    const typing = document.createElement('div');
    typing.className = 'chat-bubble chat-ai typing';
    typing.textContent = 'Thinking...';
    box.appendChild(typing);
    box.scrollTop = box.scrollHeight;

    const sendBtn = document.getElementById('send-btn');
    if (sendBtn) sendBtn.disabled = true;

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
      appendMessage('AI', err.message || 'AI assistant is unavailable right now. Please try again.');
    } finally {
      if (sendBtn) sendBtn.disabled = false;
    }
  }

  function appendMessage(sender, text) {
    const box = document.getElementById('chat-messages');
    if (!box) return;

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