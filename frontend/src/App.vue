<template>
  <div class="app-container">
    <MapView
      v-if="geojsonData"
      ref="mapViewRef"
      class="map-background"
      :geojsonData="geojsonData"
      :mapData="mapData"
      :getStyleForFeature="getStyleForFeature"
      :onEachFeature="onEachFeature"
    >
      <template #language-trigger>
        <LanguageSwitcher />
      </template>
    </MapView>

    <transition v-if="showCover" name="fade">
      <AppCover v-if="showCover" @start-explore="showCover = false" />
    </transition>

    <transition v-else name="fade">
      <div class="overlay-content">
        <div class="left-dock">
          <ControlsPanel
            :indicator-groups="indicatorGroups"
            :slider-min-year="sliderMinYear"
            :slider-max-year="sliderMaxYear"
            :slider-track-style="sliderTrackStyle"
            v-model:selected-indicator="selectedIndicator"
            v-model:from-year="fromYear"
            v-model:to-year="toYear"
          />

          <transition name="fade-slide-up">
            <MapLegend
              v-if="selectedIndicator && !loading && !combinedError && tableData.length > 0"
              :palette="COLOR_PALETTE"
              :value-bounds="valueBounds"
              :indicator-name="formatIndicatorName(selectedIndicator)"
            />
          </transition>
        </div>

        <transition name="fade-slide-up">
          <TablePanel
            v-if="selectedIndicator && !loading && !combinedError && tableData.length > 0"
            :table-data="tableData"
            :sort-column="sortColumn"
            :sort-direction="sortDirection"
            :selected-country-iso="selectedCountryIso"
            v-model:is-table-collapsed="isTableCollapsed"
            @set-sort="setSort"
            @download-csv="handleDownload(tableData)"
            @select-country="handleSelectCountryFromTable"
          />
        </transition>

        <transition name="fade">
          <StatusOverlay
            v-if="!selectedIndicator || loading || combinedError || tableData.length === 0"
            :loading="loading"
            :error="combinedError"
            :has-selected-indicator="!!selectedIndicator"
            :is-empty="!!selectedIndicator && !loading && !combinedError && tableData.length === 0"
          />
        </transition>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import MapView from './components/MapView.vue'
import LanguageSwitcher from './components/LanguageSwitcher.vue'
import AppCover from './components/AppCover.vue'
import ControlsPanel from './components/ControlsPanel.vue'
import TablePanel from './components/TablePanel.vue'
import StatusOverlay from './components/StatusOverlay.vue'
import MapLegend from './components/MapLegend.vue'
import {
  useInitialMetadata,
  useYearRange,
  useTableState,
  useIndicatorData,
  useMapChloropleth
} from './composables/useQoLData'
import {
  COLOR_PALETTE,
  createFeatureInteractionHandler,
  formatIndicatorName
} from './utils/helpers'

const showCover = ref(true)
const selectedIndicator = ref('')
const selectedCountryIso = ref('')
const mapViewRef = ref(null)

const { indicatorGroups, geojsonData, initialError } = useInitialMetadata()
const {
  sliderMinYear,
  sliderMaxYear,
  fromYear,
  toYear,
  sliderTrackStyle,
  yearRangeError,
  yearBoundsVersion,
  activeIndicatorForYears
} = useYearRange(selectedIndicator)

const {
  isTableCollapsed,
  sortBy,
  sortColumn,
  sortDirection,
  setSort,
  handleDownload
} = useTableState(selectedIndicator, fromYear, toYear)

const { tableData, loading, dataError } = useIndicatorData(
  selectedIndicator,
  fromYear,
  toYear,
  sortBy,
  yearBoundsVersion,
  activeIndicatorForYears,
  yearRangeError
)

const { mapData, valueBounds, getStyleForFeature } = useMapChloropleth(
  geojsonData,
  tableData,
  selectedCountryIso
)

const onEachFeature = createFeatureInteractionHandler(
  (isoA3) => {
    selectedCountryIso.value = isoA3
  },
  () => selectedCountryIso.value
)

function handleSelectCountryFromTable(isoA3) {
  if (selectedCountryIso.value === isoA3) {
    selectedCountryIso.value = ''
    mapViewRef.value?.resetView?.()
    return
  }
  selectedCountryIso.value = isoA3
  mapViewRef.value?.focusCountry?.(isoA3)
}

const combinedError = computed(
  () => initialError.value || yearRangeError.value || dataError.value
)

watch(selectedIndicator, () => {
  sortBy.value = 'country_asc'
  selectedCountryIso.value = ''
  if (typeof window !== 'undefined' && window.innerWidth <= 768) {
    isTableCollapsed.value = true
  }
})
</script>
