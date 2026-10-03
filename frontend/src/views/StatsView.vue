<template>
  <!-- ═══════ TAB 7: STATISTICS ═══════ -->
  <section class="tab-panel">
    <div class="tab-header" style="display:flex; justify-content: space-between; align-items:center; flex-wrap: wrap; gap: 10px; margin-bottom: 15px;">
      <h2 class="section-title" style="margin:0;">📈 Thiên Cơ Thống Kê — Phân Tích Nâng Cao</h2>
      <div class="export-actions" style="display:flex; gap:10px; align-items: center; flex-wrap: wrap;">
        <div class="stats-datepicker-wrapper" style="width: 280px; max-width: 100%;">
          <VueDatePicker
            v-model="statsDateRange"
            range
            :preset-ranges="presetRanges"
            format="dd/MM/yyyy"
            :enable-time-picker="false"
            :auto-apply="true"
            :locale="viLocale"
            :format-locale="viLocale"
            :select-text="'Áp dụng'"
            :cancel-text="'Hủy'"
            :now-button-label="'Hôm nay'"
            :action-row="{ selectBtnLabel: 'Áp dụng', cancelBtnLabel: 'Hủy', nowBtnLabel: 'Hôm nay' }"
            placeholder="Chọn khoảng thời gian"
            @update:model-value="onStatsDateChange"
            :dark="currentTheme === 'xianxia'"
          />
        </div>
        <button class="btn-jade-sm" @click="doExport('csv')">CSV</button>
        <button class="btn-jade-sm" @click="doExport('excel')">Excel</button>
      </div>
    </div>

    <!-- Trend Chart -->
    <div class="stats-chart-card" v-if="hasTrendData">
      <ChartComponent
        type="bar"
        :chart-data="trendBarData"
        :title="`📊 Xu Hướng Thu/Chi ${trendData.months || 6} Tháng`"
      />
    </div>

    <!-- Weekly Chart -->
    <div class="stats-chart-card" v-if="hasWeeklyData">
      <ChartComponent
        type="line"
        :chart-data="weeklyLineData"
        :title="`📉 Chi Tiêu Theo Tuần (${weeklyData.weeks || 4} Tuần Gần Đây)`"
      />
    </div>

    <!-- Doughnut -->
    <div class="stats-chart-card" v-if="summary.expense_by_category && summary.expense_by_category.length">
      <ChartComponent
        type="doughnut"
        :chart-data="statsDoughnutData"
        title="🥧 Tỷ Trọng Chi Tiêu Theo Danh Mục"
      />
    </div>

    <!-- Month Comparison -->
    <div class="compare-section">
      <h3 class="sub-title">🔀 So Sánh Chi Tiêu Hai Tháng</h3>
      <div class="compare-controls">
        <div class="input-group-xianxia">
          <label>Tháng 1</label>
          <input v-model="compareMonth1" type="month" @change="loadCompare" />
        </div>
        <span class="compare-vs">VS</span>
        <div class="input-group-xianxia">
          <label>Tháng 2</label>
          <input v-model="compareMonth2" type="month" @change="loadCompare" />
        </div>
      </div>
      <div v-if="compareData" class="compare-grid">
        <div class="compare-card">
          <h4>📅 {{ compareData.month1.month }}</h4>
          <div class="compare-stat">
            <span>Thu: <strong class="positive">{{ formatVND(compareData.month1.income) }}</strong></span>
            <span>Chi: <strong class="negative">{{ formatVND(compareData.month1.expense) }}</strong></span>
            <span>Tiết kiệm: <strong :class="compareData.month1.savings >= 0 ? 'positive' : 'negative'">{{ formatVND(compareData.month1.savings) }}</strong></span>
          </div>
        </div>
        <div class="compare-delta">
          <div class="delta-item" :class="compareData.delta_income >= 0 ? 'delta-up' : 'delta-down'">
            <span class="delta-arrow">{{ compareData.delta_income >= 0 ? '▲' : '▼' }}</span>
            <span>Thu: {{ formatVND(Math.abs(compareData.delta_income)) }}</span>
          </div>
          <div class="delta-item" :class="compareData.delta_expense <= 0 ? 'delta-up' : 'delta-down'">
            <span class="delta-arrow">{{ compareData.delta_expense >= 0 ? '▲' : '▼' }}</span>
            <span>Chi: {{ formatVND(Math.abs(compareData.delta_expense)) }}</span>
          </div>
          <div class="delta-item" :class="compareData.delta_savings >= 0 ? 'delta-up' : 'delta-down'">
            <span class="delta-arrow">{{ compareData.delta_savings >= 0 ? '▲' : '▼' }}</span>
            <span>Tiết kiệm: {{ formatVND(Math.abs(compareData.delta_savings)) }}</span>
          </div>
        </div>
        <div class="compare-card">
          <h4>📅 {{ compareData.month2.month }}</h4>
          <div class="compare-stat">
            <span>Thu: <strong class="positive">{{ formatVND(compareData.month2.income) }}</strong></span>
            <span>Chi: <strong class="negative">{{ formatVND(compareData.month2.expense) }}</strong></span>
            <span>Tiết kiệm: <strong :class="compareData.month2.savings >= 0 ? 'positive' : 'negative'">{{ formatVND(compareData.month2.savings) }}</strong></span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!hasTrendData && !hasWeeklyData" class="empty-state">
      Chưa có đủ dữ liệu để hiển thị thống kê. Hãy thêm giao dịch!
    </div>
  </section>
</template>

<script>
import { onMounted } from 'vue'
import { useAppStore } from '../stores/app'
import { useAppBindings } from '../composables/useAppBindings'
import ChartComponent from '../components/ChartComponents.vue'
import { VueDatePicker } from '@vuepic/vue-datepicker'

export default {
  name: 'StatsView',
  components: { ChartComponent, VueDatePicker },
  setup() {
    const store = useAppStore()
    onMounted(() => {
      store.onStatsDateChange()
      store.loadCompare()
    })
    return useAppBindings()
  },
}
</script>
