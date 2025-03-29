<template>
  <div class="card">
    <DataTable v-model:expandedRows="expandedRows" :value="testsets" dataKey="id"
               @rowExpand="onRowExpand" @rowCollapse="onRowCollapse" tableStyle="min-width: 60rem">
      <Column expander style="width: 5rem" />
      <Column field="id" header="ID"></Column>
      <Column field="name" header="Name"></Column>
      <Column field="model_type" header="Model"></Column>
      <Column field="status" header="Status"></Column>
      <Column field="num_questions" header="Questions"></Column>
      <Column field="agent_description" header="Agent Description"></Column>
      <template #expansion="slotProps">
        <div class="p-4">
          <h5>Details for {{ slotProps.data.name }}</h5>
          <DataTable
              v-if="slotProps.data.questions"
              :value="slotProps.data.questions"
              size="small"
              resizableColumns columnResizeMode="fit"
          >
            <Column field="question" header="Question"></Column>
            <Column field="reference_answer" header="Reference Answer" ></Column>
            <Column field="reference_context" header="Reference Context"></Column>
            <Column field="conversation_history" header="Conversation History"></Column>
            <Column field="metadata" header="Metadata"></Column>
          </DataTable>
        </div>
      </template>
    </DataTable>
    <Toast />
  </div>
</template>

<script setup>
import {onMounted, ref} from 'vue';
import {useToast} from 'primevue/usetoast';
import axios from 'axios';

const testsets = ref([]);
const expandedRows = ref({});
const toast = useToast();

async function fetchTestsets() {
  try {
    const response = await axios.get('http://localhost:9876/testsets');
    testsets.value = response.data;
  } catch (error) {
    console.error('Error fetching testsets:', error);
  }
}

async function fetchTestsetDetails(testsetId) {
  try {
    const response = await axios.get(`http://localhost:9876/testsets/${testsetId}`);
    let questions = JSON.parse(response.data.questions);
    // console.log(questions);

    return convertData(questions);
  } catch (error) {
    console.error('Error fetching testset details:', error);
    return [];
  }
}

const convertData = (data) => {
  return Object.keys(data.question).map((key) => ({
    //[key]: {
    question: data.question[key],
    reference_answer: data.reference_answer[key],
    reference_context: data.reference_context[key].split('\n')[0], // Keeping only the first line as requested
    conversation_history: data.conversation_history[key],
    metadata: data.metadata[key]
    //}
  }));
};

const onRowExpand = async (event) => {
  const testsetId = event.data.id;
  event.data.questions = await fetchTestsetDetails(testsetId);
  // Ensure Vue reactivity updates the table
  testsets.value = [...testsets.value];
  //toast.add({ severity: 'info', summary: 'Testset Expanded', detail: event.data.name, life: 3000 });
};


const expandAll = () => {
  expandedRows.value = testsets.value.reduce((acc, p) => (acc[p.id] = true) && acc, {});
};

const collapseAll = () => {
  expandedRows.value = null;
};

onMounted(async () => {
  await fetchTestsets();
});
</script>

<style scoped>
/* Add your styles here */
</style>