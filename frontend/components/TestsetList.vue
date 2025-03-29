<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

const ratings = ref([]);

async function fetchTestset() {
  try {
    const response = await axios.get('http://localhost:9876/testsets/');
    ratings.value = response.data;
  } catch (error) {
    console.error('Error fetching ratings:', error);
  }
}

onMounted(async () => {
  await fetchTestset();
});
</script>

<template>
  <div>
    <DataTable :value="ratings" tableStyle="min-width: 50rem">
      <Column field="id" header="ID"></Column>
      <Column field="name" header="Name"></Column>
      <Column field="model_type" header="Model"></Column>
      <Column field="status" header="Status"></Column>
      <Column field="num_questions" header="Questions"></Column>
      <Column field="agent_description" header="Agent Description"></Column>
    </DataTable>


    <!--<div v-for="rating in ratings" :key="rating.id">
      {{ rating }}
    </div>-->
  </div>
</template>

<style scoped>
/* Add your styles here */
</style>