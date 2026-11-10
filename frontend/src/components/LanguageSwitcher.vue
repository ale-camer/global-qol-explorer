<template>
  <div class="language-switcher" ref="switcherRef">
    <button class="current-language" @click="isOpen = !isOpen">
      <img :src="getFlagUrl(locale)" :alt="locale" class="flag-icon" />
      <span>{{ languageNames[locale] || locale }}</span>
      <i class="bi bi-caret-down-fill"></i>
    </button>
    <transition name="fade-slide-down">
      <ul v-if="isOpen" class="language-list">
        <li
          v-for="lang in availableLocales"
          :key="lang"
          @click="selectLanguage(lang)"
        >
          <img :src="getFlagUrl(lang)" :alt="lang" class="flag-icon" />
          <span>{{ languageNames[lang] || lang }}</span>
        </li>
      </ul>
    </transition>
  </div>
</template>

<script setup>
import { ref, watch, onBeforeUnmount } from 'vue'
import { useI18n } from 'vue-i18n'

const { locale, availableLocales } = useI18n()
const isOpen = ref(false)
const switcherRef = ref(null)

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

const handleClickOutside = (e) => {
  if (switcherRef.value && !switcherRef.value.contains(e.target)) {
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

watch(isOpen, (val) => {
  if (val) {
    document.addEventListener('click', handleClickOutside)
  } else {
    document.removeEventListener('click', handleClickOutside)
  }
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.language-switcher {
  z-index: 11;
  position: absolute;
  top: 1.25rem;
  right: 1.5rem;
}
.current-language {
  color: #f8fafc;
  cursor: pointer;
  backdrop-filter: blur(16px);
  background-color: rgba(15, 23, 42, 0.86);
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 999px;
  align-items: center;
  gap: 0.5rem;
  padding: 0.45rem 0.9rem;
  font-size: 0.85rem;
  font-weight: 500;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  transition: all 0.2s ease;
  display: flex;
}
.current-language:hover {
  border-color: rgba(56, 189, 248, 0.45);
  background-color: rgba(30, 41, 59, 0.92);
}
.flag-icon {
  object-fit: cover;
  border-radius: 3px;
  width: 20px;
  height: 15px;
  box-shadow: 0 1px 3px #0006;
}
.current-language i {
  opacity: 0.7;
  font-size: 0.65rem;
}
.language-list {
  backdrop-filter: blur(16px);
  background-color: rgba(15, 23, 42, 0.95);
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 14px;
  width: max-content;
  max-height: 70vh;
  margin: 0;
  padding: 0.4rem;
  list-style: none;
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  overflow-y: auto;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6);
}
.language-list li {
  color: #e2e8f0;
  cursor: pointer;
  align-items: center;
  gap: 0.65rem;
  padding: 0.45rem 0.85rem;
  border-radius: 8px;
  font-size: 0.85rem;
  transition: background-color 0.15s ease, color 0.15s ease;
  display: flex;
}
.language-list li:hover {
  background-color: rgba(56, 189, 248, 0.15);
  color: #38bdf8;
}
.fade-slide-down-enter-active,
.fade-slide-down-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}
.fade-slide-down-enter-from,
.fade-slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
@media (max-width: 768px) {
  .language-switcher {
    top: 0.5rem;
    right: 0.5rem;
  }
  .current-language {
    gap: 0.4rem;
    padding: 0.25rem 0.6rem;
    font-size: 0.85rem;
  }
  .flag-icon {
    width: 18px;
    height: 13px;
  }
  .language-list li {
    gap: 0.6rem;
    padding: 0.4rem 0.8rem;
    font-size: 0.9rem;
  }
}
</style>
