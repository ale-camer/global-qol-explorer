<template>
  <div class="table-panel">
    <div class="panel-header">
      <div class="d-flex align-items-center gap-2">
        <h5 class="panel-title m-0">{{ $t('data_table') }}</h5>
        <span class="count-badge">{{ filteredData.length }}</span>
      </div>
      <div class="d-flex align-items-center gap-2">
        <button
          type="button"
          class="icon-action-btn"
          @click="emit('download-csv')"
          title="Download as CSV"
        >
          <i class="bi bi-download"></i>
        </button>
        <button
          type="button"
          class="icon-action-btn"
          @click="emit('update:isTableCollapsed', !isTableCollapsed)"
          title="Toggle table visibility"
        >
          <i :class="isTableCollapsed ? 'bi bi-chevron-down' : 'bi bi-chevron-up'"></i>
        </button>
      </div>
    </div>

    <div v-if="!isTableCollapsed" class="table-search-bar">
      <i class="bi bi-search search-icon"></i>
      <input
        v-model="searchQuery"
        type="text"
        class="table-search-input"
        :placeholder="`${$t('country_header')}...`"
        aria-label="Filter countries"
      />
      <button
        v-if="searchQuery"
        type="button"
        class="clear-search-btn"
        aria-label="Clear search"
        @click="searchQuery = ''"
      >
        <i class="bi bi-x-lg"></i>
      </button>
    </div>

    <div v-if="!isTableCollapsed" ref="tableContainerRef" class="table-container">
      <table class="modern-table">
        <thead>
          <tr>
            <th
              class="text-start rank-col sortable"
              @click="emit('set-sort', 'value')"
              title="Sort by Rank / Value"
            >
              #
            </th>
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
          <tr
            v-for="row in filteredData"
            :key="row.iso_a3"
            :data-iso="row.iso_a3"
            :class="['clickable-row', { 'selected-row': selectedCountryIso === row.iso_a3 }]"
            @click="emit('select-country', row.iso_a3)"
          >
            <td class="rank-cell">{{ row.rank ? `#${row.rank}` : '—' }}</td>
            <td class="country-cell">{{ row.name }}</td>
            <td class="value-cell text-end">{{ formatValue(row.value) }}</td>
          </tr>
          <tr v-if="filteredData.length === 0">
            <td colspan="3" class="text-center py-4 text-secondary">
              No matching countries
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'

const props = defineProps({
  tableData: { type: Array, required: true },
  isTableCollapsed: { type: Boolean, default: false },
  sortColumn: { type: String, required: true },
  sortDirection: { type: String, required: true },
  selectedCountryIso: { type: String, default: '' }
})

const emit = defineEmits(['update:isTableCollapsed', 'set-sort', 'download-csv', 'select-country'])

const searchQuery = ref('')
const tableContainerRef = ref(null)

const filteredData = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return props.tableData
  return props.tableData.filter(
    (r) =>
      r.name?.toLowerCase().includes(q) ||
      r.iso_a3?.toLowerCase().includes(q)
  )
})

watch(
  () => props.selectedCountryIso,
  async (iso) => {
    if (!iso || props.isTableCollapsed) return
    await nextTick()
    const rowEl = tableContainerRef.value?.querySelector(`tr[data-iso="${iso}"]`)
    if (rowEl) {
      rowEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    }
  }
)

const formatValue = (val) =>
  val == null
    ? 'N/A'
    : parseFloat(val).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
      })
</script>
