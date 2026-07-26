(function () {
  const ANALYTICS_VISIT_COOLDOWN_MS = 30 * 60 * 1000;
  const LOCAL_HOSTS = new Set(['localhost', '127.0.0.1', '::1']);

  function getMetaContent(name) {
    const el = document.querySelector(`meta[name="${name}"]`);
    const value = el ? el.getAttribute('content') : '';
    return String(value || '').trim();
  }

  function getAnalyticsConfig() {
    return {
      endpoint: getMetaContent('analytics-endpoint'),
      siteId: getMetaContent('analytics-site-id'),
    };
  }

  function getVisitStorageKey(siteId) {
    return `analytics:last-visit:${siteId}`;
  }

  function shouldTrackAnalytics() {
    if (window.location.protocol !== 'http:' && window.location.protocol !== 'https:') return false;
    const host = String(window.location.hostname || '').toLowerCase();
    if (LOCAL_HOSTS.has(host) || host.endsWith('.local')) return false;
    return true;
  }

  function shouldCountVisit(siteId) {
    try {
      const lastVisit = Number.parseInt(window.localStorage.getItem(getVisitStorageKey(siteId)) || '', 10);
      if (Number.isFinite(lastVisit) && Date.now() - lastVisit < ANALYTICS_VISIT_COOLDOWN_MS) {
        return false;
      }
    } catch {
      return true;
    }
    return true;
  }

  function rememberVisit(siteId) {
    try {
      window.localStorage.setItem(getVisitStorageKey(siteId), String(Date.now()));
    } catch {
      // Tracking must stay best-effort and silent.
    }
  }

  function loadAnalytics() {
    if (!shouldTrackAnalytics()) return;
    const cfg = getAnalyticsConfig();
    if (!cfg.endpoint || !cfg.siteId) return;

    const countVisit = shouldCountVisit(cfg.siteId);
    const callbackName = `__analyticsCallback_${Date.now().toString(36)}_${Math.random().toString(36).slice(2)}`;
    const params = new URLSearchParams();
    const script = document.createElement('script');
    let settled = false;
    let timeoutId = 0;

    params.set('site', cfg.siteId);
    params.set('callback', callbackName);
    params.set('page_url', window.location.href);
    params.set('referrer', document.referrer || '');
    if (!countVisit) params.set('summary_only', '1');

    const cleanup = function () {
      if (settled) return;
      settled = true;
      if (timeoutId) window.clearTimeout(timeoutId);
      try {
        delete window[callbackName];
      } catch {
        window[callbackName] = undefined;
      }
      script.remove();
    };

    window[callbackName] = function (payload) {
      try {
        if (countVisit && payload && payload.ok) {
          rememberVisit(cfg.siteId);
        }
      } finally {
        cleanup();
      }
    };

    script.async = true;
    script.src = `${cfg.endpoint}${cfg.endpoint.includes('?') ? '&' : '?'}${params.toString()}`;
    script.onerror = cleanup;
    timeoutId = window.setTimeout(cleanup, 4000);
    document.head.appendChild(script);
  }

  function scheduleAnalyticsLoad() {
    if (!shouldTrackAnalytics()) return;
    const run = function () {
      window.setTimeout(loadAnalytics, 0);
    };
    // Un <script async> inyectado antes de que se dispare «load» retrasa ese
    // evento hasta que la peticion termina. Si el servidor de estadisticas se
    // cuelga, «load» no llegaria a dispararse nunca. Por eso se espera siempre
    // a «load» antes de programar nada.
    var programar = function () {
      if (typeof window.requestIdleCallback === 'function') {
        window.requestIdleCallback(run, { timeout: 2500 });
      } else {
        window.setTimeout(run, 0);
      }
    };
    if (document.readyState === 'complete') {
      programar();
      return;
    }
    window.addEventListener('load', programar, { once: true });
  }

  scheduleAnalyticsLoad();
})();
