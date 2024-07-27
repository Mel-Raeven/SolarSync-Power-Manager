<template>
    <div style="margin: 10px; padding: 5px;">
   <div class="text-right" style="margin: 5px;">
    <v-btn
      :disabled="loading"
      append-icon="mdi-refresh"
      text="Refresh"
      variant="flat"
      color="primary"
      @click="onClick"
    ></v-btn>
  </div>

  <v-data-table :items="items" :loading="loading" :headers="headers" item-value="name" v-model:sort-by="sortBy"
  >
    <template v-slot:loading>
      <v-skeleton-loader type="table-row@10"></v-skeleton-loader>
    </template>
    <template v-slot:item.usage="{ value }">
      <v-chip :color="getColor(value)">
        {{ value }}
      </v-chip>
    </template>
    <template v-slot:item.actions="{ item }">
      <v-icon
        class="me-2"
        size="small"
        @click="editItem(item)"
      >
        mdi-pencil
      </v-icon>
    </template>
  </v-data-table>

  <v-dialog max-width="500" v-model="dialog">
    <v-card :title="'Edit ' + editedItem.name + ' settings'">
    <v-form v-model="valid">
    <v-container>
      <v-row>
        <v-col
        >
        <v-row>
          <v-text-field
            v-model="editedItem.usage"
            label="Usage (Wattage)"
            required
            suffix="W"
            :rules="[() => !!editedItem.usage || 'This field is required']"
            placeholder="100"
          ></v-text-field>
        </v-row>
        <v-row>
          <v-text-field
            v-model="editedItem.priority"
            label="Priority"
            required
            :rules="[() => !!editedItem.priority || 'This field is required']"
            placeholder="1"
          ></v-text-field>
        </v-row>
        </v-col>
        </v-row>
    </v-container>
    </v-form>
    <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn
          text="Save"
          @click="this.dialog = false"
          :disabled="!editedItem.usage || !editedItem.priority"
          variant="elevated"
          color="primary"

        ></v-btn>
        <v-btn
          text="Close"
          @click="this.dialog = false"
        ></v-btn>
      </v-card-actions>
</v-card>
  </v-dialog>
</div>
</template>  

  <script>
  export default {
    data() {
      return {
        dialog: false,
        editedItem: {},
        loading: true,
        selected: [],
        sortBy: [{ key: 'priority', order: 'asc' }],
        headers: [
          { title: 'Name', key: 'name', sortable: false },
          { title: 'Type', key: 'type', sortable: false },
          {title: 'Priority', key: 'priority', sortable: true},
          {title: 'Usage (Wattage)', key: 'usage', sortable: true},
          { title: 'Edit', key: 'actions', sortable: false },
        ],
        items: [],
      };
    },
    methods: {
      onClick () {
        this.loading = true
        fetch('http://127.0.0.1:5000/added_plugs')
        .then(response => response.json())
        .then(data => {
            console.log(data)
          this.items = data.plugs;
          this.loading = false;
          console.log('Plugs:', this.items);
        })
        .catch(error => {
          console.error('Error fetching plugs:', error);
        });
        
      },
      checkIfSelected() {
        console.log(this.selected)
      },
      editItem(item) {
        this.dialog = true
        this.editedItem = item
      },
      getColor (usageNumber) {
        if (usageNumber > 1000) return 'red'
        else if (usageNumber > 500) return 'orange'
        else return 'green'
      },
    },
    mounted() {
      fetch('http://127.0.0.1:5000/added_plugs')
        .then(response => response.json())
        .then(data => {
            console.log(data)
          this.items = data.plugs;
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