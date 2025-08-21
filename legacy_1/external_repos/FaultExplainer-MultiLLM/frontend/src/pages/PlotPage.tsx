import {
  useDataPoints,
  columnFilter,
  DataPointsId,
  startTime,
  columnFilterUnits,
} from "../App";
import { ScrollArea, SimpleGrid } from "@mantine/core";
import { AreaChart } from "@mantine/charts";

// TEP Realistic Operating Ranges (based on actual simulation data analysis)
const TEP_RANGES: Record<string, { min: number; max: number; unit: string; critical: boolean }> = {
  // XMEAS (Measurement) Variables - Realistic Safe Operating Ranges
  "A Feed": { min: 0.15, max: 0.35, unit: "kscmh", critical: false },
  "D Feed": { min: 3500, max: 3800, unit: "kg/h", critical: false },
  "E Feed": { min: 4300, max: 4700, unit: "kg/h", critical: false },
  "A and C Feed": { min: 8.5, max: 10.0, unit: "kscmh", critical: false },
  "Recycle Flow": { min: 25, max: 29, unit: "kscmh", critical: false },
  "Reactor Feed Rate": { min: 40, max: 45, unit: "kscmh", critical: false },
  "Reactor Pressure": { min: 2650, max: 2750, unit: "kPa", critical: true },
  "Reactor Level": { min: 70, max: 80, unit: "%", critical: true },
  "Reactor Temperature": { min: 120.2, max: 120.6, unit: "°C", critical: true },
  "Purge Rate": { min: 0.30, max: 0.40, unit: "kscmh", critical: false },
  "Product Sep Temp": { min: 75, max: 85, unit: "°C", critical: false },
  "Product Sep Level": { min: 45, max: 55, unit: "%", critical: true },
  "Product Sep Pressure": { min: 2600, max: 2700, unit: "kPa", critical: false },
  "Product Sep Underflow": { min: 20, max: 30, unit: "m³/h", critical: false },
  "Stripper Level": { min: 45, max: 55, unit: "%", critical: false },
  "Stripper Pressure": { min: 3000, max: 3200, unit: "kPa", critical: false },
  "Stripper Underflow": { min: 20, max: 26, unit: "m³/h", critical: false },
  "Stripper Temp": { min: 60, max: 70, unit: "°C", critical: false },
  "Stripper Steam Flow": { min: 220, max: 250, unit: "kg/h", critical: false },
  "Compressor Work": { min: 330, max: 350, unit: "kW", critical: false },
  "Reactor Coolant Temp": { min: 90, max: 100, unit: "°C", critical: false },
  "Separator Coolant Temp": { min: 75, max: 85, unit: "°C", critical: false },

  // XMV (Input/Manipulated) Variables - Control Valve Positions (%)
  "D feed load": { min: 50, max: 70, unit: "%", critical: false },
  "E feed load": { min: 45, max: 65, unit: "%", critical: false },
  "A feed load": { min: 15, max: 35, unit: "%", critical: false },
  "A and C feed load": { min: 50, max: 70, unit: "%", critical: false },
  "Compressor recycle valve": { min: 15, max: 35, unit: "%", critical: true },
  "Purge valve": { min: 35, max: 55, unit: "%", critical: false },
  "Separator liquid load": { min: 30, max: 50, unit: "%", critical: true },
  "Stripper liquid load": { min: 35, max: 55, unit: "%", critical: true },
  "Stripper steam valve": { min: 40, max: 60, unit: "%", critical: false },
  "Reactor coolant load": { min: 35, max: 55, unit: "%", critical: true },
  "Condenser coolant load": { min: 30, max: 50, unit: "%", critical: false },
};

export default function DataPage() {
  const fullDataPoints = useDataPoints();
  const dataPoints = Object.keys(fullDataPoints)
    .filter((key) => columnFilter.includes(key))
    .reduce((obj: DataPointsId, key) => {
      obj[key] = fullDataPoints[key];
      return obj;
    }, {});

  if (!dataPoints) {
    return <div>Loading...</div>;
  }

  // Sort variables by range span (largest ranges first) for better visibility
  const sortedDataPoints = Object.entries(dataPoints).sort(([fieldNameA], [fieldNameB]) => {
    const rangeA = TEP_RANGES[fieldNameA];
    const rangeB = TEP_RANGES[fieldNameB];

    // Variables with ranges come first, sorted by range span (descending)
    if (rangeA && rangeB) {
      const spanA = rangeA.max - rangeA.min;
      const spanB = rangeB.max - rangeB.min;
      return spanB - spanA; // Larger spans first
    }

    // Variables with ranges come before those without
    if (rangeA && !rangeB) return -1;
    if (!rangeA && rangeB) return 1;

    // For variables without ranges, sort alphabetically
    return fieldNameA.localeCompare(fieldNameB);
  });

  return (
    <ScrollArea h={`calc(100vh - 60px - 32px)`}>
      <SimpleGrid type="container" cols={3}>
        {sortedDataPoints.map(([fieldName, values]) => {
          // console.log(values);
          const timeAxis = fullDataPoints.time.map((item) => {
            const date = new Date(
              startTime.getTime() + (item * 3 * 60000) / 0.05
            );
            return date.getHours() + ":" + date.getMinutes();
          });

          // Get operating range for this parameter
          const range = TEP_RANGES[fieldName];
          const chartData = values.map((item, idx) => ({
            data: item,
            time: timeAxis[idx],
            // Add reference lines if range exists
            ...(range && {
              min_range: range.min,
              max_range: range.max,
            }),
          }));

          // Build series array with reference lines
          const series = [{ name: "data", color: "indigo.6" }];
          if (range) {
            series.push(
              { name: "min_range", color: range.critical ? "red.4" : "orange.4", strokeDasharray: "5 5" },
              { name: "max_range", color: range.critical ? "red.4" : "orange.4", strokeDasharray: "5 5" }
            );
          }

          // Calculate smart Y-axis domain for better visibility
          const dataMin = Math.min(...values);
          const dataMax = Math.max(...values);
          let yAxisDomain: [number, number] | undefined = undefined;

          if (range) {
            // Expand domain to show range lines with some padding
            const rangeSpan = range.max - range.min;
            const padding = rangeSpan * 0.5; // 50% padding for better visibility
            const domainMin = Math.min(dataMin, range.min) - padding;
            const domainMax = Math.max(dataMax, range.max) + padding;
            yAxisDomain = [domainMin, domainMax];
          }

          return (
            <div key={fieldName} style={{ textAlign: "center" }}>
              <h4>
                {fieldName}
                {range && (
                  <span style={{ fontSize: "12px", color: range.critical ? "#e03131" : "#fd7e14", marginLeft: "8px" }}>
                    [{range.min}-{range.max} {range.unit}]
                    {range.critical && " 🚨"}
                  </span>
                )}
              </h4>
              <AreaChart
                h={300}
                key={fieldName}
                data={chartData}
                dataKey="time"
                yAxisLabel={columnFilterUnits[fieldName]}
                yAxisProps={yAxisDomain ? { domain: yAxisDomain } : undefined}
                series={series}
                curveType="step"
                tickLine="x"
                withTooltip={true}
                withDots={false}
                referenceLines={range ? [
                  { y: range.min, label: `Min: ${range.min}`, color: range.critical ? "red.4" : "orange.4" },
                  { y: range.max, label: `Max: ${range.max}`, color: range.critical ? "red.4" : "orange.4" }
                ] : undefined}
              />
            </div>
          );
        })}
      </SimpleGrid>
    </ScrollArea>
  );
}

// import { useDataPoints, columnFilter, DataPointsId, startTime } from "../App";
// import { Line } from "react-chartjs-2";
// import {
//   Chart as ChartJS,
//   CategoryScale,
//   LinearScale,
//   PointElement,
//   LineElement,
//   Title,
//   Tooltip,
//   Legend,
//   Filler,
//   TimeScale,
//   ChartOptions,
// } from "chart.js";
// import "chartjs-adapter-date-fns";
// import { ScrollArea, SimpleGrid } from "@mantine/core";

// ChartJS.register(
//   CategoryScale,
//   LinearScale,
//   PointElement,
//   LineElement,
//   Title,
//   Tooltip,
//   Legend,
//   Filler,
//   TimeScale
// );

// export default function DataPage() {
//   const fullDataPoints = useDataPoints();
//   const dataPoints = Object.keys(fullDataPoints)
//     .filter((key) => columnFilter.includes(key))
//     .reduce((obj: DataPointsId, key) => {
//       obj[key] = fullDataPoints[key];
//       return obj;
//     }, {});

//   if (!dataPoints) {
//     return <div>Loading...</div>;
//   }

//   return (
//     <ScrollArea h={`calc(100vh - 60px - 32px)`}>
//       <SimpleGrid cols={3}>
//         {Object.entries(dataPoints).map(([fieldName, values]) => (
//           <div
//             className="chart-wrapper"
//             key={fieldName}
//             style={{
//               background: "#f0f0f0",
//               padding: "0px",
//               borderRadius: "5px",
//               height: "220px",
//             }}
//           >
//             <LineChart
//               data={values}
//               fieldName={fieldName}
//               labels={fullDataPoints["time"]}
//             />
//           </div>
//         ))}
//       </SimpleGrid>
//     </ScrollArea>
//   );
// }

// const LineChart = ({
//   data,
//   fieldName,
//   labels,
// }: {
//   data: number[];
//   fieldName: string;
//   labels: number[];
// }) => {
//   const chartData = {
//     labels: labels.map((interval) => {
//       const currentTime = new Date(startTime);
//       currentTime.setMinutes(currentTime.getMinutes() + interval * 20 * 3);
//       return currentTime.toISOString();
//     }),
//     datasets: [
//       {
//         label: "",
//         data: data,
//         fill: true,
//         borderColor: "rgb(75, 192, 192)",
//         stepped: true,
//         pointRadius: 0.5,
//         borderWidth: 1,
//         pointHoverRadius: 0,
//       },
//     ],
//   };

//   const chartOptions: ChartOptions<"line"> = {
//     responsive: true,
//     animation: {
//       duration: 0.25,
//     },
//     scales: {
//       x: {
//         type: "time",
//         time: {
//           // unit: "minute",
//           tooltipFormat: "PPpp", // Tooltip format for time
//           displayFormats: {
//             minute: "HH:mm", // Display format for the x-axis labels
//           },
//         },
//         title: {
//           display: true,
//           text: "Time",
//         },
//       },
//       y: {
//         title: {
//           display: false,
//           text: "Values",
//         },
//       },
//     },
//     plugins: {
//       legend: {
//         display: false,
//       },
//       title: {
//         display: true,
//         text: fieldName,
//       },
//     },
//   };

//   return (
//     <Line style={{ height: "100%" }} data={chartData} options={chartOptions} />
//   );
// };
