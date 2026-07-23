const App = {
  version: require("./package.json").version,
  platformVersion: require("zapier-platform-core").version,

  // Disabled globally rather than per-trigger/search -- Zapier's platform
  // would otherwise silently strip/reshape our JSON before it reaches
  // perform(), which is exactly what made T005-style output-field
  // comparisons unpredictable for all three actions (new_call_completed,
  // new_lead_captured, find_subscription) alike.
  flags: { cleanInputData: false },

  authentication: {
    type: "custom",
    test: {
      url: "{{bundle.authData.base_url}}/api/v1/subscriptions/by-email/{{bundle.authData.customer_email}}",
      method: "GET",
    },
    connectionLabel: "{{bundle.authData.customer_email}}",
    fields: [
      {
        key: "customer_email",
        label: "Customer Email",
        type: "string",
        required: true,
        helpText: "The email address used at checkout for your AION Voice Receptionist subscription ([see plans](https://global-engenharia.com/vendas.html#plans)). Access is granted per subscription, not a static API key.",
      },
      {
        key: "base_url",
        label: "API Base URL",
        type: "string",
        required: false,
        default: "https://engenheiro-producao-ai.onrender.com",
        helpText: "AION API base URL -- almost every user should leave this at its default value. Only change it if [AION support](mailto:contato@global-engenharia.com) has explicitly given you a different one (e.g. a white-label agency deployment); this same value is exercised live by the connection test above, so an incorrect entry is caught immediately at connect time.",
      },
    ],
  },

  requestTemplate: {
    headers: {
      "Content-Type": "application/json",
    },
  },

  triggers: {
    new_call_completed: {
      key: "new_call_completed",
      noun: "Call",
      display: {
        label: "New Call Completed",
        description: "Triggers when your AI receptionist finishes a call — includes duration, outcome, and transcript.",
      },
      operation: {
        type: "hook",
        performSubscribe: async (z, bundle) => {
          const response = await z.request({
            url: `${bundle.authData.base_url}/zapier/webhook/subscribe`,
            method: "POST",
            body: {
              customer_email: bundle.authData.customer_email,
              event: "call_completed",
              target_url: bundle.targetUrl,
            },
          });
          return response.data;
        },
        performUnsubscribe: async (z, bundle) => {
          const subscriptionId = bundle.subscribeData.subscription_id;
          return z.request({
            url: `${bundle.authData.base_url}/zapier/webhook/subscribe/${subscriptionId}`,
            method: "DELETE",
          });
        },
        perform: async (z, bundle) => {
          return [bundle.cleanedRequest];
        },
        performList: async (z, bundle) => {
          const response = await z.request({
            url: `${bundle.authData.base_url}/api/voice-agent/calls/${encodeURIComponent(bundle.authData.customer_email)}`,
            method: "GET",
          });
          return (response.data.calls || []).map((c) => ({ id: c.id, ...c }));
        },
        sample: {
          id: "call_sample123",
          customer_email: "owner@example.com",
          caller_number: "+15551234567",
          direction: "inbound",
          duration_seconds: 96,
          outcome: "lead_captured",
          transcript: "Hi, thanks for calling — how can I help you today?",
          is_trial_call: false,
        },
      },
    },

    new_lead_captured: {
      key: "new_lead_captured",
      noun: "Lead",
      display: {
        label: "New Lead Captured",
        description: "Triggers when your AI receptionist captures a caller's name, number, and reason for calling.",
      },
      operation: {
        type: "hook",
        performSubscribe: async (z, bundle) => {
          const response = await z.request({
            url: `${bundle.authData.base_url}/zapier/webhook/subscribe`,
            method: "POST",
            body: {
              customer_email: bundle.authData.customer_email,
              event: "lead_captured",
              target_url: bundle.targetUrl,
            },
          });
          return response.data;
        },
        performUnsubscribe: async (z, bundle) => {
          const subscriptionId = bundle.subscribeData.subscription_id;
          return z.request({
            url: `${bundle.authData.base_url}/zapier/webhook/subscribe/${subscriptionId}`,
            method: "DELETE",
          });
        },
        perform: async (z, bundle) => {
          return [bundle.cleanedRequest];
        },
        performList: async (z, bundle) => {
          const response = await z.request({
            url: `${bundle.authData.base_url}/api/voice-agent/calls/${encodeURIComponent(bundle.authData.customer_email)}`,
            method: "GET",
          });
          return (response.data.calls || [])
            .filter((c) => c.lead_name || c.lead_phone)
            .map((c) => ({ id: c.id, ...c }));
        },
        sample: {
          id: "call_sample123",
          customer_email: "owner@example.com",
          phone_number: "+15550000000",
          caller_number: "+15559876543",
          direction: "inbound",
          duration_seconds: 87,
          outcome: "lead_captured",
          lead_name: "Jane Smith",
          lead_phone: "+15559876543",
          lead_intent: "appointment_request",
          is_trial_call: false,
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
        description: "Looks up your AION Voice Receptionist subscription details.",
      },
      operation: {
        inputFields: [
          {
            key: "email",
            type: "string",
            required: true,
            helpText: "Customer email used at checkout for the AION Voice Receptionist subscription",
          },
        ],
        perform: async (z, bundle) => {
          const url = `${bundle.authData.base_url}/api/v1/subscriptions/by-email/${encodeURIComponent(bundle.inputData.email)}`;
          const response = await z.request({ url, method: "GET" });
          return [response.data];
        },
        sample: {
          id: "cliente@exemplo.com",
          source: "stripe",
          plan_id: "voice_receptionist_starter",
          status: "active",
        },
      },
    },
  },
};

module.exports = App;
