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

// Xianxia color palette
const XIANXIA_COLORS = [
  '#10B981', '#F59E0B', '#A78BFA', '#F87171', '#38BDF8',
  '#FB923C', '#34D399', '#C084FC', '#FBBF24', '#60A5FA',
  '#E879F9', '#2DD4BF', '#F472B6', '#818CF8', '#FCA5A1',
]

const JADE_GRADIENT = (ctx) => {
  if (!ctx?.chart?.ctx) return '#10B981'
  const gradient = ctx.chart.ctx.createLinearGradient(0, 0, 0, ctx.chart.height || 300)
  gradient.addColorStop(0, 'rgba(16, 185, 129, 0.4)')
  gradient.addColorStop(1, 'rgba(16, 185, 129, 0.02)')
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
    const gridColor = 'rgba(30, 41, 59, 0.8)'
    const tickColor = '#94A3B8'

    // ─── DOUGHNUT ─────────────────────
    const doughnutData = computed(() => {
      const d = props.chartData
      return {
        labels: d.labels || [],
        datasets: [{
          data: d.values || [],
          backgroundColor: XIANXIA_COLORS.slice(0, (d.values || []).length),
          borderColor: '#0B1120',
          borderWidth: 2,
          hoverBorderColor: '#10B981',
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
          color: '#F59E0B',
          font: { ...baseFont, size: 15, weight: 'bold', family: "'Noto Serif TC', serif" },
          padding: { bottom: 20 },
        },
        tooltip: {
          backgroundColor: 'rgba(17, 27, 46, 0.95)',
          titleColor: '#E2E8F0',
          bodyColor: '#94A3B8',
          borderColor: 'rgba(5, 150, 105, 0.3)',
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
            backgroundColor: 'rgba(16, 185, 129, 0.7)',
            borderColor: '#10B981',
            borderWidth: 1,
            borderRadius: 6,
            borderSkipped: false,
          },
          {
            label: '🔥 Chi tiêu',
            data: d.expense || [],
            backgroundColor: 'rgba(248, 113, 113, 0.7)',
            borderColor: '#F87171',
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
          color: '#F59E0B',
          font: { ...baseFont, size: 15, weight: 'bold', family: "'Noto Serif TC', serif" },
          padding: { bottom: 16 },
        },
        tooltip: {
          backgroundColor: 'rgba(17, 27, 46, 0.95)',
          titleColor: '#E2E8F0',
          bodyColor: '#94A3B8',
          borderColor: 'rgba(5, 150, 105, 0.3)',
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
            borderColor: '#F87171',
            backgroundColor: (ctx) => {
              if (!ctx?.chart?.ctx) return 'rgba(248, 113, 113, 0.1)'
              const gradient = ctx.chart.ctx.createLinearGradient(0, 0, 0, ctx.chart.height || 300)
              gradient.addColorStop(0, 'rgba(248, 113, 113, 0.3)')
              gradient.addColorStop(1, 'rgba(248, 113, 113, 0.02)')
              return gradient
            },
            fill: true,
            tension: 0.4,
            pointBackgroundColor: '#F87171',
            pointBorderColor: '#0B1120',
            pointBorderWidth: 2,
            pointRadius: 5,
            pointHoverRadius: 8,
          },
          {
            label: '💎 Thu nhập',
            data: d.income || [],
            borderColor: '#10B981',
            backgroundColor: JADE_GRADIENT,
            fill: true,
            tension: 0.4,
            pointBackgroundColor: '#10B981',
            pointBorderColor: '#0B1120',
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
          color: '#F59E0B',
          font: { ...baseFont, size: 15, weight: 'bold', family: "'Noto Serif TC', serif" },
          padding: { bottom: 16 },
        },
        tooltip: {
          backgroundColor: 'rgba(17, 27, 46, 0.95)',
          titleColor: '#E2E8F0',
          bodyColor: '#94A3B8',
          borderColor: 'rgba(5, 150, 105, 0.3)',
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
