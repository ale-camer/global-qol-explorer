<template>
  <div class="cover-overlay">
    <div class="cover-content p-5">
      <h1 class="display-3 fw-bold mb-3">{{ $t('title') }}</h1>
      <p class="lead mb-4">{{ $t('first_paragraph_intro') }}</p>
      <p class="mb-5 fs-5">{{ $t('second_paragraph_intro') }}</p>
      <button class="explore-button btn btn-lg" @click="emit('start-explore')">
        {{ $t('intro_button') }}
        <i class="bi bi-arrow-right-circle-fill ms-2"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
const emit = defineEmits(['start-explore'])
</script>
