import { useEffect } from 'react';

export default function Privacy() {
  useEffect(() => { document.title = 'Politica de Privacidade | EcoSystem AEC'; }, []);
  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold mb-8">Politica de Privacidade</h1>
      <p className="text-gray-600 mb-6">Ultima atualizacao: 25 de junho de 2026</p>

      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-4">1. Dados que coletamos</h2>
        <p className="text-gray-700 mb-4">
          A EcoSystem AEC (Projato Engenharia) coleta os seguintes dados pessoais
          dos usuarios da plataforma:
        </p>
        <ul className="list-disc pl-6 text-gray-700 space-y-2">
          <li>Nome completo, CPF, email e telefone</li>
          <li>Dados profissionais (cargo, empresa, CREA quando aplicavel)</li>
          <li>Dados de faturamento e pagamento processados via Stripe</li>
          <li>Documentos tecnicos enviados para analise pelos agentes de IA</li>
          <li>Logs de uso da plataforma (metricas de performance, erros)</li>
        </ul>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-4">2. Base legal</h2>
        <p className="text-gray-700">
          Tratamos seus dados com base na Lei Geral de Protecao de Dados
          (Lei 13.709/2018), especificamente nas seguintes hipoteses:
          consentimento do titular, execucao de contrato, obrigacao legal
          e legítimo interesse.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-4">3. Compartilhamento de dados</h2>
        <p className="text-gray-700 mb-4">
          Compartilhamos dados apenas com:
        </p>
        <ul className="list-disc pl-6 text-gray-700 space-y-2">
          <li><strong>Stripe</strong>: processamento de pagamentos</li>
          <li><strong>DeepSeek / Google Gemini</strong>: processamento de IA (dados anonimizados)</li>
          <li><strong>Supabase</strong>: armazenamento de dados</li>
          <li><strong>Microsoft Azure / Salesforce</strong>: quando voce assina via marketplace</li>
        </ul>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-4">4. Seus direitos LGPD</h2>
        <p className="text-gray-700 mb-4">
          Conforme a LGPD, voce tem direito a:
        </p>
        <ul className="list-disc pl-6 text-gray-700 space-y-2">
          <li>Confirmacao da existencia de tratamento de dados</li>
          <li>Acesso aos dados</li>
          <li>Correcao de dados incompletos ou desatualizados</li>
          <li>Anonimizacao, bloqueio ou eliminacao de dados desnecessarios</li>
          <li>Portabilidade dos dados</li>
          <li>Eliminacao dos dados tratados com consentimento</li>
        </ul>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-4">5. Contato do DPO</h2>
        <p className="text-gray-700">
          Para exercer seus direitos ou esclarecer duvidas, entre em contato
          com nosso DPO:<br />
          Email: <a href="mailto:privacidade@ecosystemaec.com.br" className="text-blue-600 hover:underline">privacidade@ecosystemaec.com.br</a><br />
          Endereco: Rua ..., Sao Paulo - SP<br />
          Prazo de resposta: ate 15 dias uteis (conforme art. 19 da LGPD)
        </p>
      </section>
    </div>
  );
}
