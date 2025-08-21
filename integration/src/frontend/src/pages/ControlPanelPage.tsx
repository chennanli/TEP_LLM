import { Container, Title, Text, Card, Button, Group, Alert, Slider, Stack, Badge, Grid } from "@mantine/core";
import { IconSettings, IconInfoCircle, IconRocket, IconPlayerPlay, IconPlayerStop } from "@tabler/icons-react";
import { useState, useEffect } from "react";

export default function ControlPanelPage() {
  const [simulationSpeed, setSimulationSpeed] = useState(1.0);
  const [isSimulationRunning, setIsSimulationRunning] = useState(false);
  const [systemStatus, setSystemStatus] = useState({
    backend_running: false,
    simulation_speed_factor: 1.0,
    llm_enabled: false
  });

  // Fetch system status
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch('http://localhost:8000/status');
        if (response.ok) {
          const status = await response.json();
          setSystemStatus(status);
          setSimulationSpeed(status.simulation_speed_factor || 1.0);
        }
      } catch (error) {
        console.error('Failed to fetch status:', error);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const handleSpeedChange = async (value: number) => {
    setSimulationSpeed(value);

    try {
      const response = await fetch('http://localhost:8000/api/simulation_speed', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ speed_factor: value }),
      });

      if (response.ok) {
        console.log(`Simulation speed set to ${value}x`);
      } else {
        console.error('Failed to set simulation speed');
      }
    } catch (error) {
      console.error('Error setting simulation speed:', error);
    }
  };

  const handleStartSimulation = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/simulation/start', {
        method: 'POST',
      });

      if (response.ok) {
        setIsSimulationRunning(true);
        console.log('Simulation started');
      }
    } catch (error) {
      console.error('Error starting simulation:', error);
    }
  };

  const handleStopSimulation = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/simulation/stop', {
        method: 'POST',
      });

      if (response.ok) {
        setIsSimulationRunning(false);
        console.log('Simulation stopped');
      }
    } catch (error) {
      console.error('Error stopping simulation:', error);
    }
  };

  const handleStopEverything = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/stop/all', {
        method: 'POST',
      });

      if (response.ok) {
        setIsSimulationRunning(false);
        console.log('All tasks stopped');
        alert('✅ All tasks stopped successfully!');
      } else {
        console.error('Failed to stop all tasks');
        alert('❌ Failed to stop all tasks');
      }
    } catch (error) {
      console.error('Error stopping all tasks:', error);
      alert('❌ Error stopping all tasks: ' + error);
    }
  };

  return (
    <Container size="lg" py="xl">
      <Title order={1} mb="lg">
        🎛️ TEP Control Panel
      </Title>

      <Alert
        icon={<IconInfoCircle size={16} />}
        title="Control Panel Active"
        color="green"
        mb="lg"
      >
        TEP simulation control with acceleration support and LLM analysis.
      </Alert>

      <Grid>
        <Grid.Col span={6}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Group justify="space-between" mb="xs">
              <Text fw={500}>System Status</Text>
              <IconSettings size={20} />
            </Group>

            <Stack gap="sm">
              <Group justify="space-between">
                <Text size="sm">Backend:</Text>
                <Badge color={systemStatus.backend_running ? "green" : "red"}>
                  {systemStatus.backend_running ? "Running" : "Stopped"}
                </Badge>
              </Group>

              <Group justify="space-between">
                <Text size="sm">Simulation:</Text>
                <Badge color={isSimulationRunning ? "green" : "gray"}>
                  {isSimulationRunning ? "Running" : "Stopped"}
                </Badge>
              </Group>

              <Group justify="space-between">
                <Text size="sm">LLM Analysis:</Text>
                <Badge color={systemStatus.llm_enabled ? "blue" : "gray"}>
                  {systemStatus.llm_enabled ? "Enabled" : "Disabled"}
                </Badge>
              </Group>
            </Stack>
          </Card>
        </Grid.Col>

        <Grid.Col span={6}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Group justify="space-between" mb="xs">
              <Text fw={500}>Simulation Control</Text>
              <IconPlayerPlay size={20} />
            </Group>

            <Stack gap="md">
              <Group>
                <Button
                  variant="filled"
                  color="green"
                  leftSection={<IconPlayerPlay size={16} />}
                  onClick={handleStartSimulation}
                  disabled={isSimulationRunning}
                >
                  Start Simulation
                </Button>
                <Button
                  variant="filled"
                  color="red"
                  leftSection={<IconPlayerStop size={16} />}
                  onClick={handleStopSimulation}
                  disabled={!isSimulationRunning}
                >
                  Stop Simulation
                </Button>
              </Group>
              <Group>
                <Button
                  variant="filled"
                  color="orange"
                  leftSection={<IconPlayerStop size={16} />}
                  onClick={handleStopEverything}
                  size="lg"
                  style={{ width: '100%' }}
                >
                  🛑 Stop Everything
                </Button>
              </Group>
            </Stack>
          </Card>
        </Grid.Col>
      </Grid>

      <Card shadow="sm" padding="lg" radius="md" withBorder mt="lg">
        <Group justify="space-between" mb="md">
          <Text fw={500}>🚀 Simulation Acceleration</Text>
          <Badge variant="light" color="blue">
            {simulationSpeed.toFixed(1)}x Speed
          </Badge>
        </Group>

        <Text size="sm" c="dimmed" mb="md">
          Control the simulation speed factor. Higher values make the TEP simulation run faster while maintaining physics accuracy.
        </Text>

        <Slider
          value={simulationSpeed}
          onChange={setSimulationSpeed}
          onChangeEnd={handleSpeedChange}
          min={1}
          max={10}
          step={0.5}
          marks={[
            { value: 1, label: '1x' },
            { value: 2.5, label: '2.5x' },
            { value: 5, label: '5x' },
            { value: 7.5, label: '7.5x' },
            { value: 10, label: '10x' },
          ]}
          mb="md"
        />

        <Text size="xs" c="dimmed">
          💡 Recommended: 1x-2x for production, 5x-10x for testing and development
        </Text>
      </Card>

      <Text size="sm" c="dimmed" mt="md">
        💡 Tip: Monitor the "Plot" tab for real-time data and "Comparative" tab for LLM analysis results.
      </Text>
    </Container>
  );
}
