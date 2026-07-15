import { useEffect } from 'react';

export default function Terms() {
  useEffect(() => { document.title = 'Termos de Uso | EcoSystem AEC'; }, []);
  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold mb-8">Termos de Uso</h1>
      <p className="text-gray-600 mb-6">Ultima atualizacao: 25 de junho de 2026</p>

      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-4">1. Aceitacao dos termos</h2>
        <p className="text-gray-700">
          Ao usar a plataforma EcoSystem AEC + Regulatory, voce concorda
          com estes Termos de Uso. Se nao concordar, nao utilize a plataforma.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-4">2. Descricao do servico</h2>
        <p className="text-gray-700">
          O EcoSystem AEC + Regulatory e uma plataforma SaaS que oferece
          30 agentes de IA para automacao de processos de engenharia,
          arquitetura, construcao e conformidade regulatoria brasileira.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-4">3. Planos e assinatura</h2>
        <ul className="list-disc pl-6 text-gray-700 space-y-2">
          <li>O servico e oferecido em regime de assinatura mensal</li>
          <li>O cancelamento pode ser feito a qualquer momento via painel ou suporte</li>
          <li>Periodo de trial: 15 dias para todos os planos</li>
          <li>Pagamentos processados via Stripe ou marketplaces parceiros</li>
        </ul>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-4">4. Uso aceitavel</h2>
        <ul className="list-disc pl-6 text-gray-700 space-y-2">
          <li>O usuario e responsavel pela precisao dos dados inseridos</li>
          <li>Nao e permitido usar a plataforma para atividades ilicitas</li>
          <li>O usuario nao deve compartilhar credenciais de acesso</li>
          <li>Os agentes de IA fornecem recomendacoes - decisoes finais sao do usuario</li>
        </ul>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-4">5. Propriedade intelectual</h2>
        <p className="text-gray-700">
          O software, a arquitetura dos agentes e os prompts de IA sao
          propriedade intelectual da Projato Engenharia. Os documentos e
          dados enviados pelo usuario permanecem propriedade do usuario.
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-4">6. Limitacao de responsabilidade</h2>
        <p className="text-gray-700">
          A Projato Engenharia nao se responsabiliza por decisoes tecnicas
          ou regulatorias tomadas com base nas recomendacoes dos agentes
          de IA. Recomenda-se sempre a revisao por profissional habilitado
          (engenheiro, advogado, contador).
        </p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-4">7. Suporte</h2>
        <p className="text-gray-700">
          Oferecemos suporte por email: <a href="mailto:suporte@ecosystemaec.com.br" className="text-blue-600 hover:underline">suporte@ecosystemaec.com.br</a><br />
          Horario de atendimento: dias uteis, das 9h as 18h (horario de Brasilia)<br />
          Tempo de resposta: ate 24h uteis para tickets L1
        </p>
      </section>
    </div>
  );
}
