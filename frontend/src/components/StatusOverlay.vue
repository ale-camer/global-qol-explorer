<template>
  <div class="status-overlay">
    <div v-if="error" class="status-pill error-pill">
      <i class="bi bi-exclamation-triangle-fill me-2"></i>
      <span>{{ error }}</span>
    </div>
    <div v-else-if="!hasSelectedIndicator" class="status-pill onboarding-pill">
      <i class="bi bi-compass me-2"></i>
      <span>{{ $t('initial_indication') }}</span>
    </div>
    <div v-else-if="loading" class="status-pill loading-pill">
      <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
      <span>{{ $t('loading_indication') }}</span>
    </div>
    <div v-else-if="isEmpty" class="status-pill empty-pill">
      <i class="bi bi-info-circle me-2"></i>
      <span>No data available for the selected range.</span>
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
