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
import { ref, watch } from 'vue'
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

watch(isOpen, (val) => {
  if (val) {
    document.addEventListener('click', handleClickOutside)
  } else {
    document.removeEventListener('click', handleClickOutside)
  }
})
</script>

<style scoped>
.language-switcher {
  z-index: 11;
  position: absolute;
  top: 1rem;
  right: 1rem;
}
.current-language {
  color: #fff;
  cursor: pointer;
  backdrop-filter: blur(5px);
  background-color: #ffffff1a;
  border: 1px solid #fff3;
  border-radius: 50px;
  align-items: center;
  gap: 0.5rem;
  padding: 0.3rem 0.8rem;
  font-size: 1rem;
  transition: background-color 0.2s;
  display: flex;
}
.current-language:hover {
  background-color: #fff3;
}
.flag-icon {
  object-fit: cover;
  border-radius: 3px;
  width: 25px;
  height: 20px;
  box-shadow: 0 1px 3px #0003;
}
.current-language i {
  opacity: 0.8;
  font-size: 0.7rem;
}
.language-list {
  backdrop-filter: blur(10px);
  background-color: #1e1e1ecc;
  border: 1px solid #fff3;
  border-radius: 12px;
  width: max-content;
  max-height: 800px;
  margin: 0;
  padding: 0.5rem 0;
  list-style: none;
  position: absolute;
  top: calc(100% + 5px);
  right: 0;
  overflow-y: auto;
  box-shadow: 0 4px 20px #0000004d;
}
.language-list li {
  color: #fff;
  cursor: pointer;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  transition: background-color 0.2s;
  display: flex;
}
.language-list li:hover {
  background-color: #ffffff1a;
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
