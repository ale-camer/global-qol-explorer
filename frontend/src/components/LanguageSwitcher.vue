<template>
  <div class="language-switcher">
    <!-- Trigger button placed in the bottom-right dock alongside zoom controls -->
    <button
      type="button"
      class="current-language"
      title="Select Language"
      @click="isOpen = true"
    >
      <img :src="getFlagUrl(locale)" :alt="locale" class="flag-icon" />
      <span>{{ languageNames[locale] || locale }}</span>
      <i class="bi bi-translate ms-1"></i>
    </button>

    <!-- Centered Language Selection Modal Window -->
    <Teleport to="body">
      <transition name="fade">
        <div
          v-if="isOpen"
          class="lang-modal-backdrop"
          @click.self="isOpen = false"
        >
          <div class="lang-modal-window" role="dialog" aria-modal="true" aria-label="Select Language">
            <div class="lang-modal-header">
              <div class="d-flex align-items-center gap-2">
                <i class="bi bi-translate text-info fs-5"></i>
                <h5 class="m-0 fw-semibold">Select Language</h5>
              </div>
              <button
                type="button"
                class="lang-modal-close"
                aria-label="Close"
                @click="isOpen = false"
              >
                <i class="bi bi-x-lg"></i>
              </button>
            </div>

            <div class="lang-modal-grid">
              <button
                v-for="lang in orderedLocales"
                :key="lang"
                type="button"
                :class="['lang-option-card', { active: lang === locale }]"
                @click="selectLanguage(lang)"
              >
                <img :src="getFlagUrl(lang)" :alt="lang" class="flag-icon-lg" />
                <span class="lang-option-name">{{ languageNames[lang] || lang }}</span>
                <i v-if="lang === locale" class="bi bi-check-circle-fill ms-auto active-check"></i>
              </button>
            </div>
          </div>
        </div>
      </transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'

const { locale, availableLocales } = useI18n()
const isOpen = ref(false)

const PREFERRED_ORDER = [
  'english',
  'spanish',
  'portuguese',
  'french',
  'german',
  'italian',
  'dutch',
  'swedish',
  'danish',
  'finnish',
  'greek',
  'turkish',
  'russian',
  'arabic',
  'mandarin',
  'japanese',
  'korean'
]

const orderedLocales = computed(() => {
  const available = new Set(availableLocales)
  const ordered = PREFERRED_ORDER.filter((l) => available.has(l))
  const remaining = availableLocales.filter((l) => !ordered.includes(l))
  return [...ordered, ...remaining]
})

const languageNames = {
  arabic: 'العربية',
  danish: 'Dansk',
  dutch: 'Nederlands',
  english: 'English',
  finnish: 'Suomi',
  french: 'Français',
  german: 'Deutsch',
  greek: 'Ελληνικά',
  italian: 'Italiano',
  japanese: '日本語',
  korean: '한국어',
  mandarin: '中文',
  portuguese: 'Português',
  russian: 'Русский',
  spanish: 'Español',
  swedish: 'Svenska',
  turkish: 'Türkçe'
}

const flagCodes = {
  arabic: 'sa',
  danish: 'dk',
  dutch: 'nl',
  english: 'en',
  finnish: 'fi',
  french: 'fr',
  german: 'de',
  greek: 'gr',
  italian: 'it',
  japanese: 'jp',
  korean: 'kr',
  mandarin: 'cn',
  portuguese: 'pt',
  russian: 'ru',
  spanish: 'es',
  swedish: 'se',
  turkish: 'tr'
}

const flagModules = import.meta.glob('../assets/flags/*.svg', { eager: true, import: 'default' })

function getFlagUrl(lang) {
  const code = flagCodes[lang] || 'en'
  return flagModules[`../assets/flags/${code}.svg`]
}

function selectLanguage(lang) {
  locale.value = lang
  isOpen.value = false
}

function handleKeydown(e) {
  if (e.key === 'Escape' && isOpen.value) {
    isOpen.value = false
  }
}

watch(
  locale,
  (lang) => {
    if (typeof document !== 'undefined') {
      document.documentElement.dir = lang === 'arabic' ? 'rtl' : 'ltr'
    }
  },
  { immediate: true }
)

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.current-language {
  color: #f8fafc;
  cursor: pointer;
  backdrop-filter: blur(16px);
  background-color: rgba(15, 23, 42, 0.88);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 12px;
  align-items: center;
  gap: 0.5rem;
  height: 42px;
  padding: 0 0.9rem;
  font-size: 0.85rem;
  font-weight: 600;
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.45);
  transition: all 0.2s ease;
  display: inline-flex;
}

.current-language:hover {
  border-color: rgba(56, 189, 248, 0.45);
  background-color: rgba(30, 41, 59, 0.95);
  color: #38bdf8;
}

.flag-icon {
  object-fit: cover;
  border-radius: 3px;
  width: 20px;
  height: 15px;
  box-shadow: 0 1px 3px #0006;
}

/* Centered Modal Window */
.lang-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 2000;
  background: rgba(9, 13, 22, 0.72);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

.lang-modal-window {
  width: 100%;
  max-width: 580px;
  background: rgba(15, 23, 42, 0.96);
  border: 1px solid rgba(148, 163, 184, 0.24);
  border-radius: 20px;
  padding: 1.5rem;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.7);
  color: #f8fafc;
}

.lang-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 1rem;
  margin-bottom: 1.1rem;
  border-bottom: 1px solid rgba(148, 163, 184, 0.16);
}

.lang-modal-close {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(30, 41, 59, 0.7);
  color: #cbd5e1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.15s ease;
}

.lang-modal-close:hover {
  background: rgba(248, 113, 113, 0.15);
  border-color: rgba(248, 113, 113, 0.4);
  color: #fca5a5;
}

.lang-modal-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(165px, 1fr));
  gap: 0.6rem;
  max-height: 65vh;
  overflow-y: auto;
}

.lang-option-card {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.65rem 0.85rem;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.16);
  background: rgba(30, 41, 59, 0.6);
  color: #e2e8f0;
  font-size: 0.86rem;
  font-weight: 500;
  cursor: pointer;
  text-align: left;
  transition: all 0.15s ease;
}

.lang-option-card:hover {
  background: rgba(56, 189, 248, 0.14);
  border-color: rgba(56, 189, 248, 0.4);
  color: #fff;
}

.lang-option-card.active {
  background: linear-gradient(135deg, rgba(14, 165, 233, 0.22), rgba(37, 99, 235, 0.25));
  border-color: #38bdf8;
  color: #fff;
  font-weight: 600;
}

.flag-icon-lg {
  object-fit: cover;
  border-radius: 4px;
  width: 24px;
  height: 18px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.35);
  flex-shrink: 0;
}

.active-check {
  color: #38bdf8;
  font-size: 0.95rem;
}
</style>
