"use client"
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  type ChartOptions,
} from "chart.js"
import {
  BarChart as RechartsBarChart,
  PieChart as RechartsPieChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Bar,
  Pie,
  Cell,
  Legend as RechartsLegend,
  ResponsiveContainer,
  Area,
  AreaChart,
} from "recharts"

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend)

interface ChartData {
  name: string
  usage: number
}

const COLORS = [
  "#0088FE", // Blue
  "#00C49F", // Teal
  "#FFBB28", // Yellow
  "#FF8042", // Orange
  "#8884d8", // Purple
  "#82ca9d", // Green
  "#ffc658", // Gold
  "#8dd1e1", // Light Blue
  "#a4de6c", // Light Green
  "#d0ed57", // Lime
  "#ffc0cb", // Pink
  "#ff7f50", // Coral
]

const commonOptions: ChartOptions<"line" | "bar"> = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: "top" as const,
      labels: {
        font: {
          family: "'Inter', sans-serif",
          size: 12,
        },
        usePointStyle: true,
        padding: 20,
      },
    },
    tooltip: {
      mode: "index",
      intersect: false,
      bodyFont: {
        family: "'Inter', sans-serif",
        size: 12,
      },
      titleFont: {
        family: "'Inter', sans-serif",
        size: 14,
      },
      backgroundColor: "rgba(0, 0, 0, 0.8)",
      padding: 12,
      cornerRadius: 6,
      boxPadding: 6,
    },
  },
  scales: {
    x: {
      grid: {
        display: false,
      },
      ticks: {
        font: {
          family: "'Inter', sans-serif",
          size: 11,
        },
        color: "#6b7280",
      },
      border: {
        color: "rgba(0, 0, 0, 0.1)",
      },
    },
    y: {
      beginAtZero: true,
      grid: {
        color: "rgba(0, 0, 0, 0.05)",
      },
      ticks: {
        font: {
          family: "'Inter', sans-serif",
          size: 11,
        },
        color: "#6b7280",
        padding: 8,
      },
      border: {
        color: "rgba(0, 0, 0, 0.1)",
      },
    },
  },
  elements: {
    line: {
      tension: 0.4,
    },
    point: {
      radius: 4,
      hoverRadius: 6,
    },
  },
  interaction: {
    mode: "index",
    intersect: false,
  },
}

export function LineChart({
  data,
  xAxisLabel = "Date",
  yAxisLabel = "Usage",
  className,
}: { data: ChartData[]; xAxisLabel?: string; yAxisLabel?: string; className?: string }) {
  if (!data || data.length === 0) {
    return <div className="flex items-center justify-center h-full text-gray-400">No data available</div>
  }

  return (
    <div className={`chart-container ${className}`}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={data}
          margin={{
            top: 10,
            right: 30,
            left: 20,
            bottom: 30,
          }}
        >
          <defs>
            <linearGradient id="colorUsage" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#00B2FF" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#00B2FF" stopOpacity={0.1} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(0, 0, 0, 0.05)" />
          <XAxis
            dataKey="name"
            tick={{ fontSize: 12 }}
            tickLine={{ stroke: "rgba(0, 0, 0, 0.1)" }}
            axisLine={{ stroke: "rgba(0, 0, 0, 0.1)" }}
            label={{
              value: xAxisLabel,
              position: "insideBottom",
              offset: -10,
              style: { textAnchor: "middle", fill: "#6b7280", fontSize: 12 },
            }}
          />
          <YAxis
            tick={{ fontSize: 12 }}
            tickLine={{ stroke: "rgba(0, 0, 0, 0.1)" }}
            axisLine={{ stroke: "rgba(0, 0, 0, 0.1)" }}
            label={{
              value: yAxisLabel,
              angle: -90,
              position: "insideLeft",
              style: { textAnchor: "middle", fill: "#6b7280", fontSize: 12 },
            }}
          />
          <RechartsTooltip
            formatter={(value) => [`${value} ${yAxisLabel}`, "Usage"]}
            contentStyle={{
              backgroundColor: "rgba(255, 255, 255, 0.95)",
              border: "none",
              borderRadius: "6px",
              boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
              fontSize: "12px",
            }}
          />
          <Area
            type="monotone"
            dataKey="usage"
            stroke="#00B2FF"
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorUsage)"
            activeDot={{ r: 6, strokeWidth: 0, fill: "#00B2FF" }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

export function BarChart({ data, yAxisLabel = "kWh" }) {
  if (!data || data.length === 0) {
    return <div className="flex items-center justify-center h-full text-gray-400">No data available</div>
  }

  return (
    <div className="chart-container h-full w-full">
      <ResponsiveContainer width="100%" height="100%">
        <RechartsBarChart
          data={data}
          margin={{
            top: 20,
            right: 30,
            left: 20,
            bottom: 60,
          }}
          barSize={30}
        >
          <defs>
            <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#00B2FF" stopOpacity={1} />
              <stop offset="100%" stopColor="#0085FF" stopOpacity={0.8} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(0, 0, 0, 0.05)" />
          <XAxis
            dataKey="name"
            angle={-45}
            textAnchor="end"
            height={60}
            tick={{ fontSize: 12 }}
            tickLine={{ stroke: "rgba(0, 0, 0, 0.1)" }}
            axisLine={{ stroke: "rgba(0, 0, 0, 0.1)" }}
          />
          <YAxis
            tick={{ fontSize: 12 }}
            tickLine={{ stroke: "rgba(0, 0, 0, 0.1)" }}
            axisLine={{ stroke: "rgba(0, 0, 0, 0.1)" }}
            label={{
              value: yAxisLabel,
              angle: -90,
              position: "insideLeft",
              style: { textAnchor: "middle", fill: "#6b7280", fontSize: 12 },
            }}
          />
          <RechartsTooltip
            formatter={(value) => [`${value} ${yAxisLabel}`, "Usage"]}
            contentStyle={{
              backgroundColor: "rgba(255, 255, 255, 0.95)",
              border: "none",
              borderRadius: "6px",
              boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
              fontSize: "12px",
            }}
          />
          <Bar dataKey="usage" fill="url(#barGradient)" radius={[4, 4, 0, 0]} animationDuration={1500} />
        </RechartsBarChart>
      </ResponsiveContainer>
    </div>
  )
}

export function PieChart({ data, valueFormat = (value) => `${value} kWh` }) {
  if (!data || data.length === 0) {
    return <div className="flex items-center justify-center h-full text-gray-400">No data available</div>
  }

  return (
    <div className="chart-container h-full w-full">
      <ResponsiveContainer width="100%" height="100%">
        <RechartsPieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={true}
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            outerRadius={100}
            innerRadius={60}
            fill="#8884d8"
            dataKey="usage"
            paddingAngle={2}
            animationDuration={1500}
            animationBegin={200}
          >
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={COLORS[index % COLORS.length]}
                stroke="rgba(255, 255, 255, 0.5)"
                strokeWidth={2}
              />
            ))}
          </Pie>
          <RechartsTooltip
            formatter={(value) => [valueFormat(value), "Usage"]}
            contentStyle={{
              backgroundColor: "rgba(255, 255, 255, 0.95)",
              border: "none",
              borderRadius: "6px",
              boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
              fontSize: "12px",
            }}
          />
          <RechartsLegend
            layout="horizontal"
            verticalAlign="bottom"
            align="center"
            wrapperStyle={{ fontSize: "12px", paddingTop: "20px" }}
          />
        </RechartsPieChart>
      </ResponsiveContainer>
    </div>
  )
}

