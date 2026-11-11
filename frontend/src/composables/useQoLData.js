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
  const yearBoundsVersion = ref(0)
  const activeIndicatorForYears = ref('')
  let yearsAbortController = null

  const sliderTrackStyle = computed(() =>
    getSliderTrackStyle(fromYear.value, toYear.value, sliderMinYear.value, sliderMaxYear.value)
  )

  async function loadYearBounds() {
    if (yearsAbortController) {
      yearsAbortController.abort()
    }
    const indicator = selectedIndicator.value
    if (!indicator) {
      activeIndicatorForYears.value = ''
      return
    }
    yearsAbortController = new AbortController()
    try {
      yearRangeError.value = null
      const bounds = await fetchYears(indicator, { signal: yearsAbortController.signal })
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
      activeIndicatorForYears.value = indicator
      yearBoundsVersion.value += 1
    } catch (err) {
      if (err?.name === 'AbortError') return
      console.error('Failed to load year bounds:', err)
      yearRangeError.value = 'Could not load available years for this indicator.'
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
    yearRangeError,
    yearBoundsVersion,
    activeIndicatorForYears
  }
}

export function useIndicatorData(
  selectedIndicator,
  fromYear,
  toYear,
  sortBy,
  yearBoundsVersion,
  activeIndicatorForYears,
  yearRangeError
) {
  const rawData = ref([])
  const loading = ref(false)
  const dataError = ref(null)
  let dataAbortController = null

  const tableData = computed(() => {
    const validSorted = [...rawData.value]
      .filter((r) => r.value != null)
      .sort((a, b) => b.value - a.value)
    const totalRanked = validSorted.length
    const rankMap = new Map()
    validSorted.forEach((r, idx) => {
      rankMap.set(r.iso_a3, idx + 1)
    })

    const rows = rawData.value.map((r) => ({
      ...r,
      rank: rankMap.get(r.iso_a3) ?? null,
      totalRanked
    }))

    const currentSort = sortBy?.value || 'country_asc'
    return rows.sort((a, b) => {
      if (currentSort === 'country_asc') {
        return (a.name || '').localeCompare(b.name || '')
      }
      if (currentSort === 'country_desc') {
        return (b.name || '').localeCompare(a.name || '')
      }
      if (currentSort === 'value_asc') {
        return (a.value ?? Infinity) - (b.value ?? Infinity)
      }
      if (currentSort === 'value_desc') {
        return (b.value ?? -Infinity) - (a.value ?? -Infinity)
      }
      return 0
    })
  })

  async function loadData() {
    if (!selectedIndicator.value) {
      rawData.value = []
      loading.value = false
      return
    }
    if (dataAbortController) {
      dataAbortController.abort()
    }
    const controller = new AbortController()
    dataAbortController = controller

    loading.value = true
    dataError.value = null
    try {
      const result = await fetchIndicatorData(
        selectedIndicator.value,
        fromYear.value,
        toYear.value,
        sortBy.value,
        { signal: controller.signal }
      )
      rawData.value = result
    } catch (err) {
      if (err?.name === 'AbortError') return
      dataError.value = 'Failed to load indicator data.'
      rawData.value = []
    } finally {
      if (dataAbortController === controller) {
        loading.value = false
      }
    }
  }

  const debouncedLoad = debounce(loadData, 400)

  watch(selectedIndicator, (newInd) => {
    debouncedLoad.cancel()
    if (dataAbortController) {
      dataAbortController.abort()
    }
    rawData.value = []
    dataError.value = null
    loading.value = !!newInd
  })

  watch([fromYear, toYear], () => {
    if (!selectedIndicator.value) return
    if (activeIndicatorForYears && activeIndicatorForYears.value !== selectedIndicator.value) {
      return
    }
    debouncedLoad()
  })

  if (yearBoundsVersion) {
    watch(yearBoundsVersion, () => {
      debouncedLoad.cancel()
      loadData()
    })
  }

  if (yearRangeError) {
    watch(yearRangeError, (err) => {
      if (err) {
        loading.value = false
      }
    })
  }

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

export function useMapChloropleth(geojsonData, tableData, selectedCountryIso) {
  const mapData = computed(() =>
    geojsonData.value ? mergeGeojsonWithData(geojsonData.value, tableData.value) : null
  )
  const valueBounds = computed(() => computeValueBounds(tableData.value))

  return {
    mapData,
    valueBounds,
    getStyleForFeature: (feature) =>
      getFeatureStyle(feature, valueBounds.value, selectedCountryIso?.value || '')
  }
}
