import {
  IExecuteFunctions,
  INodeExecutionData,
  INodeType,
  INodeTypeDescription,
  JsonObject,
  NodeApiError,
} from 'n8n-workflow';

export class AionCompliance implements INodeType {
  description: INodeTypeDescription = {
    displayName: 'AION Compliance',
    name: 'aionCompliance',
    group: ['transform'],
    icon: 'file:logo.png',
    version: 1,
    subtitle: '={{$parameter["operation"]}}',
    description: 'Run compliance checks with the AION Copilot platform',
    defaults: { name: 'AION Compliance' },
    inputs: ['main'],
    outputs: ['main'],
    credentials: [{ name: 'aionApi', required: true }],
    properties: [
      {
        displayName: 'Service',
        name: 'service',
        type: 'options',
        options: [
          { name: 'NR-1 Psychosocial Risk (Brazil)', value: 'compliance-nr1' },
          { name: 'LGPD Privacy Scan (Brazil)', value: 'compliance-lgpd' },
          { name: 'EU AI Act Readiness', value: 'compliance-eu-ai-act' },
          { name: 'CSRD Double Materiality', value: 'compliance-csrd' },
          { name: 'Carbon Inventory Scope 1+2', value: 'carbon-inventory' },
          { name: 'Vendor Risk Assessment', value: 'vendor-risk' },
          { name: 'Contract Risk Analysis', value: 'contract-risk' },
          { name: 'M&A Due Diligence', value: 'ma-due-diligence' },
        ],
        default: 'compliance-nr1',
        required: true,
        description: 'Which compliance check to run',
      },
      {
        displayName: 'Company Name',
        name: 'company',
        type: 'string',
        default: '',
        required: true,
        description: 'Company name for the check',
      },
      {
        displayName: 'Additional Parameters',
        name: 'additionalParameters',
        type: 'collection',
        placeholder: 'Add Parameter',
        default: {},
        options: [
          {
            displayName: 'Sector',
            name: 'sector',
            type: 'string',
            default: '',
            description: 'Company sector (e.g. construction, healthcare, technology)',
          },
          {
            displayName: 'AI Systems Description',
            name: 'aiSystems',
            type: 'string',
            typeOptions: { rows: 4 },
            default: '',
            description: 'Description of the AI systems in scope (required for EU AI Act)',
          },
        ],
      },
    ],
  };

  async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
    const items = this.getInputData();
    const results: INodeExecutionData[] = [];

    const credentials = await this.getCredentials('aionApi');
    const baseUrl = credentials.baseUrl as string;
    const customerEmail = credentials.customerEmail as string;

    for (let i = 0; i < items.length; i++) {
      const service = this.getNodeParameter('service', i) as string;
      const company = this.getNodeParameter('company', i) as string;
      const additional = this.getNodeParameter('additionalParameters', i, {}) as {
        sector?: string;
        aiSystems?: string;
      };

      let url = `${baseUrl}/api/agents/execute`;
      let body: Record<string, unknown> = {
        agent_id: agentForService(service),
        task_type: 'execute',
        customer_email: customerEmail,
        payload: {
          empresa: company,
          setor: additional.sector,
        },
      };

      if (service === 'compliance-eu-ai-act' && additional.aiSystems) {
        url = `${baseUrl}/api/eu-ai-act/readiness-check`;
        body = {
          empresa: company,
          ai_systems: additional.aiSystems,
        };
      }

      try {
        const response = await this.helpers.httpRequest({
          url,
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body,
        });
        results.push({ json: response });
      } catch (error) {
        if (this.continueOnFail()) {
          results.push({ json: { error: (error as Error).message, service, company } });
          continue;
        }
        throw new NodeApiError(this.getNode(), error as JsonObject);
      }
    }

    return [results];
  }
}

function agentForService(service: string): string {
  const agentMap: Record<string, string> = {
    'compliance-nr1': 'nr1_psicossocial',
    'compliance-lgpd': 'lgpd_operacional',
    'compliance-eu-ai-act': 'eu_ai_act_readiness',
    'compliance-csrd': 'csrd_reporting',
    'carbon-inventory': 'inventario_carbono',
    'vendor-risk': 'vendor_risk',
    'contract-risk': 'contract_risk',
    'ma-due-diligence': 'ma_due_diligence',
  };
  return agentMap[service] || 'compliance';
}
