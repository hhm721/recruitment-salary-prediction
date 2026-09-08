import { inject, onMounted, onUnmounted } from 'vue'

const PAGE_TOOLBAR_KEY = Symbol('pageToolbar')

export function providePageToolbar(toolbarRef) {
  return { [PAGE_TOOLBAR_KEY]: toolbarRef }
}

export function usePageToolbar(handlers) {
  const toolbar = inject(PAGE_TOOLBAR_KEY, null)

  onMounted(() => {
    if (toolbar) {
      toolbar.value = handlers
    }
  })

  onUnmounted(() => {
    if (toolbar) {
      toolbar.value = { onSearch: null, onReset: null }
    }
  })
}

export { PAGE_TOOLBAR_KEY }
