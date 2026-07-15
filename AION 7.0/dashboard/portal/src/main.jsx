import { StrictMode, Suspense } from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './index.css';
import './i18n/config';

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <Suspense fallback={<div className="loading">Carregando...</div>}>
      <App />
    </Suspense>
  </StrictMode>,
);
