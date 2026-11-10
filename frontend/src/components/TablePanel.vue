<template>
  <div class="table-panel d-flex flex-column p-0">
    <div class="panel-header d-flex justify-content-between align-items-center p-3">
      <h5 class="m-0 text-dark fw-light">{{ $t('data_table') }}</h5>
      <div>
        <button
          class="btn btn-sm btn-success py-0 px-2 me-2"
          @click="emit('download-csv')"
          title="Download as CSV"
        >
          <i class="bi bi-download"></i>
        </button>
        <button
          class="btn btn-sm btn-warning py-0 px-2"
          @click="emit('update:isTableCollapsed', !isTableCollapsed)"
          title="Toggle table visibility"
        >
          <i :class="isTableCollapsed ? 'bi bi-arrows-expand' : 'bi bi-arrows-collapse'"></i>
        </button>
      </div>
    </div>

    <div v-if="!isTableCollapsed" class="table-container w-100 overflow-y-auto px-3 pb-3">
      <table class="table table-borderless">
        <thead class="text-white">
          <tr>
            <th
              class="text-start sortable"
              @click="emit('set-sort', 'country')"
              title="Sort by Country"
            >
              {{ $t('country_header') }}
              <i
                v-if="sortColumn === 'country'"
                :class="['bi', sortDirection === 'asc' ? 'bi-arrow-up' : 'bi-arrow-down']"
              ></i>
            </th>
            <th
              class="text-end sortable"
              @click="emit('set-sort', 'value')"
              title="Sort by Value"
            >
              {{ $t('data_header') }}
              <i
                v-if="sortColumn === 'value'"
                :class="['bi', sortDirection === 'asc' ? 'bi-arrow-up' : 'bi-arrow-down']"
              ></i>
            </th>
          </tr>
        </thead>
        <tbody class="text-dark bg-white">
          <tr v-for="row in tableData" :key="row.iso_a3">
            <td>{{ row.name }}</td>
            <td class="text-end">{{ formatValue(row.value) }}</td>
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

<style scoped>
@media (max-width: 430px) and (max-height: 932px) {
  .table-panel {
    order: 1;
    top: 30%;
    left: 10%;
  }
}
</style>
