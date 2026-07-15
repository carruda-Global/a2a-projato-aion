global class EcoSystemMCPTools {

    @InvocableMethod(
        label='EcoSystem - Analisar Especificacoes'
        description='Agente Spec Analyst - Analisa especificacoes tecnicas'
        category='EcoSystem AEC'
    )
    global static List<MCPResponse> analyzeSpecs(List<MCPRequest> requests) {
        return callAgent('spec_analyst', 'analyze', requests);
    }

    @InvocableMethod(
        label='EcoSystem - Processar Compras'
        description='Agente Procurement - Processa pedidos de compra'
        category='EcoSystem AEC'
    )
    global static List<MCPResponse> processProcurement(List<MCPRequest> requests) {
        return callAgent('procurement', 'process', requests);
    }

    @InvocableMethod(
        label='EcoSystem - Consultar Estoque'
        description='Agente Inventory - Verifica disponibilidade em estoque'
        category='EcoSystem AEC'
    )
    global static List<MCPResponse> checkInventory(List<MCPRequest> requests) {
        return callAgent('inventory', 'check', requests);
    }

    @InvocableMethod(
        label='EcoSystem - Rastrear Logistica'
        description='Agente Logistics - Rastreia entregas e fretes'
        category='EcoSystem AEC'
    )
    global static List<MCPResponse> trackLogistics(List<MCPRequest> requests) {
        return callAgent('logistics', 'track', requests);
    }

    @InvocableMethod(
        label='EcoSystem - Instrucoes de Campo'
        description='Agente Field Execution - Gera instrucoes BIM/RA para obras'
        category='EcoSystem AEC'
    )
    global static List<MCPResponse> fieldInstructions(List<MCPRequest> requests) {
        return callAgent('field_execution', 'generate', requests);
    }

    @InvocableMethod(
        label='EcoSystem - NR-1 Psicossocial'
        description='Agente NR-1 - Inventario de riscos psicossociais'
        category='EcoSystem Regulatory'
    )
    global static List<MCPResponse> nr1Psychosocial(List<MCPRequest> requests) {
        return callAgent('nr1_psicossocial', 'analyze', requests);
    }

    @InvocableMethod(
        label='EcoSystem - LGPD Operacional'
        description='Agente LGPD - Mapeamento de dados e conformidade ANPD'
        category='EcoSystem Regulatory'
    )
    global static List<MCPResponse> lgpdCompliance(List<MCPRequest> requests) {
        return callAgent('lgpd_operacional', 'analyze', requests);
    }

    @InvocableMethod(
        label='EcoSystem - ESG IFRS'
        description='Agente ESG - Relatorios IFRS S1/S2'
        category='EcoSystem Regulatory'
    )
    global static List<MCPResponse> esgReport(List<MCPRequest> requests) {
        return callAgent('esg_ifrs', 'report', requests);
    }

    global class MCPRequest {
        @InvocableVariable(label='Dados' description='JSON com dados de entrada')
        global String data;
    }

    global class MCPResponse {
        @InvocableVariable(label='Sucesso')
        global Boolean success;
        @InvocableVariable(label='Resultado')
        global String result;
        @InvocableVariable(label='Erro')
        global String error;
    }

    private static List<MCPResponse> callAgent(String agentId, String action, List<MCPRequest> requests) {
        List<MCPResponse> responses = new List<MCPResponse>();
        Http http = new Http();
        HttpRequest req = new HttpRequest();
        req.setEndpoint('callout:EcoSystemAEC/api/agents/execute');
        req.setMethod('POST');
        req.setHeader('Content-Type', 'application/json');

        for (MCPRequest r : requests) {
            MCPResponse resp = new MCPResponse();
            try {
                Map<String, Object> body = new Map<String, Object>();
                body.put('agent_id', agentId);
                body.put('action', action);
                body.put('data', r.data != null ? JSON.deserializeUntyped(r.data) : null);
                body.put('user_id', UserInfo.getUserId());
                req.setBody(JSON.serialize(body));

                HttpResponse httpResp = http.send(req);
                if (httpResp.getStatusCode() == 200) {
                    resp.success = true;
                    resp.result = httpResp.getBody();
                } else {
                    resp.success = false;
                    resp.error = 'Erro ' + httpResp.getStatusCode() + ': ' + httpResp.getBody();
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
