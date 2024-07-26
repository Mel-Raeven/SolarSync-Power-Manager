<template>
    <div style="margin: 10px; padding: 5px; background-color: beige; border-radius: 10px;">
   <div class="text-center">
    <v-btn
      :disabled="loading"
      append-icon="mdi-refresh"
      text="Refresh"
      variant="outlined"
      @click="onClick"
    ></v-btn>
  </div>

  <v-data-table :items="items" :loading="loading">
    <template v-slot:loading>
      <v-skeleton-loader type="table-row@10"></v-skeleton-loader>
    </template>
  </v-data-table>
</div>
</template>  

  <script>
  export default {
    data() {
      return {
        loading: true,
        headers: [
          { text: 'Name', value: 'name' },
          { text: 'Type', value: 'type' },
        ],
        items: [],
      };
    },
    methods: {
      onClick () {
        this.loading = true
        fetch('http://127.0.0.1:5000/refresh_plugs')
        .then(response => response.json())
        .then(data => {
          this.items = JSON.parse(data.plugs);
          this.loading = false;
          console.log('Plugs:', this.items);
        })
        .catch(error => {
          console.error('Error fetching plugs:', error);
        });
        
      },
    },
    mounted() {
      fetch('http://127.0.0.1:5000/list_plugs')
        .then(response => response.json())
        .then(data => {
          this.items = JSON.parse(data.plugs);
          this.loading = false;
          console.log('Plugs:', this.items);
        })
        .catch(error => {
          console.error('Error fetching plugs:', error);
        });
    },
  };
  </script>
  
  <style scoped>
  h1 {
    color: blue;
  }
  </style>