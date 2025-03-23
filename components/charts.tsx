"use client"

import { Line, Bar, Pie } from "react-chartjs-2"
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

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend)

interface ChartData {
  name: string
  usage: number
}

const chartColors = [
  "rgba(0, 178, 255, 0.8)", // Blue
  "rgba(255, 149, 0, 0.8)", // Orange
  "rgba(0, 178, 255, 0.6)", // Light Blue
  "rgba(255, 149, 0, 0.6)", // Light Orange
  "rgba(0, 178, 255, 0.4)", // Lighter Blue
  "rgba(255, 149, 0, 0.4)", // Lighter Orange
  "rgba(0, 133, 255, 0.8)", // Darker Blue
  "rgba(255, 120, 0, 0.8)", // Darker Orange
  "rgba(0, 133, 255, 0.6)", // Darker Light Blue
  "rgba(255, 120, 0, 0.6)", // Darker Light Orange
]

const commonOptions: ChartOptions<"line" | "bar"> = {
  responsive: true,
  plugins: {
    legend: {
      position: "top" as const,
      labels: {
        font: {
          family: "'Inter', sans-serif",
        },
      },
    },
    tooltip: {
      mode: "index",
      intersect: false,
      bodyFont: {
        family: "'Inter', sans-serif",
      },
      titleFont: {
        family: "'Inter', sans-serif",
      },
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
        },
      },
    },
    y: {
      beginAtZero: true,
      grid: {
        color: "rgba(0, 0, 0, 0.1)",
      },
      ticks: {
        font: {
          family: "'Inter', sans-serif",
        },
      },
    },
  },
}

interface LineChartProps {
  data: ChartData[];
  xAxisLabel?: string;
  yAxisLabel?: string;
  className?: string;
  valueFormat?: (value: number) => string;
}

export function LineChart({
  data,
  xAxisLabel = "Date",
  yAxisLabel = "Usage",
  className,
  valueFormat
}: LineChartProps) {
  const chartData = {
    labels: data.map((d) => d.name),
    datasets: [
      {
        label: yAxisLabel || "Usage",
        data: data.map((d) => d.usage),
        borderColor: "rgba(0, 178, 255, 1)",
        backgroundColor: "rgba(0, 178, 255, 0.2)",
        tension: 0.4,
        fill: true,
      },
    ],
  }

  const options: ChartOptions<"line"> = {
    ...commonOptions,
    plugins: {
      ...commonOptions.plugins,
      title: {
        display: true,
        text: "Usage Over Time",
      },
      tooltip: {
        ...commonOptions.plugins?.tooltip,
        callbacks: {
          label: function(context) {
            let label = context.dataset.label || '';
            if (label) {
              label += ': ';
            }
            if (context.parsed.y !== null) {
              label += valueFormat 
                ? valueFormat(context.parsed.y) 
                : `${context.parsed.y}`;
            }
            return label;
          }
        }
      }
    },
    scales: {
      ...commonOptions.scales,
      x: {
        ...commonOptions.scales?.x,
        title: {
          display: true,
          text: xAxisLabel,
        },
      },
      y: {
        ...commonOptions.scales?.y,
        title: {
          display: true,
          text: yAxisLabel,
        },
      },
    },
  }

  return (
    <div className={`chart-container ${className}`}>
      <Line data={chartData} options={options} />
    </div>
  )
}

interface BarChartProps {
  data: ChartData[];
  yAxisLabel?: string;
  className?: string;
  valueFormat?: (value: number) => string;
}

export function BarChart({ data, yAxisLabel = "Energy (kWh)", className, valueFormat }: BarChartProps) {
  const chartData = {
    labels: data.map((d) => d.name),
    datasets: [
      {
        label: yAxisLabel,
        data: data.map((d) => d.usage),
        backgroundColor: data.map((_, i) => chartColors[i % chartColors.length]),
      },
    ],
  }

  const options: ChartOptions<"bar"> = {
    ...commonOptions,
    plugins: {
      ...commonOptions.plugins,
      title: {
        display: true,
        text: "Energy Usage",
        color: "rgba(0, 178, 255, 1)",
      },
      tooltip: {
        ...commonOptions.plugins?.tooltip,
        callbacks: {
          label: function(context) {
            let label = context.dataset.label || '';
            if (label) {
              label += ': ';
            }
            if (context.parsed.y !== null) {
              label += valueFormat 
                ? valueFormat(context.parsed.y) 
                : `${context.parsed.y}`;
            }
            return label;
          }
        }
      }
    },
    scales: {
      ...commonOptions.scales,
      y: {
        ...commonOptions.scales?.y,
        title: {
          display: true,
          text: yAxisLabel,
        },
      },
    },
  }

  return (
    <div className={`chart-container ${className}`}>
      <Bar data={chartData} options={options} />
    </div>
  )
}

interface PieChartProps {
  data: ChartData[];
  className?: string;
  valueFormat?: (value: number) => string;
}

export function PieChart({ data, valueFormat, className }: PieChartProps) {
  const chartData = {
    labels: data.map((d) => d.name),
    datasets: [
      {
        data: data.map((d) => d.usage),
        backgroundColor: data.map((_, i) => chartColors[i % chartColors.length]),
        borderColor: data.map((_, i) => chartColors[i % chartColors.length].replace(/[^,]+(?=\))/, "1")),
        borderWidth: 1,
      },
    ],
  }

  const options: ChartOptions<"pie"> = {
    responsive: true,
    plugins: {
      legend: {
        position: "right" as const,
        labels: {
          color: "rgba(0, 178, 255, 1)",
          font: {
            family: "'Inter', sans-serif",
          },
        },
      },
      title: {
        display: true,
        text: "Energy Usage Distribution",
        color: "rgba(0, 178, 255, 1)",
        font: {
          family: "'Inter', sans-serif",
        },
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            let label = context.label || '';
            if (label) {
              label += ': ';
            }
            if (context.parsed !== null) {
              label += valueFormat 
                ? valueFormat(context.parsed as number) 
                : `${context.parsed} kWh`;
            }
            return label;
          }
        }
      }
    },
  }

  return (
    <div className={`chart-container ${className}`}>
      <Pie data={chartData} options={options} />
    </div>
  )
}

