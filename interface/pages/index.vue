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

  <v-data-table     v-model="selected" :items="items" :loading="loading" :headers="headers"     item-value="name" show-select     return-object>
    <template v-slot:loading>
      <v-skeleton-loader type="table-row@10"></v-skeleton-loader>
    </template>
  </v-data-table>

  <v-btn @click="checkIfSelected()"></v-btn>
</div>
</template>  

  <script>
  export default {
    data() {
      return {
        loading: true,
        selected: [],
        headers: [
          { title: 'Name', key: 'name', sortable: true },
          { title: 'Type', key: 'type', sortable: true },
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
      checkIfSelected() {
        const updatedSelected = this.selected.map(item => ({
          ...item,
          priority: 0,
          usage: 0
        }));

        fetch('http://127.0.0.1:5000/add_plugs', {
          method: 'POST',
          headers: {
        'Content-Type': 'application/json'
          },
          body: JSON.stringify(updatedSelected)
        })
        .then(response => response.json())
        .then(data => {
          console.log('Selection submitted:', data);
        })
        .catch(error => {
          console.error('Error submitting selection:', error);
        });
      }
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

  ::v-deep .v-data-table-header__content span { 
    font-weight: bold !important;
  }
  </style>