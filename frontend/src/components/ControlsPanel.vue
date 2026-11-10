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
    <!-- STEP 1: Categories (completely collapses into a clickable trigger once a category is chosen) -->
    <div class="control-group">
      <!-- Expanded Category List -->
      <template v-if="isCategoryOpen">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <label class="control-label m-0">
            <i class="bi bi-grid-1x2 me-1"></i>
            Category
          </label>
          <button
            v-if="selectedCategory"
            type="button"
            class="collapse-pill-btn"
            @click="isCategoryOpen = false"
          >
            <i class="bi bi-chevron-up"></i>
          </button>
        </div>

        <div class="category-grid">
          <button
            v-for="group in indicatorGroups"
            :key="group.category"
            type="button"
            :class="['category-item', { active: selectedCategory === group.category }]"
            @click="selectCategory(group.category)"
          >
            <span class="cat-icon">
              <i :class="getCategoryIcon(group.category)"></i>
            </span>
            <span class="cat-name">{{ group.category }}</span>
            <span class="cat-count">{{ group.indicators.length }}</span>
          </button>
        </div>
      </template>

      <!-- Collapsed Category Trigger (click to re-open categories) -->
      <button
        v-else
        type="button"
        class="collapsed-selector-bar"
        title="Click to change category"
        @click="openCategoryList"
      >
        <span class="cat-icon">
          <i :class="getCategoryIcon(selectedCategory)"></i>
        </span>
        <div class="collapsed-bar-text">
          <span class="collapsed-bar-label">Category</span>
          <span class="collapsed-bar-value">{{ selectedCategory }}</span>
        </div>
        <i class="bi bi-chevron-down ms-auto collapsed-chevron"></i>
      </button>
    </div>

    <!-- STEP 2: Indicators inside the chosen Category -->
    <div
      v-if="selectedCategory && activeCategoryIndicators.length > 0 && !isCategoryOpen"
      class="control-group mt-3 pt-3 border-top-subtle"
    >
      <template v-if="isIndicatorListOpen">
        <div class="d-flex justify-content-between align-items-center mb-2">
          <label class="control-label m-0">
            <i class="bi bi-bar-chart-line me-1"></i>
            {{ $t('indicator') }}
          </label>
          <button
            v-if="selectedIndicator"
            type="button"
            class="collapse-pill-btn"
            @click="isIndicatorListOpen = false"
          >
            <i class="bi bi-chevron-up"></i>
          </button>
        </div>

        <div class="indicator-list">
          <button
            v-for="ind in activeCategoryIndicators"
            :key="ind.indicator_name"
            type="button"
            :class="['indicator-item', { active: selectedIndicator === ind.indicator_name }]"
            @click="onSelectIndicator(ind.indicator_name)"
          >
            <span>{{ formatIndicatorName(ind.indicator_name) }}</span>
            <i
              v-if="selectedIndicator === ind.indicator_name"
              class="bi bi-check-circle-fill ms-2"
            ></i>
          </button>
        </div>
      </template>

      <!-- Collapsed Indicator Trigger (once an indicator is chosen, collapses cleanly; click to reopen) -->
      <button
        v-else
        type="button"
        class="collapsed-selector-bar active-indicator-bar"
        title="Click to change indicator"
        @click="isIndicatorListOpen = true"
      >
        <span class="cat-icon">
          <i class="bi bi-bar-chart-line-fill"></i>
        </span>
        <div class="collapsed-bar-text">
          <span class="collapsed-bar-label">{{ $t('indicator') }}</span>
          <span class="collapsed-bar-value">{{ formatIndicatorName(selectedIndicator) }}</span>
        </div>
        <i class="bi bi-chevron-down ms-auto collapsed-chevron"></i>
      </button>
    </div>

    <!-- STEP 3: Year Range Slider -->
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
import { ref, computed, watch } from 'vue'
import { formatIndicatorName } from '../utils/helpers'

const props = defineProps({
  indicatorGroups: { type: Array, required: true },
  selectedIndicator: { type: String, required: true },
  sliderMinYear: { type: Number, default: 2000 },
  sliderMaxYear: { type: Number, default: 2023 },
  fromYear: { type: Number, default: 2000 },
  toYear: { type: Number, default: 2023 },
  sliderTrackStyle: { type: Object, required: true }
})

const emit = defineEmits(['update:selectedIndicator', 'update:fromYear', 'update:toYear'])

const selectedCategory = ref('')
const isCategoryOpen = ref(true)
const isIndicatorListOpen = ref(true)

const CATEGORY_ICONS = {
  'Demography and Population Structure': 'bi-people-fill',
  'Economy and Labor': 'bi-cash-coin',
  'Education, Science and Technology': 'bi-mortarboard-fill',
  'Environment and Sustainability': 'bi-tree-fill',
  'Food and Nutrition': 'bi-basket2-fill',
  'Health and Wellbeing': 'bi-heart-pulse-fill',
  'Society, Security and Rights': 'bi-shield-check',
  'Subjective Wellbeing and Human Development': 'bi-stars'
}

function getCategoryIcon(category) {
  return CATEGORY_ICONS[category] || 'bi-folder2-open'
}

const activeCategoryIndicators = computed(() => {
  const group = props.indicatorGroups.find((g) => g.category === selectedCategory.value)
  return group ? group.indicators : []
})

function openCategoryList() {
  isCategoryOpen.value = true
}

function selectCategory(category) {
  selectedCategory.value = category
  isCategoryOpen.value = false
  isIndicatorListOpen.value = true
}

function onSelectIndicator(indicatorName) {
  emit('update:selectedIndicator', indicatorName)
  isIndicatorListOpen.value = false
}

watch(
  () => props.selectedIndicator,
  (ind) => {
    if (ind && !selectedCategory.value) {
      const found = props.indicatorGroups.find((g) =>
        g.indicators.some((i) => i.indicator_name === ind)
      )
      if (found) {
        selectedCategory.value = found.category
        isCategoryOpen.value = false
      }
    }
  }
)

const onFromYearInput = (e) => emit('update:fromYear', Number(e.target.value))
const onToYearInput = (e) => emit('update:toYear', Number(e.target.value))
</script>
