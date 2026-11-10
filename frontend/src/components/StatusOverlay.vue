<template>
  <div class="status-overlay">
    <div v-if="error" class="error p-4 rounded-4 fs-4">
      {{ error }}
    </div>
    <div v-else-if="!hasSelectedIndicator" class="status-message p-4 rounded-4 fs-4 border-danger border-5">
      {{ $t('initial_indication') }}
    </div>
    <div v-else-if="loading" class="status-message p-4 rounded-4 fs-4">
      {{ $t('loading_indication') }}
    </div>
    <div v-else-if="isEmpty" class="status-message p-4 rounded-4 fs-4">
      No data available for the selected range.
    </div>
  </div>
</template>

<script setup>
defineProps({
  loading: { type: Boolean, required: true },
  error: { type: String, default: null },
  hasSelectedIndicator: { type: Boolean, required: true },
  isEmpty: { type: Boolean, default: false }
})
</script>
