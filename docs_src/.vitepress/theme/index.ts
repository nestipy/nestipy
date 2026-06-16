import DefaultTheme from 'vitepress/theme'
import HomeLanding from './components/HomeLanding.vue'
import './custom.css'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('HomeLanding', HomeLanding)
  }
}
