<template>
  <Card style="margin: 50px;">
    <template #content>
      <ReportList/>
    </template>
  </Card>

  <Card style="margin: 50px;">
    <template #title>Documents</template>
    <template #content>
      <DocumentList/>
    </template>
  </Card>

  <Card style="margin: 50px;">
    <template #title>Testset</template>
    <template #content>
      <TestsetDetailList/>
    </template>
  </Card>
</template>
<script setup lang="ts">
import TestsetView from "~/components/TestsetView.vue";
</script>