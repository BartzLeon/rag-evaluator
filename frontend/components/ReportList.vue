<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

const ratings = ref([]);
const models = ref([]);
const model = ref(null);
const createReportVisible = ref(false);

async function fetchRatings() {
  try {
    const response = await axios.get('http://localhost:9876/ratings/');
    ratings.value = response.data;
  } catch (error) {
    console.error('Error fetching ratings:', error);
  }
}

async function createReport() {
  try {
    const response = await axios.post('http://localhost:9876/ratings/');
    ratings.value = response.data;
  } catch (error) {
    console.error('Error fetching ratings:', error);
  }
}

async function fetchModels() {
  try {
    const response = await axios.get('http://localhost:9876/models/');
    response.data = response.data.map((model: string) => ({ name: model }));
    console.log(response.data);
    models.value = response.data;
  } catch (error) {
    console.error('Error fetching models:', error);
  }
}

const getSeverity = (value:any) => {
  value = value * 100;
  if (value >= 90) return 'success';
  if (value >= 70) return 'info';
  if (value >= 50) return 'warn';
  if (value >= 30) return 'error';
  return 'secondary';
};

onMounted(async () => {
  await fetchRatings();
  await fetchModels();
});
</script>

<template>
    <DataTable :value="ratings" tableStyle="min-width: 50rem">
      <template #header>
        <div class="flex flex-wrap items-center justify-between gap-2">
          <span class="text-xl font-bold">Reports</span>
          <Button raised @click="createReportVisible = true">
            Request Report
          </Button>
        </div>
      </template>
      <Column field="id" header="ID"></Column>
      <Column field="score" header="Score">
        <template #body="slotProps">
          <!--<p style="color: red">{{ slotProps.data.scores }}</p>-->
          <div v-for="[key, value] in Object.entries(JSON.parse(slotProps.data.scores).score)" :key="key">
            <Message variant="outlined" style="margin: 10px;" size="small" :severity="getSeverity(value)">{{ key.toLowerCase() }}: {{ value }}</Message>
          </div>
        </template>
      </Column>
      <Column field="model_type" header="Model"></Column>
      <Column field="status" header="Status">
        <template #body="slotProps">
          <Message :value="slotProps.data.status" v-if="slotProps.data.status === 'Completed'" :severity="slotProps.data.status === 'Completed' ? 'success' : 'error'" variant="outlined" size="small">
            {{ slotProps.data.status }}
          </Message>
          <ProgressBar v-else mode="indeterminate" style="height: 6px"></ProgressBar>
        </template>
      </Column>
      <Column field="report_path" header="Report">
        <template #body="slotProps">
          <a :href="'file:///Users/leonbartz/private/ele/rest-example/JupyterProject/' + slotProps.data.report_path + 'report.html'" target="_blank">View Report</a>
        </template>
      </Column>
      <Column field="knowledge_base_score" header="knowledge_base_score"></Column>
    </DataTable>

  <Dialog v-model:visible="createReportVisible" modal header="Edit Profile" :style="{ width: '25rem' }">
    <span class="text-surface-500 dark:text-surface-400 block mb-8">Request the creation of a report.</span>
    <div class="flex items-center gap-4 mb-4">
      <label for="username" class="font-semibold w-24">Model Name</label>
      <Select id="model" option-label="name" v-model="model" :options="models" placeholder="Select a City" class="w-full md:w-56" />
    </div>
    <div class="flex items-center gap-4 mb-8">
      <label for="email" class="font-semibold w-24">Testset</label>
      <InputText id="email" class="flex-auto" autocomplete="off" />
    </div>
    <div class="flex justify-end gap-2">
      <Button type="button" label="Cancel" severity="secondary" @click="visible = false"></Button>
      <Button type="button" label="Save" @click="visible = false"></Button>
    </div>
  </Dialog>
</template>

<style scoped>
/* Add your styles here */
</style>