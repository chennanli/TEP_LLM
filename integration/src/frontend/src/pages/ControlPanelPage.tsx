import { Container, Title, Text, Card, Button, Group, Alert } from "@mantine/core";
import { IconSettings, IconInfoCircle } from "@tabler/icons-react";

export default function ControlPanelPage() {
  return (
    <Container size="lg" py="xl">
      <Title order={1} mb="lg">
        🎛️ Control Panel
      </Title>
      
      <Alert 
        icon={<IconInfoCircle size={16} />} 
        title="Control Panel - Coming Soon" 
        color="blue"
        mb="lg"
      >
        The control panel functionality is currently being integrated. 
        For now, you can use the other tabs to monitor the TEP system.
      </Alert>

      <Card shadow="sm" padding="lg" radius="md" withBorder>
        <Group justify="space-between" mb="xs">
          <Text fw={500}>TEP System Control</Text>
          <IconSettings size={20} />
        </Group>

        <Text size="sm" c="dimmed" mb="md">
          Control panel for Tennessee Eastman Process simulation and fault injection.
        </Text>

        <Group>
          <Button variant="light" disabled>
            Start Simulation
          </Button>
          <Button variant="light" disabled>
            Inject Fault
          </Button>
          <Button variant="light" disabled>
            Reset System
          </Button>
        </Group>
      </Card>

      <Text size="sm" c="dimmed" mt="md">
        💡 Tip: Use the "Plot" tab to view real-time monitoring data and the "Comparative" tab for LLM analysis results.
      </Text>
    </Container>
  );
}
