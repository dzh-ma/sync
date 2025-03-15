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

export function LineChart({
  data,
  xAxisLabel = "Date",
  yAxisLabel = "Usage",
  className,
}: { data: ChartData[]; xAxisLabel?: string; yAxisLabel?: string; className?: string }) {
  const chartData = {
    labels: data.map((d) => d.name),
    datasets: [
      {
        label: "Usage",
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

export function BarChart({ data, className }: { data: ChartData[]; className?: string }) {
  const chartData = {
    labels: data.map((d) => d.name),
    datasets: [
      {
        label: "Usage",
        data: data.map((d) => d.usage),
        backgroundColor: chartColors,
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
    },
    scales: {
      ...commonOptions.scales,
      y: {
        ...commonOptions.scales?.y,
        title: {
          display: true,
          text: "Energy (kWh)",
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

export function PieChart({ data, className }: { data: ChartData[]; className?: string }) {
  const chartData = {
    labels: data.map((d) => d.name),
    datasets: [
      {
        data: data.map((d) => d.usage),
        backgroundColor: chartColors,
        borderColor: chartColors.map((color) => color.replace("0.8", "1")),
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
    },
  }

  return (
    <div className={`chart-container ${className}`}>
      <Pie data={chartData} options={options} />
    </div>
  )
}

