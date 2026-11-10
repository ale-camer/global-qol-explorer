<template>
  <div class="app-container">
    <MapView
      v-if="geojsonData"
      class="map-background"
      :geojsonData="geojsonData"
      :mapData="mapData"
      :getStyleForFeature="getStyleForFeature"
      :onEachFeature="bindFeatureInteractions"
    />

    <LanguageSwitcher />

    <transition v-if="showCover" name="fade">
      <AppCover v-if="showCover" @start-explore="showCover = false" />
    </transition>

    <transition v-else name="fade">
      <div class="overlay-content">
        <AppHeader />

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
          <TablePanel
            v-if="selectedIndicator && !loading && !combinedError && tableData.length > 0"
            :table-data="tableData"
            :sort-column="sortColumn"
            :sort-direction="sortDirection"
            v-model:is-table-collapsed="isTableCollapsed"
            @set-sort="setSort"
            @download-csv="handleDownload(tableData)"
          />
        </transition>

        <transition name="fade">
          <StatusOverlay
            v-if="!selectedIndicator || loading || combinedError"
            :loading="loading"
            :error="combinedError"
            :has-selected-indicator="!!selectedIndicator"
          />
        </transition>

        <transition name="fade-slide-up">
          <MapLegend
            v-if="selectedIndicator && !loading && !combinedError && tableData.length > 0"
            :palette="COLOR_PALETTE"
            :value-bounds="valueBounds"
            :indicator-name="formatIndicatorName(selectedIndicator)"
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
import AppHeader from './components/AppHeader.vue'
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
  bindFeatureInteractions,
  formatIndicatorName
} from './utils/helpers'

const showCover = ref(true)
const selectedIndicator = ref('')

const { indicatorGroups, geojsonData, initialError } = useInitialMetadata()
const {
  sliderMinYear,
  sliderMaxYear,
  fromYear,
  toYear,
  sliderTrackStyle,
  yearRangeError
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
  sortBy
)

const { mapData, valueBounds, getStyleForFeature } = useMapChloropleth(
  geojsonData,
  tableData
)

const combinedError = computed(
  () => initialError.value || yearRangeError.value || dataError.value
)

watch(selectedIndicator, () => {
  sortBy.value = 'country_asc'
})
</script>
