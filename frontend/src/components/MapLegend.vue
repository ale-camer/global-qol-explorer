<template>
  <div class="legend-panel p-3">
    <h6 class="legend-title mb-2 text-dark">{{ indicatorName }}</h6>
    <div class="legend-gradient" :style="gradientStyle"></div>
    <div class="legend-labels d-flex justify-content-between mt-1">
      <span class="text-dark fw-light">{{ minFormatted }}</span>
      <span class="text-dark fw-light">{{ maxFormatted }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  palette: { type: Array, required: true },
  valueBounds: {
    type: Object,
    required: true,
    validator: (b) => typeof b.min === 'number' && typeof b.max === 'number'
  },
  indicatorName: { type: String, required: true }
})

const gradientStyle = computed(() => ({
  background: `linear-gradient(to right, ${props.palette.join(', ')})`
}))

const minFormatted = computed(() => props.valueBounds.min.toFixed(2))
const maxFormatted = computed(() => props.valueBounds.max.toFixed(2))
</script>
