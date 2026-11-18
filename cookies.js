// Laad CSS van Orest Bida's cookieconsent
const ccCss = document.createElement('link');
ccCss.rel = 'stylesheet';
ccCss.href = 'https://jsdelivr.net';
document.head.appendChild(ccCss);

// Laad JS en start de banner
const ccScript = document.createElement('script');
ccScript.src = 'https://jsdelivr.net';
ccScript.onload = function () {
    CookieConsent.run({
        guiOptions: {
            consentModal: {
                layout: 'box',
                position: 'bottom left',
                equalWeightButtons: true,
                flipButtons: false
            },
            preferencesModal: {
                layout: 'box',
                position: 'right',
                equalWeightButtons: true,
                flipButtons: false
            }
        },
        categories: {
            necessary: {
                readOnly: true
            },
            analytics: {},
            marketing: {}
        },
        language: {
            default: 'nl',
            translations: {
                nl: {
                    consentModal: {
                        title: 'Wij respecteren jouw privacy',
                        description: 'Helmcheck.nl gebruikt noodzakelijke cookies om de site goed te laten werken en – alleen met jouw toestemming – marketingcookies voor affiliate-productlinks. Lees meer in onze <a href="privacy-en-disclaimer.html">Privacyverklaring & Disclaimer</a>.',
                        acceptAllBtn: 'Alles accepteren',
                        acceptNecessaryBtn: 'Alleen noodzakelijk',
                        showPreferencesBtn: 'Voorkeuren beheren'
                    },
                    preferencesModal: {
                        title: 'Cookie-instellingen',
                        acceptAllBtn: 'Alles accepteren',
                        acceptNecessaryBtn: 'Alleen noodzakelijk',
                        savePreferencesBtn: 'Instellingen opslaan',
                        closeIconLabel: 'Sluiten',
                        sections: [
                            {
                                title: 'Jouw privacy op Helmcheck.nl',
                                description: 'Je kunt onze keuzehulp volledig anoniem gebruiken. Hieronder kies je zelf welke cookies je wel of niet toestaat.'
                            },
                            {
                                title: 'Noodzakelijke cookies <span class="pm__badge">Altijd actief</span>',
                                description: 'Deze cookies zijn nodig om de website technisch goed te laten werken en om jouw gekozen cookievoorkeuren te onthouden.',
                                linkedCategory: 'necessary'
                            },
                            {
                                title: 'Analytische cookies',
                                description: 'Helpen ons om anoniem te zien welke pagina’s en keuzehulp-vragen het meest worden gebruikt, zodat we de informatie kunnen verbeteren.',
                                linkedCategory: 'analytics'
                            },
                            {
                                title: 'Marketing & Affiliate cookies',
                                description: 'Worden gebruikt door affiliate-partners (zoals Bol.com of Coolblue) wanneer je op een aanbevolen helm klikt, zodat wij een kleine commissie ontvangen zonder extra kosten voor jou.',
                                linkedCategory: 'marketing'
                            }
                        ]
                    }
                }
            }
        }
    });
};
document.body.appendChild(ccScript);
