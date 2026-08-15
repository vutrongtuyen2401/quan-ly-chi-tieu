<template>
  <!-- ═══════════════════════════════════════════════════════ -->
  <!-- CÀN KHÔN LINH THẠCH CÁC — CHART COMPONENTS            -->
  <!-- ═══════════════════════════════════════════════════════ -->

  <!-- DOUGHNUT CHART — Phân bổ chi tiêu -->
  <div v-if="type === 'doughnut'" class="chart-wrapper">
    <Doughnut :data="doughnutData" :options="doughnutOptions" />
  </div>

  <!-- BAR CHART — Xu hướng thu/chi -->
  <div v-else-if="type === 'bar'" class="chart-wrapper">
    <Bar :data="barData" :options="barOptions" />
  </div>

  <!-- LINE CHART — Chi tiêu theo tuần -->
  <div v-else-if="type === 'line'" class="chart-wrapper">
    <Line :data="lineData" :options="lineOptions" />
  </div>
</template>

<script>
import { computed } from 'vue'
import { Doughnut, Bar, Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  ArcElement, BarElement, LineElement, PointElement,
  CategoryScale, LinearScale,
  Title, Tooltip, Legend, Filler
} from 'chart.js'

ChartJS.register(
  ArcElement, BarElement, LineElement, PointElement,
  CategoryScale, LinearScale,
  Title, Tooltip, Legend, Filler
)

// Xianxia color palette (light theme)
const XIANXIA_COLORS = [
  '#4fa8a0', '#e8c874', '#8b5cf6', '#ef4444', '#3b82f6',
  '#f97316', '#10b981', '#ec4899', '#f59e0b', '#06b6d4',
  '#a855f7', '#14b8a6', '#f43f5e', '#6366f1', '#fb923c',
]

const JADE_GRADIENT = (ctx) => {
  if (!ctx?.chart?.ctx) return '#4fa8a0'
  const gradient = ctx.chart.ctx.createLinearGradient(0, 0, 0, ctx.chart.height || 300)
  gradient.addColorStop(0, 'rgba(79, 168, 160, 0.4)')
  gradient.addColorStop(1, 'rgba(79, 168, 160, 0.02)')
  return gradient
}

export default {
  name: 'ChartComponent',
  components: { Doughnut, Bar, Line },
  props: {
    type: { type: String, required: true }, // 'doughnut', 'bar', 'line'
    chartData: { type: Object, default: () => ({}) },
    title: { type: String, default: '' },
  },
  setup(props) {
    // ─── Common Options ───────────────
    const baseFont = {
      family: "'Inter', sans-serif",
      size: 12,
    }
    const gridColor = 'rgba(71, 101, 130, 0.18)'
    const tickColor = '#2c3e50'

    // ─── DOUGHNUT ─────────────────────
    const doughnutData = computed(() => {
      const d = props.chartData
      return {
        labels: d.labels || [],
        datasets: [{
          data: d.values || [],
          backgroundColor: XIANXIA_COLORS.slice(0, (d.values || []).length),
          borderColor: '#ffffff',
          borderWidth: 2,
          hoverBorderColor: '#e8c874',
          hoverBorderWidth: 3,
          hoverOffset: 8,
        }]
      }
    })

    const doughnutOptions = computed(() => ({
      responsive: true,
      maintainAspectRatio: false,
      cutout: '65%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: tickColor,
            font: baseFont,
            padding: 16,
            usePointStyle: true,
            pointStyleWidth: 12,
          }
        },
        title: {
          display: !!props.title,
          text: props.title,
          color: '#b38217',
          font: { ...baseFont, size: 15, weight: 'bold', family: "'Lora', 'Cormorant Garamond', serif" },
          padding: { bottom: 20 },
        },
        tooltip: {
          backgroundColor: 'rgba(255, 255, 255, 0.96)',
          titleColor: '#1a3a5c',
          bodyColor: '#2c3e50',
          borderColor: 'rgba(232, 200, 116, 0.6)',
          borderWidth: 1,
          cornerRadius: 8,
          padding: 12,
          callbacks: {
            label: (ctx) => {
              const val = ctx.parsed || 0
              const total = ctx.dataset.data.reduce((a, b) => a + b, 0)
              const pct = total > 0 ? ((val / total) * 100).toFixed(1) : 0
              return ` ${ctx.label}: ${val.toLocaleString('vi-VN')} ₫ (${pct}%)`
            }
          }
        }
      }
    }))

    // ─── BAR ──────────────────────────
    const barData = computed(() => {
      const d = props.chartData
      return {
        labels: d.labels || [],
        datasets: [
          {
            label: '💎 Thu nhập',
            data: d.income || [],
            backgroundColor: 'rgba(79, 168, 160, 0.8)',
            borderColor: '#4fa8a0',
            borderWidth: 1,
            borderRadius: 6,
            borderSkipped: false,
          },
          {
            label: '🔥 Chi tiêu',
            data: d.expense || [],
            backgroundColor: 'rgba(224, 102, 102, 0.8)',
            borderColor: '#e06666',
            borderWidth: 1,
            borderRadius: 6,
            borderSkipped: false,
          },
        ]
      }
    })

    const barOptions = computed(() => ({
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            color: tickColor,
            font: baseFont,
            padding: 20,
            usePointStyle: true,
          }
        },
        title: {
          display: !!props.title,
          text: props.title,
          color: '#b38217',
          font: { ...baseFont, size: 15, weight: 'bold', family: "'Lora', 'Cormorant Garamond', serif" },
          padding: { bottom: 16 },
        },
        tooltip: {
          backgroundColor: 'rgba(255, 255, 255, 0.96)',
          titleColor: '#1a3a5c',
          bodyColor: '#2c3e50',
          borderColor: 'rgba(232, 200, 116, 0.6)',
          borderWidth: 1,
          cornerRadius: 8,
          padding: 12,
          callbacks: {
            label: (ctx) => ` ${ctx.dataset.label}: ${ctx.parsed.y.toLocaleString('vi-VN')} ₫`
          }
        }
      },
      scales: {
        x: {
          grid: { color: gridColor, drawBorder: false },
          ticks: { color: tickColor, font: baseFont },
        },
        y: {
          grid: { color: gridColor, drawBorder: false },
          ticks: {
            color: tickColor,
            font: baseFont,
            callback: (val) => (val / 1000000).toFixed(1) + 'M',
          },
          beginAtZero: true,
        }
      }
    }))

    // ─── LINE ─────────────────────────
    const lineData = computed(() => {
      const d = props.chartData
      return {
        labels: d.labels || [],
        datasets: [
          {
            label: '🔥 Chi tiêu',
            data: d.expense || [],
            borderColor: '#e06666',
            backgroundColor: (ctx) => {
              if (!ctx?.chart?.ctx) return 'rgba(224, 102, 102, 0.1)'
              const gradient = ctx.chart.ctx.createLinearGradient(0, 0, 0, ctx.chart.height || 300)
              gradient.addColorStop(0, 'rgba(224, 102, 102, 0.3)')
              gradient.addColorStop(1, 'rgba(224, 102, 102, 0.02)')
              return gradient
            },
            fill: true,
            tension: 0.4,
            pointBackgroundColor: '#e06666',
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2,
            pointRadius: 5,
            pointHoverRadius: 8,
          },
          {
            label: '💎 Thu nhập',
            data: d.income || [],
            borderColor: '#4fa8a0',
            backgroundColor: JADE_GRADIENT,
            fill: true,
            tension: 0.4,
            pointBackgroundColor: '#4fa8a0',
            pointBorderColor: '#ffffff',
            pointBorderWidth: 2,
            pointRadius: 5,
            pointHoverRadius: 8,
          },
        ]
      }
    })

    const lineOptions = computed(() => ({
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false,
      },
      plugins: {
        legend: {
          position: 'top',
          labels: {
            color: tickColor,
            font: baseFont,
            padding: 20,
            usePointStyle: true,
          }
        },
        title: {
          display: !!props.title,
          text: props.title,
          color: '#b38217',
          font: { ...baseFont, size: 15, weight: 'bold', family: "'Lora', 'Cormorant Garamond', serif" },
          padding: { bottom: 16 },
        },
        tooltip: {
          backgroundColor: 'rgba(255, 255, 255, 0.96)',
          titleColor: '#1a3a5c',
          bodyColor: '#2c3e50',
          borderColor: 'rgba(232, 200, 116, 0.6)',
          borderWidth: 1,
          cornerRadius: 8,
          padding: 12,
          callbacks: {
            label: (ctx) => ` ${ctx.dataset.label}: ${ctx.parsed.y.toLocaleString('vi-VN')} ₫`
          }
        }
      },
      scales: {
        x: {
          grid: { color: gridColor, drawBorder: false },
          ticks: { color: tickColor, font: baseFont },
        },
        y: {
          grid: { color: gridColor, drawBorder: false },
          ticks: {
            color: tickColor,
            font: baseFont,
            callback: (val) => (val / 1000000).toFixed(1) + 'M',
          },
          beginAtZero: true,
        }
      }
    }))

    return {
      doughnutData, doughnutOptions,
      barData, barOptions,
      lineData, lineOptions,
    }
  }
}
</script>

<style scoped>
.chart-wrapper {
  position: relative;
  width: 100%;
  min-height: 300px;
  max-height: 400px;
}
</style>
