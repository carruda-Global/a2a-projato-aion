public class EcoSystemAgentAction {

    public class Request {
        @InvocableVariable(label='Agente ID' description='ID do agente: spec_analyst, procurement, inventory, logistics, field_execution, bim_coordinator, nr1_psicossocial, lgpd_operacional, esg_ifrs, etc.')
        public String agentId;

        @InvocableVariable(label='Acao' description='Acao a executar: analyze, process, check, track, generate, etc.')
        public String action;

        @InvocableVariable(label='Dados' description='JSON com os dados da requisicao')
        public String data;

        @InvocableVariable(label='Plano' description='Plano de assinatura: starter, professional, enterprise, full_suite')
        public String planId;
    }

    public class Response {
        @InvocableVariable(label='Sucesso')
        public Boolean success;

        @InvocableVariable(label='Resultado')
        public String result;

        @InvocableVariable(label='Erro')
        public String error;
    }

    @InvocableMethod(
        label='Chamar Agente EcoSystem AEC'
        description='Invoca um dos 27 agentes de IA do EcoSystem AEC + Regulatory'
        category='EcoSystem AEC'
    )
    public static List<Response> callAgent(List<Request> requests) {
        List<Response> responses = new List<Response>();

        Http http = new Http();
        HttpRequest req = new HttpRequest();
        req.setEndpoint('callout:EcoSystemAEC/api/agents/execute');
        req.setMethod('POST');
        req.setHeader('Content-Type', 'application/json');

        for (Request r : requests) {
            Response resp = new Response();
            try {
                String body = JSON.serialize(new Map<String, Object>{
                    'agent_id' => r.agentId,
                    'action' => r.action,
                    'data' => r.data != null ? JSON.deserializeUntyped(r.data) : null,
                    'user_id' => UserInfo.getUserId(),
                    'plan_id' => r.planId
                });
                req.setBody(body);

                HttpResponse httpResp = http.send(req);
                if (httpResp.getStatusCode() == 200) {
                    resp.success = true;
                    resp.result = httpResp.getBody();
                } else {
                    resp.success = false;
                    resp.error = 'Erro HTTP ' + httpResp.getStatusCode() + ': ' + httpResp.getBody();
                }
            } catch (Exception e) {
                resp.success = false;
                resp.error = e.getMessage();
            }
            responses.add(resp);
        }

        return responses;
    }
}
