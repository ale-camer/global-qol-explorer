<template>
  <div class="legend-panel">
    <div class="d-flex justify-content-between align-items-center mb-2">
      <h6 class="legend-title">{{ indicatorName }}</h6>
    </div>
    <div class="legend-gradient" :style="gradientStyle"></div>
    <div class="legend-labels d-flex justify-content-between mt-2">
      <span>{{ minFormatted }}</span>
      <span>{{ maxFormatted }}</span>
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

const minFormatted = computed(() =>
  props.valueBounds.min.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
)
const maxFormatted = computed(() =>
  props.valueBounds.max.toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
)
</script>
