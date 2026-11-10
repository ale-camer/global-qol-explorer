<template>
  <div class="table-panel">
    <div class="panel-header">
      <div class="d-flex align-items-center gap-2">
        <h5 class="panel-title m-0">{{ $t('data_table') }}</h5>
        <span class="count-badge">{{ tableData.length }}</span>
      </div>
      <div class="d-flex align-items-center gap-2">
        <button
          class="icon-action-btn"
          @click="emit('download-csv')"
          title="Download as CSV"
        >
          <i class="bi bi-download"></i>
        </button>
        <button
          class="icon-action-btn"
          @click="emit('update:isTableCollapsed', !isTableCollapsed)"
          title="Toggle table visibility"
        >
          <i :class="isTableCollapsed ? 'bi bi-chevron-down' : 'bi bi-chevron-up'"></i>
        </button>
      </div>
    </div>

    <div v-if="!isTableCollapsed" class="table-container">
      <table class="modern-table">
        <thead>
          <tr>
            <th
              class="text-start sortable"
              @click="emit('set-sort', 'country')"
              title="Sort by Country"
            >
              <span>{{ $t('country_header') }}</span>
              <i
                v-if="sortColumn === 'country'"
                :class="['bi', sortDirection === 'asc' ? 'bi-arrow-up-short' : 'bi-arrow-down-short']"
              ></i>
            </th>
            <th
              class="text-end sortable"
              @click="emit('set-sort', 'value')"
              title="Sort by Value"
            >
              <span>{{ $t('data_header') }}</span>
              <i
                v-if="sortColumn === 'value'"
                :class="['bi', sortDirection === 'asc' ? 'bi-arrow-up-short' : 'bi-arrow-down-short']"
              ></i>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in tableData" :key="row.iso_a3">
            <td class="country-cell">{{ row.name }}</td>
            <td class="value-cell text-end">{{ formatValue(row.value) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
defineProps({
  tableData: { type: Array, required: true },
  isTableCollapsed: { type: Boolean, default: false },
  sortColumn: { type: String, required: true },
  sortDirection: { type: String, required: true }
})

const emit = defineEmits(['update:isTableCollapsed', 'set-sort', 'download-csv'])

const formatValue = (val) =>
  val == null
    ? 'N/A'
    : parseFloat(val).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })
</script>
