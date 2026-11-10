import { ref, computed, watch, onMounted } from 'vue'
import {
  fetchIndicators,
  fetchYears,
  fetchWorldGeometry,
  fetchIndicatorData
} from '../services/api'
import {
  getSliderTrackStyle,
  debounce,
  toggleSortOrder,
  downloadCsv,
  mergeGeojsonWithData,
  computeValueBounds,
  getFeatureStyle
} from '../utils/helpers'

export function useInitialMetadata() {
  const indicatorGroups = ref([])
  const geojsonData = ref(null)
  const initialError = ref(null)

  onMounted(async () => {
    try {
      const [indicators, geometry] = await Promise.all([fetchIndicators(), fetchWorldGeometry()])
      indicatorGroups.value = indicators
      geojsonData.value = geometry
    } catch (err) {
      console.error('CRITICAL ERROR on mount:', err)
      initialError.value = 'Could not load initial application data. Please refresh the page.'
    }
  })

  return { indicatorGroups, geojsonData, initialError }
}

export function useYearRange(selectedIndicator) {
  const sliderMinYear = ref(1990)
  const sliderMaxYear = ref(2025)
  const fromYear = ref(2000)
  const toYear = ref(2020)
  const yearRangeError = ref(null)

  const sliderTrackStyle = computed(() =>
    getSliderTrackStyle(fromYear.value, toYear.value, sliderMinYear.value, sliderMaxYear.value)
  )

  async function loadYearBounds() {
    if (selectedIndicator.value) {
      try {
        yearRangeError.value = null
        const bounds = await fetchYears(selectedIndicator.value)
        if (bounds && bounds.length === 2) {
          sliderMinYear.value = bounds[0]
          sliderMaxYear.value = bounds[1]
          fromYear.value = bounds[0]
          toYear.value = bounds[1]
        } else if (bounds && bounds.length > 0) {
          sliderMinYear.value = bounds[0]
          sliderMaxYear.value = bounds[0]
          fromYear.value = bounds[0]
          toYear.value = bounds[0]
        }
      } catch (err) {
        console.error('Failed to load year bounds:', err)
        yearRangeError.value = 'Could not load available years for this indicator.'
      }
    }
  }

  watch(selectedIndicator, loadYearBounds)
  watch(fromYear, (val) => {
    if (parseInt(val) > parseInt(toYear.value)) {
      toYear.value = val
    }
  })
  watch(toYear, (val) => {
    if (parseInt(val) < parseInt(fromYear.value)) {
      fromYear.value = val
    }
  })

  return {
    sliderMinYear,
    sliderMaxYear,
    fromYear,
    toYear,
    sliderTrackStyle,
    yearRangeError
  }
}

export function useIndicatorData(selectedIndicator, fromYear, toYear, sortBy) {
  const tableData = ref([])
  const loading = ref(false)
  const dataError = ref(null)

  async function loadData() {
    if (!selectedIndicator.value) {
      tableData.value = []
      return
    }
    loading.value = true
    dataError.value = null
    try {
      tableData.value = await fetchIndicatorData(
        selectedIndicator.value,
        fromYear.value,
        toYear.value,
        sortBy.value
      )
    } catch {
      dataError.value = 'Failed to load indicator data.'
      tableData.value = []
    } finally {
      loading.value = false
    }
  }

  const debouncedLoad = debounce(loadData, 400)
  watch(selectedIndicator, () => {
    tableData.value = []
  })
  watch([fromYear, toYear, sortBy], debouncedLoad, { immediate: true })

  return { tableData, loading, dataError }
}

export function useTableState(selectedIndicator, fromYear, toYear) {
  const isTableCollapsed = ref(false)
  const sortBy = ref('country_asc')
  const sortColumn = computed(() => sortBy.value.split('_')[0])
  const sortDirection = computed(() => sortBy.value.split('_')[1])

  function setSort(column) {
    sortBy.value = toggleSortOrder(sortBy.value, column)
  }

  function handleDownload(rows) {
    downloadCsv(rows, selectedIndicator.value, fromYear.value, toYear.value)
  }

  return {
    isTableCollapsed,
    sortBy,
    sortColumn,
    sortDirection,
    setSort,
    handleDownload
  }
}

export function useMapChloropleth(geojsonData, tableData) {
  const mapData = computed(() =>
    geojsonData.value ? mergeGeojsonWithData(geojsonData.value, tableData.value) : null
  )
  const valueBounds = computed(() => computeValueBounds(tableData.value))

  return {
    mapData,
    valueBounds,
    getStyleForFeature: (feature) => getFeatureStyle(feature, valueBounds.value)
  }
}
