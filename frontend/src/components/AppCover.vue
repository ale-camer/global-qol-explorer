<template>
  <div class="cover-overlay">
    <div class="cover-content">
      <img :src="qolLogo" alt="Global Quality of Life Explorer" class="cover-app-logo" />
      <h1 class="cover-title">{{ $t('title') }}</h1>
      <p class="cover-lead">{{ $t('first_paragraph_intro') }}</p>
      <p class="cover-sub">{{ $t('second_paragraph_intro') }}</p>
      <button class="explore-button" @click="emit('start-explore')">
        <span>{{ $t('intro_button') }}</span>
        <i class="bi bi-arrow-right"></i>
      </button>
    </div>
  </div>
</template>

<script setup>
import qolLogo from '../assets/qol.png'

const emit = defineEmits(['start-explore'])
</script>
