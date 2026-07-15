import { useEffect } from 'react';
import { Link } from 'react-router-dom';

export default function Support() {
  useEffect(() => { document.title = 'Suporte | EcoSystem AEC'; }, []);
  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold mb-8">Suporte e Ajuda</h1>

      <div className="grid md:grid-cols-2 gap-8 mb-12">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h2 className="text-xl font-semibold mb-4">Email de Suporte</h2>
          <p className="text-gray-700 mb-2">
            Envie suas duvidas, problemas ou sugestoes:
          </p>
          <a href="mailto:suporte@ecosystemaec.com.br" className="text-blue-600 hover:underline text-lg font-medium">
            suporte@ecosystemaec.com.br
          </a>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <h2 className="text-xl font-semibold mb-4">Horario de Atendimento</h2>
          <p className="text-gray-700">
            Dias uteis: 9h as 18h (Brasilia)<br />
            Tempo de resposta: ate 24h uteis<br />
            Emergencias: respondemos em ate 4h uteis
          </p>
        </div>
      </div>

      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-4">Perguntas Frequentes</h2>
        <div className="space-y-4">
          <details className="bg-white p-4 rounded-lg border">
            <summary className="font-medium cursor-pointer">Como funciona o periodo de trial?</summary>
            <p className="mt-2 text-gray-700">
              Todos os planos oferecem 15 dias de trial gratuito. Nao e necessario
              cartao de credito para comecar.
            </p>
          </details>
          <details className="bg-white p-4 rounded-lg border">
            <summary className="font-medium cursor-pointer">Posso cancelar a qualquer momento?</summary>
            <p className="mt-2 text-gray-700">
              Sim. O cancelamento pode ser feito pelo painel ou entrando em contato
              com o suporte. O acesso continua ate o fim do periodo pago.
            </p>
          </details>
          <details className="bg-white p-4 rounded-lg border">
            <summary className="font-medium cursor-pointer">Como funciona a seguranca dos meus dados?</summary>
            <p className="mt-2 text-gray-700">
              Seus dados sao criptografados em transito (TLS 1.3) e em repouso (AES-256).
              Agentes com dados sensiveis (NR-1, LGPD) rodam em LLM segregado.
              Veja nossa <Link to="/privacy" className="text-blue-600 hover:underline">Politica de Privacidade</Link>.
            </p>
          </details>
        </div>
      </section>

      <section>
        <h2 className="text-xl font-semibold mb-4">Telefone</h2>
        <p className="text-gray-700">
          Atendimento telefonico: (11) XXXX-XXXX<br />
          Disponivel em dias uteis, das 9h as 17h
        </p>
      </section>
    </div>
  );
}
