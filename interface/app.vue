<template>
  <NuxtLayout >
    <v-app >
      <v-app-bar :elevation="1" style="position: sticky;">
        <template v-slot:prepend>
          <v-app-bar-nav-icon></v-app-bar-nav-icon>
        </template>
        <v-app-bar-title>Application Bar</v-app-bar-title>
      </v-app-bar>
      <NuxtPage :class="backgroundClass"/>
    </v-app>
  </NuxtLayout>
</template>

<script>
export default {
  computed: {
    backgroundClass() {
      const currentTime = new Date().getHours();
      if (currentTime >= 18 || currentTime < 6) {
        return 'black-orange-gradient';
      } else {
        return 'blue-gradient';
      }
    }
  }
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
