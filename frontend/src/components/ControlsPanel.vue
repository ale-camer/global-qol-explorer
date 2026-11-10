<template>
  <div
    :class="[
      'controls-panel p-4',
      {
        'highlight-onboarding': !selectedIndicator,
        'active-panel': selectedIndicator
      }
    ]"
  >
    <div class="mb-3">
      <label for="indicator-select" class="form-label text-dark">
        {{ $t('indicator') }}
      </label>
      <select
        id="indicator-select"
        class="form-select"
        :value="selectedIndicator"
        @change="onIndicatorChange"
      >
        <option disabled value="" hidden>{{ $t('indicator_example') }}</option>
        <optgroup
          v-for="group in indicatorGroups"
          :key="group.category"
          :label="group.category"
        >
          <option
            v-for="ind in group.indicators"
            :key="ind.indicator_name"
            :value="ind.indicator_name"
          >
            {{ formatIndicatorName(ind.indicator_name) }}
          </option>
        </optgroup>
      </select>
    </div>

    <div v-if="selectedIndicator">
      <div class="mb-3">
        <label class="form-label text-dark">
          {{ $t('year_range') }}
          <strong>{{ fromYear }} - {{ toYear }}</strong>
        </label>
        <div class="range-slider">
          <div class="slider-track" :style="sliderTrackStyle"></div>
          <input
            type="range"
            :min="sliderMinYear"
            :max="sliderMaxYear"
            :value="fromYear"
            @input="onFromYearInput"
          />
          <input
            type="range"
            :min="sliderMinYear"
            :max="sliderMaxYear"
            :value="toYear"
            @input="onToYearInput"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { formatIndicatorName } from '../utils/helpers'

defineProps({
  indicatorGroups: { type: Array, required: true },
  selectedIndicator: { type: String, required: true },
  sliderMinYear: { type: Number, default: 2000 },
  sliderMaxYear: { type: Number, default: 2023 },
  fromYear: { type: Number, default: 2000 },
  toYear: { type: Number, default: 2023 },
  sliderTrackStyle: { type: Object, required: true }
})

const emit = defineEmits(['update:selectedIndicator', 'update:fromYear', 'update:toYear'])

const onIndicatorChange = (e) => emit('update:selectedIndicator', e.target.value)
const onFromYearInput = (e) => emit('update:fromYear', Number(e.target.value))
const onToYearInput = (e) => emit('update:toYear', Number(e.target.value))
</script>

<style scoped>
@media (max-width: 430px) and (max-height: 932px) {
  .controls-panel {
    order: 0;
    top: 2.5%;
    left: 0.01%;
  }
  .controls-panel.active-panel {
    top: 5%;
    left: 10%;
  }
}
</style>
