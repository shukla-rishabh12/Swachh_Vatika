/**
 * Central API helper. All fetch calls go through this.
 */
(function () {
  const BASE = '/api/v1';

  async function request(method, path, body = null, options = {}) {
    const url = path.startsWith('http') ? path : BASE + path;
    const opts = {
      method,
      credentials: 'include',
      headers: { 'Accept': 'application/json' },
      ...options,
    };

    if (body instanceof FormData) {
      opts.body = body;
    } else if (body !== null && body !== undefined) {
      opts.headers['Content-Type'] = 'application/json';
      opts.body = JSON.stringify(body);
    }

    let res, data;
    try {
      res = await fetch(url, opts);
    } catch (err) {
      throw { success: false, message: 'Network error. Check your connection.', error: { code: 'NETWORK_ERROR' } };
    }

    try {
      data = await res.json();
    } catch (err) {
      data = { success: false, message: 'Invalid server response.', error: { code: 'BAD_JSON' } };
    }

    if (!res.ok || data.success === false) {
      if (res.status === 401 && !options.silent) {
        const p = window.location.pathname;
        if (!p.includes('/login') && !p.includes('/register') && p !== '/') {
          window.location.href = '/auth/login.html';
        }
      }
      throw data;
    }
    return data;
  }

  const api = {
    get:    (path, options)       => request('GET',    path, null, options),
    post:   (path, body, options) => request('POST',   path, body, options),
    patch:  (path, body, options) => request('PATCH',  path, body, options),
    delete: (path, options)       => request('DELETE', path, null, options),
    upload: (path, formData, options) => request('POST', path, formData, options),
  };

  window.api = api;
})();