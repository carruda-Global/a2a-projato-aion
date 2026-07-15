import { ICredentialType, INodeProperties } from 'n8n-workflow';

export class AionApi implements ICredentialType {
  name = 'aionApi';
  displayName = 'AION API';
  documentationUrl = 'https://engenheiro-producao-ai.onrender.com/docs';

  properties: INodeProperties[] = [
    {
      displayName: 'Customer Email',
      name: 'customerEmail',
      type: 'string',
      default: '',
      required: true,
      description: 'The email address used at checkout for your AION subscription. Access is granted per subscription, not a static API key.',
    },
    {
      displayName: 'Base URL',
      name: 'baseUrl',
      type: 'string',
      default: 'https://engenheiro-producao-ai.onrender.com',
      required: true,
      description: 'AION API base URL',
    },
  ];
}
