"use client"

import React from "react";
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
} from "chart.js"
import './charts.css'; // Import the CSS file

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Title, Tooltip, Legend)

export function LineChart({ className }: { className?: string }) {
  const data = {
    labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    datasets: [
      {
        data: [12, 19, 15, 17, 22, 28, 25],
        borderColor: "#00B2FF",
        backgroundColor: "rgba(0, 178, 255, 0.1)",
        tension: 0.4,
        fill: true,
      },
    ],
  }

  return (
    <div className={`${className} chart-containerC chart-lineC`}>
      <Line
        data={data}
        options={{
          responsive: true,
          plugins: {
            legend: {
              display: false,
            },
          },
        }}
      />
    </div>
  )
}

export function BarChart({ className }: { className?: string }) {
  const data = {
    labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    datasets: [
      {
        data: [15, 30, 25, 18, 12, 25, 28],
        backgroundColor: "#00B2FF",
      },
    ],
  }

  return (
    <div className={`${className} chart-containerC chart-barC`}>
      <Bar
        data={data}
        options={{
          responsive: true,
          plugins: {
            legend: {
              display: false,
            },
          },
        }}
      />
    </div>
  )
}

export function PieChart({ className }: { className?: string }) {
  const data = {
    labels: ["Heating", "Cooling", "Lighting", "Appliances", "Other"],
    datasets: [
      {
        data: [30, 25, 20, 15, 10],
        backgroundColor: ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"],
      },
    ],
  }

  return (
    <div className={`${className} chart-containerC chart-pieC`}>
      <Pie
        data={data}
        options={{
          responsive: true,
          plugins: {
            legend: {
              position: "bottom" as const,
            },
          },
        }}
      />
    </div>
  )
}
