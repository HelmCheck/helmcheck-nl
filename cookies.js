const CookieConsent = {
    getConsent: function () {
        try {
            return JSON.parse(localStorage.getItem('hc_cookie_consent'));
        } catch (e) {
            return null;
        }
    },
    saveConsent: function (analytics, marketing) {
        const prefs = { necessary: true, analytics: analytics, marketing: marketing, date: new Date().toISOString() };
        localStorage.setItem('hc_cookie_consent', JSON.stringify(prefs));
        this.hideAll();
        this.applyScripts(prefs);
    },
    applyScripts: function (prefs) {
        if (!prefs) return;
        document.querySelectorAll('script[type="text/plain"][data-category]').forEach(function (el) {
            const cat = el.getAttribute('data-category');
            if ((cat === 'analytics' && prefs.analytics) || (cat === 'marketing' && prefs.marketing)) {
                const s = document.createElement('script');
                if (el.src) s.src = el.src;
                else s.textContent = el.textContent;
                document.body.appendChild(s);
                el.removeAttribute('data-category');
            }
        });
    },
    hideAll: function () {
        const b = document.getElementById('hc-cookie-banner');
        const m = document.getElementById('hc-cookie-modal');
        if (b) b.remove();
        if (m) m.remove();
    },
    showBanner: function () {
        if (document.getElementById('hc-cookie-banner')) return;
        const banner = document.createElement('div');
        banner.id = 'hc-cookie-banner';
        banner.style.cssText = 'position:fixed;bottom:16px;left:16px;right:16px;max-width:460px;background:#0f172a;color:#f8fafc;padding:18px 20px;border-radius:16px;box-shadow:0 10px 25px rgba(0,0,0,0.25);z-index:9999;font-family:inherit;font-size:14px;line-height:1.5;';
        banner.innerHTML = `
            <div style="font-weight:800;font-size:16px;margin-bottom:6px;">Wij respecteren jouw privacy</div>
    <p style="color:#cbd5e1;margin-bottom:14px;font-size:13px;">Helmcheck.nl gebruikt noodzakelijke cookies en – alleen met jouw toestemming – anonieme statistieken om de keuzehulp te verbeteren. Lees meer in onze <a href="/privacy-en-disclaimer.html" style="color:#38bdf8;text-decoration:underline;">Privacy &amp; Disclaimer</a>.</p>
            <div style="display:flex;gap:8px;flex-wrap:wrap;">
                <button id="hc-accept-all" style="flex:1;background:#0284c7;color:#fff;border:none;padding:9px 12px;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px;">Alles accepteren</button>
                <button id="hc-accept-nec" style="flex:1;background:#334155;color:#fff;border:none;padding:9px 12px;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px;">Alleen noodzakelijk</button>
                <button id="hc-open-prefs" style="width:100%;background:transparent;color:#94a3b8;border:1px solid #334155;padding:7px 12px;border-radius:8px;font-weight:600;cursor:pointer;font-size:12px;">Voorkeuren beheren</button>
            </div>
        `;
        document.body.appendChild(banner);
        document.getElementById('hc-accept-all').onclick = () => this.saveConsent(true, true);
        document.getElementById('hc-accept-nec').onclick = () => this.saveConsent(false, false);
        document.getElementById('hc-open-prefs').onclick = () => this.showPreferences();
    },
    showPreferences: function () {
        this.hideAll();
        const saved = this.getConsent() || { analytics: false, marketing: false };
        const modal = document.createElement('div');
        modal.id = 'hc-cookie-modal';
        modal.style.cssText = 'position:fixed;inset:0;background:rgba(15,23,42,0.7);display:flex;align-items:center;justify-content:center;padding:16px;z-index:10000;font-family:inherit;';
        modal.innerHTML = `
            <div style="background:#ffffff;color:#0f172a;max-width:460px;width:100%;border-radius:16px;padding:22px;box-shadow:0 20px 35px rgba(0,0,0,0.3);font-size:14px;line-height:1.5;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                    <strong style="font-size:17px;">Cookie-instellingen</strong>
                    <button id="hc-close-modal" style="background:none;border:none;font-size:20px;cursor:pointer;color:#64748b;">&times;</button>
                </div>
                <div style="border-bottom:1px solid #e2e8f0;padding:10px 0;">
                    <div style="display:flex;justify-content:space-between;font-weight:700;"><span>Noodzakelijke cookies</span><span style="color:#0284c7;font-size:12px;">Altijd actief</span></div>
                    <p style="font-size:12px;color:#64748b;margin-top:4px;">Nodig om de website goed te laten werken en je keuze te onthouden.</p>
                </div>
                <div style="border-bottom:1px solid #e2e8f0;padding:10px 0;">
                    <label style="display:flex;justify-content:space-between;align-items:center;font-weight:700;cursor:pointer;">
                        <span>Analytische cookies</span>
                        <input type="checkbox" id="hc-chk-ana" ${saved.analytics ? 'checked' : ''} style="width:18px;height:18px;">
                    </label>
                    <p style="font-size:12px;color:#64748b;margin-top:4px;">Helpen ons anoniem te zien welke pagina's het meest gelezen worden.</p>
                </div>
                <div style="padding:10px 0 16px;">
                    <label style="display:flex;justify-content:space-between;align-items:center;font-weight:700;cursor:pointer;">
                        <span>Overige / Externe media cookies</span>
                        <input type="checkbox" id="hc-chk-mkt" ${saved.marketing ? 'checked' : ''} style="width:18px;height:18px;">
                    </label>
                    <p style="font-size:12px;color:#64748b;margin-top:4px;">Voor eventuele ingesloten video's of externe inhoud (op dit moment niet actief op Helmcheck.nl).</p>
                </div>
                <div style="display:flex;gap:8px;">
                    <button id="hc-save-prefs" style="flex:1;background:#0284c7;color:#fff;border:none;padding:10px;border-radius:8px;font-weight:700;cursor:pointer;">Opslaan</button>
                    <button id="hc-modal-all" style="flex:1;background:#0f172a;color:#fff;border:none;padding:10px;border-radius:8px;font-weight:700;cursor:pointer;">Alles accepteren</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        document.getElementById('hc-close-modal').onclick = () => this.hideAll();
        document.getElementById('hc-save-prefs').onclick = () => {
            this.saveConsent(document.getElementById('hc-chk-ana').checked, document.getElementById('hc-chk-mkt').checked);
        };
        document.getElementById('hc-modal-all').onclick = () => this.saveConsent(true, true);
    },
    init: function () {
        const saved = this.getConsent();
        if (!saved) {
            this.showBanner();
        } else {
            this.applyScripts(saved);
        }
    }
};

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => CookieConsent.init());
} else {
    CookieConsent.init();
}
