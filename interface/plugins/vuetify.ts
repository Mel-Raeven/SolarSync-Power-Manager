// import this after install `@mdi/font` package
import '@mdi/font/css/materialdesignicons.css'

import 'vuetify/styles'
import { createVuetify, type ThemeDefinition } from 'vuetify'

const light: ThemeDefinition = {
  dark: false,
  colors: {
    background: '#f7f7f7',
    primary: '#5c6e58'
  
  },
}

const dark: ThemeDefinition = {
  dark: true,
  colors: {
    background: '#1d2228',
    primary: '#fb8122',
    color: '#e1e2e2'
  },
}

export default defineNuxtPlugin((app) => {
  const vuetify = createVuetify({
    theme: {
      defaultTheme: 'light',
      themes: {
        light,
        dark,
      },
    },
  })
  app.vueApp.use(vuetify)
})
