<template>
  <div class="status-overlay">
    <template v-if="hasSelectedIndicator">
      <div v-if="loading" class="status-message p-4 rounded-4 fs-4">
        {{ $t('loading_indication') }}
      </div>
      <div v-else-if="error" class="error p-4 rounded-4 fs-4">
        {{ error }}
      </div>
    </template>
    <div v-else class="status-message p-4 rounded-4 fs-4 border-danger border-5">
      {{ $t('initial_indication') }}
    </div>
  </div>
</template>

<script setup>
defineProps({
  loading: { type: Boolean, required: true },
  error: { type: String, default: null },
  hasSelectedIndicator: { type: Boolean, required: true }
})
</script>
