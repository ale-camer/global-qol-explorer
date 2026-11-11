<template>
  <div class="map-wrapper">
    <l-map
      ref="mapRef"
      :zoom="initialZoom"
      :min-zoom="minZoom"
      :max-zoom="8"
      :center="[15, 10]"
      :max-bounds="[
        [-85, -180],
        [85, 180]
      ]"
      :use-global-leaflet="false"
      :options="{
        zoomControl: false,
        attributionControl: false,
        zoomSnap: 0.1,
        zoomDelta: 0.5,
        maxBoundsViscosity: 1.0,
        worldCopyJump: false
      }"
      @ready="onMapReady"
    >
      <l-tile-layer
        url="https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}"
        name="Esri World Dark Gray"
      />
      <l-geo-json
        v-if="mapData"
        ref="geoJsonRef"
        :key="JSON.stringify(mapData.features.map((f) => f.properties.value))"
        :geojson="mapData"
        :options-style="getStyleForFeature"
        :options="{ onEachFeature }"
      />
    </l-map>

    <div class="bottom-right-dock" role="group" aria-label="Map and language controls">
      <slot name="language-trigger" />

      <div class="map-nav-controls">
        <button
          type="button"
          class="map-nav-btn"
          title="Zoom in"
          aria-label="Zoom in"
          @click="zoomIn"
        >
          <i class="bi bi-plus-lg"></i>
        </button>
        <button
          type="button"
          class="map-nav-btn"
          title="Zoom out"
          aria-label="Zoom out"
          @click="zoomOut"
        >
          <i class="bi bi-dash-lg"></i>
        </button>
        <button
          type="button"
          class="map-nav-btn"
          title="Reset world view"
          aria-label="Reset world view"
          @click="resetView"
        >
          <i class="bi bi-globe2"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { LMap, LTileLayer, LGeoJson } from '@vue-leaflet/vue-leaflet'

if (typeof window !== 'undefined') {
  window.L = L
}

defineProps({
  geojsonData: { type: Object, required: true },
  mapData: { type: Object, default: null },
  getStyleForFeature: { type: Function, required: true },
  onEachFeature: { type: Function, required: true }
})

function computeViewportMinZoom() {
  if (typeof window === 'undefined') return 2.6
  const widthZoom = Math.log2(window.innerWidth / 256)
  const heightZoom = Math.log2(window.innerHeight / 256)
  return Math.max(2.2, Number(Math.max(widthZoom, heightZoom).toFixed(1)))
}

const DEFAULT_CENTER = [15, 10]
const minZoom = ref(computeViewportMinZoom())
const initialZoom = ref(computeViewportMinZoom())

const mapRef = ref(null)
const geoJsonRef = ref(null)

function getLeafletMap() {
  return mapRef.value?.leafletObject || null
}

function onMapReady(leafletMap) {
  const z = computeViewportMinZoom()
  minZoom.value = z
  leafletMap.setMinZoom(z)
  if (leafletMap.getZoom() < z) {
    leafletMap.setView(DEFAULT_CENTER, z, { animate: false })
  }
}

function handleResize() {
  const leafletMap = getLeafletMap()
  if (!leafletMap) return
  const z = computeViewportMinZoom()
  minZoom.value = z
  leafletMap.setMinZoom(z)
  if (leafletMap.getZoom() < z) {
    leafletMap.setZoom(z)
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
})

function zoomIn() {
  const leafletMap = getLeafletMap()
  if (leafletMap) {
    leafletMap.zoomIn(0.5)
  }
}

function zoomOut() {
  const leafletMap = getLeafletMap()
  if (leafletMap) {
    leafletMap.zoomOut(0.5)
  }
}

function resetView() {
  const leafletMap = getLeafletMap()
  if (leafletMap) {
    const z = computeViewportMinZoom()
    leafletMap.flyTo(DEFAULT_CENTER, z, { duration: 0.6 })
  }
}

function focusCountry(isoA3) {
  const leafletMap = getLeafletMap()
  const geoJsonLayer = geoJsonRef.value?.leafletObject
  if (!leafletMap || !geoJsonLayer || !isoA3) return

  let targetLayer = null
  geoJsonLayer.eachLayer((layer) => {
    if (layer.feature?.properties?.iso_a3 === isoA3) {
      targetLayer = layer
    } else if (layer.setStyle) {
      const hasVal = layer.feature?.properties?.value != null
      layer.setStyle({
        weight: 0.8,
        color: hasVal ? '#0f172a' : '#334155',
        fillOpacity: hasVal ? 0.82 : 0.45
      })
      layer.closeTooltip?.()
    }
  })

  if (targetLayer && targetLayer.getBounds) {
    const bounds = targetLayer.getBounds()
    if (bounds.isValid()) {
      leafletMap.flyToBounds(bounds, {
        padding: [90, 90],
        maxZoom: 5,
        duration: 0.65
      })
    }
    targetLayer.setStyle?.({
      weight: 2.8,
      color: '#38bdf8',
      fillOpacity: 0.96
    })
    targetLayer.bringToFront?.()
    targetLayer.openTooltip?.()
  }
}

defineExpose({
  getLeafletMap,
  geoJsonRef,
  resetView,
  focusCountry
})
</script>
