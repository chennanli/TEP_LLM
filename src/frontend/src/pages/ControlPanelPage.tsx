import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  Text,
  Button,
  Group,
  Stack,
  Badge,
  Slider,
  Select,
  Alert,
  Progress,
  ActionIcon,
  Notification,
  Paper,
  Title,
  Divider,
  Switch,
  NumberInput,
} from '@mantine/core';
import {
  IconPlay,
  IconPlayerStop,
  IconSettings,
  IconAlertTriangle,
  IconCheck,
  IconRefresh,
  IconActivity,
} from '@tabler/icons-react';

interface SimulationConfig {
  duration: number;
  preset: 'demo' | 'balanced' | 'realistic';
  faults: Record<string, { start_time: number; magnitude: number }>;
}

interface SimulationStatus {
  status: 'stopped' | 'running' | 'error';
  current_step: number;
  total_steps: number;
  anomaly_score: number;
  is_anomaly: boolean;
  data?: any;
}

export default function ControlPanelPage() {
  const [simulationStatus, setSimulationStatus] = useState<SimulationStatus>({
    status: 'stopped',
    current_step: 0,
    total_steps: 0,
    anomaly_score: 0,
    is_anomaly: false,
  });

  const [config, setConfig] = useState<SimulationConfig>({
    duration: 1000,
    preset: 'demo',
    faults: {},
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Fault injection controls
  const [faultControls, setFaultControls] = useState({
    idv1: { enabled: false, start_time: 100, magnitude: 0.5 },
    idv2: { enabled: false, start_time: 200, magnitude: 0.7 },
    idv3: { enabled: false, start_time: 150, magnitude: 0.6 },
    idv4: { enabled: false, start_time: 300, magnitude: 0.8 },
  });

  // WebSocket connection for real-time updates
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/realtime');
    
    ws.onopen = () => {
      console.log('WebSocket connected');
    };
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      
      if (data.type === 'simulation_data' && data.data) {
        setSimulationStatus(prev => ({
          ...prev,
          ...data.data.simulation_state,
          data: data.data.data,
        }));
      }
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
    
    return () => {
      ws.close();
    };
  }, []);

  // Fetch simulation status
  const fetchStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/simulation/status');
      if (response.ok) {
        const data = await response.json();
        setSimulationStatus(data.simulation_state || data);
      }
    } catch (err) {
      console.error('Error fetching status:', err);
    }
  };

  // Start simulation
  const startSimulation = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Prepare fault configuration
      const activeFaults: Record<string, any> = {};
      Object.entries(faultControls).forEach(([faultId, fault]) => {
        if (fault.enabled) {
          activeFaults[faultId] = {
            start_time: fault.start_time,
            magnitude: fault.magnitude,
          };
        }
      });

      const simulationConfig = {
        ...config,
        faults: activeFaults,
      };

      const response = await fetch('http://localhost:8000/api/v1/simulation/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(simulationConfig),
      });

      if (response.ok) {
        const result = await response.json();
        setSuccess('Simulation started successfully!');
        fetchStatus();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to start simulation');
      }
    } catch (err) {
      setError('Network error: Could not connect to simulation service');
    } finally {
      setLoading(false);
    }
  };

  // Stop simulation
  const stopSimulation = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/simulation/stop', {
        method: 'POST',
      });

      if (response.ok) {
        setSuccess('Simulation stopped successfully!');
        fetchStatus();
      } else {
        setError('Failed to stop simulation');
      }
    } catch (err) {
      setError('Network error: Could not connect to simulation service');
    } finally {
      setLoading(false);
    }
  };

  // Update fault control
  const updateFaultControl = (faultId: string, field: string, value: any) => {
    setFaultControls(prev => ({
      ...prev,
      [faultId]: {
        ...prev[faultId as keyof typeof prev],
        [field]: value,
      },
    }));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'green';
      case 'stopped': return 'gray';
      case 'error': return 'red';
      default: return 'gray';
    }
  };

  const progress = simulationStatus.total_steps > 0 
    ? (simulationStatus.current_step / simulationStatus.total_steps) * 100 
    : 0;

  return (
    <Stack gap="md" p="md">
      <Title order={2}>🎛️ TEP Control Panel</Title>
      
      {/* Status Alerts */}
      {error && (
        <Alert icon={<IconAlertTriangle size="1rem" />} color="red" onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert icon={<IconCheck size="1rem" />} color="green" onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      <Grid>
        {/* Simulation Control */}
        <Grid.Col span={6}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Group justify="space-between" mb="xs">
              <Text fw={500}>Simulation Control</Text>
              <Badge color={getStatusColor(simulationStatus.status)} variant="light">
                {simulationStatus.status.toUpperCase()}
              </Badge>
            </Group>

            <Stack gap="md">
              <Group>
                <Button
                  leftSection={<IconPlay size="1rem" />}
                  onClick={startSimulation}
                  loading={loading}
                  disabled={simulationStatus.status === 'running'}
                  color="green"
                >
                  Start Simulation
                </Button>
                
                <Button
                  leftSection={<IconPlayerStop size="1rem" />}
                  onClick={stopSimulation}
                  loading={loading}
                  disabled={simulationStatus.status !== 'running'}
                  color="red"
                >
                  Stop Simulation
                </Button>
                
                <ActionIcon onClick={fetchStatus} variant="light">
                  <IconRefresh size="1rem" />
                </ActionIcon>
              </Group>

              {simulationStatus.status === 'running' && (
                <>
                  <Text size="sm">
                    Step: {simulationStatus.current_step} / {simulationStatus.total_steps}
                  </Text>
                  <Progress value={progress} size="lg" />
                </>
              )}
            </Stack>
          </Card>
        </Grid.Col>

        {/* Anomaly Status */}
        <Grid.Col span={6}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Group justify="space-between" mb="xs">
              <Text fw={500}>Anomaly Detection</Text>
              <Badge 
                color={simulationStatus.is_anomaly ? 'red' : 'green'} 
                variant="light"
                leftSection={<IconActivity size="0.8rem" />}
              >
                {simulationStatus.is_anomaly ? 'ANOMALY' : 'NORMAL'}
              </Badge>
            </Group>

            <Stack gap="sm">
              <Text size="sm">
                Anomaly Score: <strong>{simulationStatus.anomaly_score.toFixed(2)}</strong>
              </Text>
              <Progress 
                value={Math.min(simulationStatus.anomaly_score * 50, 100)} 
                color={simulationStatus.is_anomaly ? 'red' : 'blue'}
                size="md"
              />
              {simulationStatus.is_anomaly && (
                <Alert color="red" size="sm">
                  Anomaly detected! Consider triggering LLM analysis.
                </Alert>
              )}
            </Stack>
          </Card>
        </Grid.Col>

        {/* Configuration */}
        <Grid.Col span={12}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Text fw={500} mb="md">Simulation Configuration</Text>
            
            <Grid>
              <Grid.Col span={4}>
                <NumberInput
                  label="Duration (steps)"
                  value={config.duration}
                  onChange={(value) => setConfig(prev => ({ ...prev, duration: Number(value) }))}
                  min={100}
                  max={5000}
                  step={100}
                />
              </Grid.Col>
              
              <Grid.Col span={4}>
                <Select
                  label="Preset Mode"
                  value={config.preset}
                  onChange={(value) => setConfig(prev => ({ ...prev, preset: value as any }))}
                  data={[
                    { value: 'demo', label: 'Demo (4s intervals)' },
                    { value: 'balanced', label: 'Balanced (60s intervals)' },
                    { value: 'realistic', label: 'Realistic (180s intervals)' },
                  ]}
                />
              </Grid.Col>
            </Grid>
          </Card>
        </Grid.Col>

        {/* Fault Injection */}
        <Grid.Col span={12}>
          <Card shadow="sm" padding="lg" radius="md" withBorder>
            <Text fw={500} mb="md">Fault Injection Controls</Text>
            
            <Grid>
              {Object.entries(faultControls).map(([faultId, fault]) => (
                <Grid.Col span={6} key={faultId}>
                  <Paper p="md" withBorder>
                    <Group justify="space-between" mb="sm">
                      <Text fw={500}>{faultId.toUpperCase()}</Text>
                      <Switch
                        checked={fault.enabled}
                        onChange={(event) => 
                          updateFaultControl(faultId, 'enabled', event.currentTarget.checked)
                        }
                      />
                    </Group>
                    
                    {fault.enabled && (
                      <Stack gap="xs">
                        <Text size="sm">Start Time: {fault.start_time}</Text>
                        <Slider
                          value={fault.start_time}
                          onChange={(value) => updateFaultControl(faultId, 'start_time', value)}
                          min={0}
                          max={config.duration}
                          step={10}
                          size="sm"
                        />
                        
                        <Text size="sm">Magnitude: {fault.magnitude}</Text>
                        <Slider
                          value={fault.magnitude}
                          onChange={(value) => updateFaultControl(faultId, 'magnitude', value)}
                          min={0}
                          max={1}
                          step={0.1}
                          size="sm"
                        />
                      </Stack>
                    )}
                  </Paper>
                </Grid.Col>
              ))}
            </Grid>
          </Card>
        </Grid.Col>
      </Grid>
    </Stack>
  );
}
