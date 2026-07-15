const App = {
  version: require("./package.json").version,
  platformVersion: require("zapier-platform-core").version,

  authentication: {
    type: "custom",
    test: {
      url: "{{bundle.authData.base_url}}/api/v1/subscriptions/by-email/{{bundle.authData.customer_email}}",
      method: "GET",
    },
    fields: [
      {
        key: "customer_email",
        label: "Customer Email",
        type: "string",
        required: true,
        helpText: "The email address used at checkout for your AION subscription. Access is granted per subscription, not a static API key.",
      },
      {
        key: "base_url",
        label: "API Base URL",
        type: "string",
        required: false,
        default: "https://engenheiro-producao-ai.onrender.com",
        helpText: "AION API base URL",
      },
    ],
  },

  requestTemplate: {
    headers: {
      "Content-Type": "application/json",
    },
  },

  creates: {
    run_eu_ai_act_check: {
      key: "run_eu_ai_act_check",
      noun: "EU AI Act Check",
      display: {
        label: "Run EU AI Act Readiness Check",
        description: "Classifica sistemas de IA conforme EU AI Act.",
      },
      operation: {
        inputFields: [
          { key: "company", label: "Company Name", type: "string", required: true },
          { key: "ai_systems", label: "AI Systems Description", type: "text", required: true },
        ],
        perform: async (z, bundle) => {
          const url = `${bundle.authData.base_url}/api/eu-ai-act/readiness-check`;
          const response = await z.request({
            url,
            method: "POST",
            body: {
              company: bundle.inputData.company,
              ai_use: bundle.inputData.ai_systems,
              sells_to_eu: "yes",
            },
          });
          return response.data;
        },
        sample: {
          status: "completed",
          risk_classification: "high-risk",
          risk_score: 0.72,
          summary: "Sistema classificado como alto risco (Article 6, Annex III)",
        },
      },
    },
  },

  searches: {
    find_subscription: {
      key: "find_subscription",
      noun: "Subscription",
      display: {
        label: "Find Subscription",
        description: "Busca detalhes de uma assinatura AION.",
      },
      operation: {
        inputFields: [
          {
            key: "email",
            type: "string",
            required: true,
            helpText: "Customer email used at checkout for the AION subscription",
          },
        ],
        perform: async (z, bundle) => {
          const url = `${bundle.authData.base_url}/api/v1/subscriptions/by-email/${encodeURIComponent(bundle.inputData.email)}`;
          const response = await z.request({
            url,
            method: "GET",
          });
          return [response.data];
        },
        sample: {
          id: "cliente@exemplo.com",
          source: "stripe",
          plan_id: "compliance_essencial",
          status: "active",
        },
      },
    },
  },
};

module.exports = App;
