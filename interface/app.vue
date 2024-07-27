<template>
  <NuxtLayout >
    <v-app >
      <v-app-bar :elevation="0" style="position: sticky;">
        <template v-slot:prepend>
          <v-app-bar-nav-icon></v-app-bar-nav-icon>
        </template>
        
        <v-app-bar-title>SolarSync management interface</v-app-bar-title>
        <v-checkbox class="pt-3"
          v-model="$vuetify.theme.dark"
          color="purple"
          false-icon="mdi-theme-light-dark"
          true-icon="mdi-theme-light-dark"
          @click="toggleTheme()"
        >
        </v-checkbox>
      
      </v-app-bar>
      <NuxtPage :class="backgroundClass"/>
      
    </v-app>
  </NuxtLayout>
</template>

<script setup>
import { useTheme } from 'vuetify'

const theme = useTheme()

function toggleTheme () {
  theme.global.name.value = theme.global.current.value.dark ? 'light' : 'dark'
}

const currentTime = new Date().getHours();
if (currentTime >= 18 || currentTime < 6) {
  theme.global.name.value = 'dark';
} else {
  theme.global.name.value = 'light';
}

</script>

<style>
  .blue-gradient {
    background: linear-gradient(to bottom, #007bff, #00bfff);
  }

  .black-orange-gradient {
    background: linear-gradient(to bottom, #464343, #ff8c00);
  }
</style>
