import { Box, Button, ContextView, Divider, Badge, Inline, Link, List, ListItem, Spinner, Text, Banner } from "@stripe/ui-extension-sdk/ui";
import type { ExtensionContextValue } from "@stripe/ui-extension-sdk/context";
import { useEffect, useState } from "react";

const API_URL = "https://engenheiro-producao-ai.onrender.com";

interface ComplianceScore {
  score: number;
  nivel: string;
  obrigacoes: { nome: string; status: string; prazo?: string; multa?: string }[];
  plano_recomendado: string;
  link_ativacao: string;
}

const EcosystemApp = ({ userContext }: ExtensionContextValue) => {
  const [score, setScore] = useState<ComplianceScore | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchComplianceScore();
  }, []);

  const fetchComplianceScore = async () => {
    try {
      const response = await fetch(`${API_URL}/api/stripe/compliance-score`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ stripe_account_id: userContext?.account?.id, email: userContext?.account?.email }),
      });
      const data = await response.json();
      setScore(data);
    } catch {
      setError("Não foi possível carregar o score.");
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (s: number) => (s >= 80 ? "success" : s >= 50 ? "warning" : "critical");

  if (loading) return (
    <ContextView title="EcoSystem Compliance">
      <Box css={{ stack: "x", gap: "medium", alignY: "center" }}>
        <Spinner />
        <Text>Analisando compliance da sua empresa...</Text>
      </Box>
    </ContextView>
  );

  if (error) return (
    <ContextView title="EcoSystem Compliance">
      <Banner type="critical" title="Erro" description={error} />
    </ContextView>
  );

  return (
    <ContextView title="EcoSystem Compliance" description="Score de compliance regulatório da sua empresa">
      <Box css={{ padding: "large", background: "container", borderRadius: "medium", marginBottom: "medium" }}>
        <Text size="small" color="secondary">Score de Compliance</Text>
        <Box css={{ stack: "x", alignY: "center", gap: "small", marginTop: "small" }}>
          <Text size="xxlarge" weight="bold" color={getScoreColor(score?.score || 0)}>{score?.score || 0}</Text>
          <Text size="xlarge" color="secondary">/100</Text>
          <Badge type={getScoreColor(score?.score || 0) as any}>{score?.nivel}</Badge>
        </Box>
      </Box>
      <Divider />
      <Box css={{ marginTop: "medium", marginBottom: "medium" }}>
        <Text weight="semibold" size="small">Obrigações Regulatórias</Text>
        <List>
          {score?.obrigacoes.map((ob, i) => (
            <ListItem key={i} title={ob.nome} value={<Badge type={ob.status === "ok" ? "success" : "critical"}>{ob.status === "ok" ? "Em dia" : "Crítico"}</Badge>} />
          ))}
        </List>
      </Box>
      <Divider />
      {score?.score && score.score < 100 && (
        <Box css={{ marginTop: "medium" }}>
          <Banner type="warning" title={`Plano recomendado: ${score.plano_recomendado}`} description="Regularize sua empresa em 48h com nossos agentes de IA" />
          <Box css={{ marginTop: "small" }}>
            <Button type="primary" href={score.link_ativacao} target="_blank">Ativar agentes de compliance →</Button>
          </Box>
        </Box>
      )}
      <Box css={{ marginTop: "medium" }}>
        <Text size="xsmall" color="secondary">Powered by EcoSystem AI — Global Match Engenharia</Text>
      </Box>
    </ContextView>
  );
};

export default EcosystemApp;
