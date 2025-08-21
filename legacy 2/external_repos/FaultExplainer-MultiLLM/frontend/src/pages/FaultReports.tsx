import { useStatState, useConversationState } from "../App";
import {
  ScrollArea,
  Text,
  Accordion,
  Space,
  Card,
  Image,
  SimpleGrid,
} from "@mantine/core";
import { marked } from "marked";
import { AreaChart } from "@mantine/charts";

export default function HistoryPage() {
  const conversation = useConversationState().conversation;
  const t2_stat = useStatState();
  const transformedData = t2_stat.map((item) => {
    // Cap T² values at 100 for display, but keep original for tooltip
    const cappedT2 = Math.min(item.t2_stat, 100);
    const cappedAnomaly = item.anomaly ? Math.min(item.t2_stat, 100) : 0;

    return {
      ...item,
      t2_stat: cappedT2,
      anomaly: cappedAnomaly,
      original_t2: item.t2_stat, // Keep original value for reference
    };
  });
  return (
    <ScrollArea h={`calc(100vh - 60px - 32px)`}>
      <Text
        size="xl"
        ta="center"
        dangerouslySetInnerHTML={{ __html: "T<sup>2</sup> Statistic" }}
      />

      <AreaChart
        h={300}
        data={transformedData}
        dataKey="time"
        yAxisProps={{ domain: [0, 100] }}
        yAxisLabel="T² Statistic (0-100 scale)"
        series={[
          { name: "t2_stat", label: "T² Normal", color: "green.2" },
          { name: "anomaly", label: "T² Anomaly", color: "red.4" },
        ]}
        curveType="step"
        tickLine="x"
        withDots={false}
        withGradient={false}
        fillOpacity={0.75}
        strokeWidth={0}
        withYAxis={true}
        withTooltip={true}
        tooltipProps={{
          content: ({ label, payload }) => {
            if (!payload || payload.length === 0) return null;
            const data = payload[0]?.payload;
            return (
              <div style={{
                background: 'white',
                border: '1px solid #ccc',
                borderRadius: '4px',
                padding: '8px',
                fontSize: '12px'
              }}>
                <div><strong>Time:</strong> {label}</div>
                <div><strong>T² Value:</strong> {data?.original_t2?.toFixed(2) || 'N/A'}</div>
                <div><strong>Status:</strong> {data?.anomaly > 0 ? 'Anomaly' : 'Normal'}</div>
                {data?.original_t2 > 100 && (
                  <div style={{ color: 'red', fontWeight: 'bold' }}>
                    ⚠️ Value exceeds scale (>100)
                  </div>
                )}
              </div>
            );
          }
        }}
        referenceLines={[
          { y: 30, label: "Anomaly Threshold (30)", color: "red.6" }
        ]}
      />

      <Space h="xl" />
      <Accordion variant="separated">
        {conversation.map(
          (msg) =>
            msg.explanation && (
              <Accordion.Item key={msg.id} value={`Fault ${msg.id}`}>
                <Accordion.Control>{msg.id}</Accordion.Control>
                <Accordion.Panel>
                  <Card shadow="sm" padding="lg" radius="md" withBorder>
                    {msg.images && (
                      <Card.Section>
                        <SimpleGrid cols={Math.min(msg.images.length, 3)}>
                          {(() => {
                            return msg.images.map((img, idx) => (
                              <Image
                                key={idx}
                                src={`data:image/png;base64,${img.image}`}
                                alt={`Graph for ${img.name}`}
                                radius="md"
                              />
                            ));
                          })()}
                        </SimpleGrid>
                      </Card.Section>
                    )}
                    {msg.text && (
                      <div
                        dangerouslySetInnerHTML={{
                          __html: marked.parse(msg.text),
                        }}
                      />
                    )}
                  </Card>
                </Accordion.Panel>
                {/* {idx}:{msg.explanation.toString()} */}
              </Accordion.Item>
            )
        )}
      </Accordion>
    </ScrollArea>
  );
}
