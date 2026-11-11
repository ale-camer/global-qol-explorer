<template>
  <!-- MODE A: Bottom-Center Selection Dock (stays here for BOTH Step 1: Classification AND Step 2: Indicator) -->
  <div v-if="isShowcaseOpen" class="category-showcase-dock">
    <!-- Top bar of the bottom-center dock -->
    <div class="showcase-header">
      <button
        v-if="showcaseStep === 'indicators'"
        type="button"
        class="back-to-cats-btn"
        @click="backToClassifications"
      >
        <i class="bi bi-arrow-left"></i>
        <span>{{ selectedCategory }}</span>
      </button>

      <div class="showcase-search-wrap">
        <i class="bi bi-search showcase-search-icon"></i>
        <input
          v-model="showcaseSearch"
          type="text"
          class="showcase-search-input"
          :placeholder="
            showcaseStep === 'categories'
              ? 'Search classification or indicator (e.g. GDP, Health, CO2)...'
              : `Filter indicators in ${selectedCategory}...`
          "
          aria-label="Search classification or indicator"
        />
        <button
          v-if="showcaseSearch"
          type="button"
          class="clear-search-btn"
          @click="showcaseSearch = ''"
        >
          <i class="bi bi-x-lg"></i>
        </button>
      </div>

      <button
        v-if="selectedIndicator"
        type="button"
        class="showcase-close-btn"
        title="Minimize to corner"
        @click="isShowcaseOpen = false"
      >
        <i class="bi bi-x-lg"></i>
      </button>
    </div>

    <!-- STEP 1 IN BOTTOM-CENTER DOCK: Visual Classification Cards -->
    <template v-if="showcaseStep === 'categories'">
      <!-- Direct indicator matches when typing in search -->
      <div
        v-if="showcaseSearch.trim() && matchingIndicatorsAll.length > 0"
        class="quick-indicator-matches"
      >
        <span class="matches-label">Matching Indicators</span>
        <div class="matches-pills">
          <button
            v-for="item in matchingIndicatorsAll"
            :key="item.indicator_name"
            type="button"
            class="match-pill-btn"
            @click="selectCategoryAndIndicator(item.category, item.indicator_name)"
          >
            <i :class="[getCategoryMeta(item.category).icon, 'me-1']"></i>
            <span>{{ formatIndicatorName(item.indicator_name) }}</span>
          </button>
        </div>
      </div>

      <div class="category-cards-grid">
        <button
          v-for="group in filteredCategoryGroups"
          :key="group.category"
          type="button"
          :class="['category-visual-card', { active: selectedCategory === group.category }]"
          @click="selectClassification(group.category)"
        >
          <div
            class="category-card-art"
            :style="{ background: getCategoryMeta(group.category).gradient }"
          >
            <i :class="[getCategoryMeta(group.category).icon, 'category-art-icon']"></i>
            <span class="category-card-badge">{{ group.indicators.length }}</span>
          </div>
          <div class="category-card-body">
            <span class="category-card-title">{{ group.category }}</span>
          </div>
        </button>

        <div v-if="filteredCategoryGroups.length === 0" class="no-categories-msg">
          No matching classifications found.
        </div>
      </div>
    </template>

    <!-- STEP 2 IN BOTTOM-CENTER DOCK: Indicators of the chosen Classification -->
    <template v-else>
      <div class="showcase-indicators-grid">
        <button
          v-for="ind in filteredActiveIndicators"
          :key="ind.indicator_name"
          type="button"
          :class="['showcase-indicator-card', { active: selectedIndicator === ind.indicator_name }]"
          @click="onSelectIndicator(ind.indicator_name)"
        >
          <span
            class="showcase-ind-icon"
            :style="{ background: getCategoryMeta(selectedCategory).gradient }"
          >
            <i :class="getCategoryMeta(selectedCategory).icon"></i>
          </span>
          <span class="showcase-ind-name">{{ formatIndicatorName(ind.indicator_name) }}</span>
          <i
            :class="[
              'bi ms-auto showcase-ind-arrow',
              selectedIndicator === ind.indicator_name ? 'bi-check-circle-fill' : 'bi-arrow-right-short'
            ]"
          ></i>
        </button>

        <div v-if="filteredActiveIndicators.length === 0" class="no-categories-msg">
          No matching indicators in this classification.
        </div>
      </div>
    </template>
  </div>

  <!-- MODE B: Docked at Bottom-Left Corner over the Ocean ONLY AFTER an Indicator is chosen -->
  <div v-else class="controls-panel active-panel">
    <!-- Collapsed Classification Bar (click to reopen Step 1 in bottom-center) -->
    <div class="control-group">
      <button
        type="button"
        class="collapsed-selector-bar"
        title="Click to change classification"
        @click="openClassificationsStep"
      >
        <span
          class="cat-icon"
          :style="{ background: getCategoryMeta(selectedCategory).gradient }"
        >
          <i :class="getCategoryMeta(selectedCategory).icon"></i>
        </span>
        <div class="collapsed-bar-text">
          <span class="collapsed-bar-label">Classification</span>
          <span class="collapsed-bar-value">{{ selectedCategory }}</span>
        </div>
        <i class="bi bi-grid-fill ms-auto collapsed-chevron"></i>
      </button>
    </div>

    <!-- Collapsed Indicator Bar (click to reopen Step 2 in bottom-center) -->
    <div class="control-group mt-2">
      <button
        type="button"
        class="collapsed-selector-bar active-indicator-bar"
        title="Click to change indicator"
        @click="openIndicatorsStep"
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

    <!-- Year Range Slider -->
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
const isShowcaseOpen = ref(true)
const showcaseStep = ref('categories') // 'categories' | 'indicators'
const showcaseSearch = ref('')

const CATEGORY_META = {
  'Demography and Population Structure': {
    icon: 'bi-people-fill',
    gradient: 'linear-gradient(135deg, rgba(14, 165, 233, 0.35), rgba(37, 99, 235, 0.45))'
  },
  'Economy and Labor': {
    icon: 'bi-cash-coin',
    gradient: 'linear-gradient(135deg, rgba(16, 185, 129, 0.35), rgba(5, 150, 105, 0.45))'
  },
  'Education, Science and Technology': {
    icon: 'bi-mortarboard-fill',
    gradient: 'linear-gradient(135deg, rgba(139, 92, 246, 0.35), rgba(109, 40, 217, 0.45))'
  },
  'Environment and Sustainability': {
    icon: 'bi-tree-fill',
    gradient: 'linear-gradient(135deg, rgba(34, 197, 94, 0.35), rgba(21, 128, 61, 0.45))'
  },
  'Food and Nutrition': {
    icon: 'bi-basket2-fill',
    gradient: 'linear-gradient(135deg, rgba(245, 158, 11, 0.35), rgba(217, 119, 6, 0.45))'
  },
  'Health and Wellbeing': {
    icon: 'bi-heart-pulse-fill',
    gradient: 'linear-gradient(135deg, rgba(244, 63, 94, 0.35), rgba(225, 29, 72, 0.45))'
  },
  'Society, Security and Rights': {
    icon: 'bi-shield-check',
    gradient: 'linear-gradient(135deg, rgba(59, 130, 246, 0.35), rgba(30, 64, 175, 0.45))'
  },
  'Subjective Wellbeing and Human Development': {
    icon: 'bi-stars',
    gradient: 'linear-gradient(135deg, rgba(236, 72, 153, 0.35), rgba(190, 24, 93, 0.45))'
  }
}

function getCategoryMeta(category) {
  return (
    CATEGORY_META[category] || {
      icon: 'bi-folder2-open',
      gradient: 'linear-gradient(135deg, rgba(56, 189, 248, 0.25), rgba(59, 130, 246, 0.35))'
    }
  )
}

const filteredCategoryGroups = computed(() => {
  const q = showcaseSearch.value.trim().toLowerCase()
  if (!q) return props.indicatorGroups
  return props.indicatorGroups.filter((group) => {
    const catMatch = group.category.toLowerCase().includes(q)
    const indMatch = group.indicators.some((ind) =>
      formatIndicatorName(ind.indicator_name).toLowerCase().includes(q)
    )
    return catMatch || indMatch
  })
})

const matchingIndicatorsAll = computed(() => {
  const q = showcaseSearch.value.trim().toLowerCase()
  if (!q) return []
  const matches = []
  for (const group of props.indicatorGroups) {
    for (const ind of group.indicators) {
      if (formatIndicatorName(ind.indicator_name).toLowerCase().includes(q)) {
        matches.push({ category: group.category, indicator_name: ind.indicator_name })
      }
    }
  }
  return matches.slice(0, 8)
})

const activeCategoryIndicators = computed(() => {
  const group = props.indicatorGroups.find((g) => g.category === selectedCategory.value)
  return group ? group.indicators : []
})

const filteredActiveIndicators = computed(() => {
  const q = showcaseSearch.value.trim().toLowerCase()
  if (!q) return activeCategoryIndicators.value
  return activeCategoryIndicators.value.filter((ind) =>
    formatIndicatorName(ind.indicator_name).toLowerCase().includes(q)
  )
})

function selectClassification(category) {
  selectedCategory.value = category
  showcaseSearch.value = ''
  showcaseStep.value = 'indicators'
}

function backToClassifications() {
  showcaseSearch.value = ''
  showcaseStep.value = 'categories'
}

function openClassificationsStep() {
  showcaseSearch.value = ''
  showcaseStep.value = 'categories'
  isShowcaseOpen.value = true
}

function openIndicatorsStep() {
  showcaseSearch.value = ''
  showcaseStep.value = 'indicators'
  isShowcaseOpen.value = true
}

function selectCategoryAndIndicator(category, indicatorName) {
  selectedCategory.value = category
  showcaseSearch.value = ''
  isShowcaseOpen.value = false
  emit('update:selectedIndicator', indicatorName)
}

function onSelectIndicator(indicatorName) {
  showcaseSearch.value = ''
  isShowcaseOpen.value = false
  emit('update:selectedIndicator', indicatorName)
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
        isShowcaseOpen.value = false
      }
    }
  }
)

const onFromYearInput = (e) => emit('update:fromYear', Number(e.target.value))
const onToYearInput = (e) => emit('update:toYear', Number(e.target.value))
</script>
