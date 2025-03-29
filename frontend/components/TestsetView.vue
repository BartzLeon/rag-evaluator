<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

const testset = ref([]);

async function fetchTestset() {
  try {
    const response = await axios.get('http://localhost:9876/testsets/1');
    let questions = JSON.parse(response.data.questions);
    let parsedQuestions = convertData(questions);
    console.log(parsedQuestions);
    response.data.questions = parsedQuestions;
    testset.value = response.data;
  } catch (error) {
    console.error('Error fetching ratings:', error);
  }
}

const convertData = (data: any) => {
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

//const transformedData = convertData(inputData);

//console.log(JSON.stringify(transformedData, null, 2));

onMounted(async () => {
  await fetchTestset();
});
</script>

<template>
  <div>
    <DataTable v-if="testset.questions" :value="testset.questions">
      <Column field="question" header="question"></Column>
      <Column field="reference_answer" header="reference_answer"></Column>
      <Column field="reference_context" header="reference_context"></Column>
      <Column field="conversation_history" header="conversation_history"></Column>
      <Column field="metadata" header="metadata"></Column>

    </DataTable>

  </div>
</template>

<style scoped>
/* Add your styles here */
</style>