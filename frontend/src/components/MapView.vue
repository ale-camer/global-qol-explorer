<template>
  <l-map
    ref="map"
    :zoom="2"
    :center="[30, 10]"
    :options="{ zoomControl: false, attributionControl: false }"
  >
    <l-tile-layer
      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      name="OpenStreetMap"
    />
    <l-geo-json
      v-if="mapData"
      :key="JSON.stringify(mapData.features.map((f) => f.properties.value))"
      :geojson="mapData"
      :options-style="getStyleForFeature"
      :options-on-each-feature="onEachFeature"
    />
  </l-map>
</template>

<script setup>
import { ref } from 'vue'
import 'leaflet/dist/leaflet.css'
import { LMap, LTileLayer, LGeoJson } from '@vue-leaflet/vue-leaflet'

defineProps({
  geojsonData: { type: Object, required: true },
  mapData: { type: Object, default: null },
  getStyleForFeature: { type: Function, required: true },
  onEachFeature: { type: Function, required: true }
})

const map = ref(null)
</script>
