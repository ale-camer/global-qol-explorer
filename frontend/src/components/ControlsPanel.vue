<template>
  <div
    :class="[
      'controls-panel',
      {
        'highlight-onboarding': !selectedIndicator,
        'active-panel': selectedIndicator
      }
    ]"
  >
    <div class="control-group">
      <label for="indicator-select" class="control-label">
        <i class="bi bi-bar-chart-line me-1"></i>
        {{ $t('indicator') }}
      </label>
      <select
        id="indicator-select"
        class="form-select modern-select"
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

    <div v-if="selectedIndicator" class="control-group mt-3 pt-3 border-top-subtle">
      <div class="d-flex justify-content-between align-items-center mb-2">
        <label class="control-label m-0">
          <i class="bi bi-calendar3 me-1"></i>
          {{ $t('year_range') }}
        </label>
        <span class="year-pill">{{ fromYear }} – {{ toYear }}</span>
      </div>
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
      <div class="d-flex justify-content-between mt-1 slider-extremes">
        <span>{{ sliderMinYear }}</span>
        <span>{{ sliderMaxYear }}</span>
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
