<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

const ratings = ref([]);

async function fetchDocuments() {
  try {
    const response = await axios.get('http://localhost:9876/documents/');
    ratings.value = response.data;
  } catch (error) {
    console.error('Error fetching ratings:', error);
  }
}

onMounted(async () => {
  await fetchDocuments();
});
</script>

<template>
  <div>
    <DataTable :value="ratings" tableStyle="min-width: 50rem">
      <Column field="id" header="ID"></Column>
      <Column field="name" header="Name"></Column>
      <Column field="status" header="Status"></Column>
      <Column field="saved_to_chroma" header="Questions"></Column>
    </DataTable>


    <!--<div v-for="rating in ratings" :key="rating.id">
      {{ rating }}
    </div>-->
  </div>
</template>

<style scoped>
/* Add your styles here */
</style>