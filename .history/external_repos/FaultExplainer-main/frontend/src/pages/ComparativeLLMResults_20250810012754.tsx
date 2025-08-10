import React, { useState, useEffect } from "react";
import {
  ScrollArea,
  Text,
  Card,
  SimpleGrid,
  Badge,
  Table,
  Accordion,
  Group,
  Stack,
  Paper,
  Progress,
  Alert,
  Button,
  Switch,
} from "@mantine/core";
import { IconClock, IconRobot, IconAlertCircle, IconCheck, IconHeartbeat, IconLock, IconLockOpen } from "@tabler/icons-react";
import { marked } from "marked";

interface LLMAnalysis {
  analysis: string;
  response_time: number;
  status: string;
}

interface ComparativeResults {
  timestamp: string;
  feature_analysis: string;
  llm_analyses: Record<string, LLMAnalysis>;
  performance_summary: Record<string, { response_time: number; word_count: number }>;
}

interface ComparativeLLMResultsProps {
  results: ComparativeResults | null;
  isLoading: boolean;
}

const ModelCard: React.FC<{ modelName: string; analysis: LLMAnalysis; performance?: any }> = ({
  modelName,
  analysis,
  performance,
}) => {
  const getModelIcon = () => {
    return <IconRobot size={16} />;
  };

  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder>
      <Group justify="space-between" mb="md">
        <Group>
          {getModelIcon()}
          <Text fw={600} size="lg" tt="capitalize">
            {modelName}
          </Text>
        </Group>
        <Group>
          <Badge
            color={analysis.status === "success" ? "green" : "red"}
            variant="light"
            leftSection={analysis.status === "success" ? <IconCheck size={12} /> : <IconAlertCircle size={12} />}
          >
            {analysis.status}
          </Badge>
          {analysis.response_time > 0 && (
            <Badge color="gray" variant="light" leftSection={<IconClock size={12} />}>
              {analysis.response_time}s
            </Badge>
          )}
        </Group>
      </Group>

      {analysis.status === "success" ? (
        <div
          dangerouslySetInnerHTML={{
            __html: marked.parse(analysis.analysis),
          }}
          style={{ fontSize: "14px", lineHeight: "1.5" }}
        />
      ) : (
        <Alert color="red" icon={<IconAlertCircle size={16} />}>
          {analysis.analysis}
        </Alert>
      )}

      {performance && (
        <Paper p="xs" mt="md" bg="gray.0">
          <Group justify="space-between">
            <Text size="xs" c="dimmed">
              Words: {performance.word_count}
            </Text>
            <Text size="xs" c="dimmed">
              Speed: {(performance.word_count / performance.response_time).toFixed(1)} words/s
            </Text>
          </Group>
        </Paper>
      )}
    </Card>
  );
};

const PerformanceComparison: React.FC<{ performance: Record<string, any> }> = ({ performance }) => {
  const models = Object.keys(performance);
  const maxTime = Math.max(...models.map(m => performance[m].response_time));

  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder>
      <Text fw={600} size="lg" mb="md">
        Performance Comparison
      </Text>
      
      <Table>
        <Table.Thead>
          <Table.Tr>
            <Table.Th>Model</Table.Th>
            <Table.Th>Response Time</Table.Th>
            <Table.Th>Word Count</Table.Th>
            <Table.Th>Words/Second</Table.Th>
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {models.map((model) => {
            const perf = performance[model];
            const wordsPerSecond = (perf.word_count / perf.response_time).toFixed(1);
            const timePercentage = (perf.response_time / maxTime) * 100;
            
            return (
              <Table.Tr key={model}>
                <Table.Td>
                  <Text tt="capitalize" fw={500}>{model}</Text>
                </Table.Td>
                <Table.Td>
                  <Group>
                    <Progress value={timePercentage} size="sm" w={60} />
                    <Text size="sm">{perf.response_time}s</Text>
                  </Group>
                </Table.Td>
                <Table.Td>{perf.word_count}</Table.Td>
                <Table.Td>{wordsPerSecond}</Table.Td>
              </Table.Tr>
            );
          })}
        </Table.Tbody>
      </Table>
    </Card>
  );
};

export default function ComparativeLLMResults({ results, isLoading }: ComparativeLLMResultsProps) {
  const [lmstudioHealth, setLmstudioHealth] = useState<any>(null);
  const [checkingHealth, setCheckingHealth] = useState(false);
  const [isFrozen, setIsFrozen] = useState(false);
  const [frozenResults, setFrozenResults] = useState<ComparativeResults | null>(null);

  // Update frozen results when not frozen
  useEffect(() => {
    if (!isFrozen && results) {
      setFrozenResults(results);
    }
  }, [results, isFrozen]);

  // Use frozen results when frozen, live results when not frozen
  const displayResults = isFrozen ? frozenResults : results;

  const checkLMStudioHealth = async () => {
    setCheckingHealth(true);
    try {
      const response = await fetch("http://localhost:8000/health/lmstudio");
      const health = await response.json();
      setLmstudioHealth(health);
    } catch (error) {
      setLmstudioHealth({ status: "error", error: "Cannot connect to backend" });
    } finally {
      setCheckingHealth(false);
    }
  };

  if (isLoading && !isFrozen) {
    return (
      <ScrollArea h={`calc(100vh - 60px - 32px)`}>
        <Stack align="center" justify="center" h="50vh">
          <Text size="lg">🤖 Analyzing with multiple LLMs...</Text>
          <Progress size="lg" value={100} striped animated />
        </Stack>
      </ScrollArea>
    );
  }

  if (!displayResults) {
    return (
      <ScrollArea h={`calc(100vh - 60px - 32px)`}>
        <Stack align="center" justify="center" h="50vh">
          <Text size="lg" c="dimmed">No analysis results available</Text>
          <Text size="sm" c="dimmed">Run a fault analysis to see comparative LLM results</Text>
        </Stack>
      </ScrollArea>
    );
  }

  const models = Object.keys(displayResults.llm_analyses);

  return (
    <ScrollArea h={`calc(100vh - 60px - 32px)`}>
      <Stack gap="lg" p="md">
        {/* Header */}
        <Paper p="md" bg="blue.0">
          <Group justify="space-between">
            <Text size="xl" fw={700}>
              🔍 Multi-LLM Fault Analysis Comparison
            </Text>
            <Group>
              <Button
                size="sm"
                variant="light"
                leftSection={<IconHeartbeat size={16} />}
                onClick={checkLMStudioHealth}
                loading={checkingHealth}
              >
                Check LMStudio
              </Button>
              <Switch
                checked={isFrozen}
                onChange={(event) => setIsFrozen(event.currentTarget.checked)}
                label={isFrozen ? "🔒 Display Frozen" : "🔄 Live Updates"}
                thumbIcon={isFrozen ? <IconLock size={12} /> : <IconLockOpen size={12} />}
                color={isFrozen ? "orange" : "blue"}
                size="sm"
              />
              <Text size="sm" c="dimmed">
                {displayResults.timestamp}
              </Text>
            </Group>
          </Group>
        </Paper>

        {/* LMStudio Health Status */}
        {lmstudioHealth && (
          <Alert
            color={lmstudioHealth.status === "healthy" ? "green" : "red"}
            icon={lmstudioHealth.status === "healthy" ? <IconCheck size={16} /> : <IconAlertCircle size={16} />}
            title={`LMStudio Status: ${lmstudioHealth.status.toUpperCase()}`}
            withCloseButton
            onClose={() => setLmstudioHealth(null)}
          >
            {lmstudioHealth.status === "healthy" ? (
              <Text size="sm">
                ✅ {lmstudioHealth.models_available} models available
              </Text>
            ) : (
              <Text size="sm">
                ❌ {lmstudioHealth.error}
                <br />
                💡 Try restarting LMStudio server or run: <code>./lmstudio_quick_check.sh --fix</code>
              </Text>
            )}
          </Alert>
        )}

        {/* Feature Analysis */}
        <Accordion defaultValue="features">
          <Accordion.Item value="features">
            <Accordion.Control>
              <Text fw={600}>📊 Feature Analysis</Text>
            </Accordion.Control>
            <Accordion.Panel>
              <Paper p="md" bg="gray.0">
                <pre style={{ whiteSpace: "pre-wrap", fontSize: "14px" }}>
                  {results.feature_analysis}
                </pre>
              </Paper>
            </Accordion.Panel>
          </Accordion.Item>
        </Accordion>

        {/* Performance Comparison */}
        {Object.keys(results.performance_summary).length > 0 && (
          <PerformanceComparison performance={results.performance_summary} />
        )}

        {/* LLM Analyses */}
        <Text size="xl" fw={600} mt="lg">
          🤖 LLM Analysis Results
        </Text>
        
        <SimpleGrid cols={{ base: 1, md: 2, lg: models.length > 2 ? 3 : 2 }}>
          {models.map((modelName) => (
            <ModelCard
              key={modelName}
              modelName={modelName}
              analysis={results.llm_analyses[modelName]}
              performance={results.performance_summary[modelName]}
            />
          ))}
        </SimpleGrid>
      </Stack>
    </ScrollArea>
  );
}
