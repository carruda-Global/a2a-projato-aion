import React, { useState } from 'react';

const PrivacyConsent = ({ user, onConsentGiven }) => {
    const [accepted, setAccepted] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [showPolicy, setShowPolicy] = useState(false);
    const [showTerms, setShowTerms] = useState(false);

    const handleConsent = async () => {
        if (!accepted) { setError('Voce precisa aceitar os termos para continuar'); return; }
        setLoading(true); setError(null);
        try {
            await fetch('/api/privacy/consent', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    user_id: user.id, email: user.email,
                    consent_given: true, consent_version: '1.0',
                    privacy_policy_accepted: true, terms_of_service_accepted: true,
                    ip_address: user.ip, user_agent: navigator.userAgent
                })
            });
            onConsentGiven(true);
        } catch (err) {
            setError('Erro ao registrar consentimento');
        }
        setLoading(false);
    };

    return (
        <div className="privacy-consent">
            <h2>Politica de Privacidade e Termos de Uso</h2>
            <div className="consent-text">
                <p>Para continuar usando a plataforma AION, voce precisa aceitar nossa{' '}
                    <button className="link-button" onClick={() => setShowPolicy(true)}>Politica de Privacidade</button>
                    {' '}e{' '}
                    <button className="link-button" onClick={() => setShowTerms(true)}>Termos de Uso</button>.
                </p>
            </div>
            <div className="consent-checkbox">
                <label>
                    <input type="checkbox" checked={accepted} onChange={(e) => setAccepted(e.target.checked)} />
                    Li e concordo com a Politica de Privacidade e os Termos de Uso
                </label>
            </div>
            {error && <div className="error-message">{error}</div>}
            <button className="btn btn-primary" onClick={handleConsent} disabled={loading}>
                {loading ? 'Processando...' : 'Continuar'}
            </button>
            {showPolicy && (
                <div className="modal" onClick={() => setShowPolicy(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <button className="modal-close" onClick={() => setShowPolicy(false)}>&times;</button>
                        <iframe src="/api/privacy/policy" className="modal-iframe" title="Politica de Privacidade" />
                    </div>
                </div>
            )}
            {showTerms && (
                <div className="modal" onClick={() => setShowTerms(false)}>
                    <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                        <button className="modal-close" onClick={() => setShowTerms(false)}>&times;</button>
                        <iframe src="/api/privacy/terms" className="modal-iframe" title="Termos de Uso" />
                    </div>
                </div>
            )}
        </div>
    );
};

export default PrivacyConsent;
