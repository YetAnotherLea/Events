<template>
  <div class="event-card">
    <h2 class="event-title">{{ event.title_fr }}</h2>

    <p v-if="event.location_city">
      <span class="label">Ville:</span>
      <span class="value">{{ event.location_city }}</span>
    </p>
    <p v-if="event.daterange_fr">
      <span class="label">Date:</span>
      <span class="value">{{ event.daterange_fr }}</span>
    </p>
    <p v-if="event.category">
      <span class="label">Catégorie:</span>
      <span class="value">{{ event.category }}</span>
    </p>

    <!-- Description avec sauts de ligne et listes -->
    <div v-if="event.description_fr" class="description" v-html="formatDescription(event.description_fr)"></div>

    <div v-if="event.keywords_fr" class="keywords">
      <span v-for="k in event.keywords_fr.split(';')" :key="k" class="badge">{{ k }}</span>
    </div>

    <router-link :to="`/event/${event.uid}`" class="details-link">Voir détails</router-link>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { sanitizeHtml } from "../utils/sanitize";

const props = defineProps({
  event: Object
});


const formatDescription = (text) => {
  if (!text) return '';
  
  return sanitizeHtml(
    text
      .replace(/\n/g, '<br>')
      .replace(/•\s*(.+)/g, '<li>$1</li>')
      .replace(/(<li>.+<\/li>)/g, '<ul>$1</ul>')
  );
};
</script>

<style scoped>
.event-card {
  background-color: #f0f4ff;
  padding: 1.5rem 2rem;
  border-radius: 16px;
  box-shadow: 0 6px 18px rgba(0,0,0,0.12);
  transition: transform 0.2s, box-shadow 0.2s;
}
.event-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0,0,0,0.18);
}

.event-title {
  font-size: 1.6rem;
  font-weight: 700;
  color: #1e3a8a;
  margin-bottom: 10px;
}

.event-card p {
  margin: 6px 0;
  font-size: 1rem;
  line-height: 1.5;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
}
.event-card .label {
  width: 90px;
  color: #111827;
  font-weight: 600;
  margin-right: 6px;
}
.event-card .value {
  flex: 1;
}


.description {
  margin: 10px 0 15px;
  padding: 12px 16px;
  background-color: #eaf0ff;
  border-radius: 12px;
  line-height: 1.6;
  color: #374151;
}
.description ul {
  margin: 8px 0 8px 20px;
  padding: 0;
}
.description li {
  margin-bottom: 4px;
}


.keywords {
  margin: 10px 0;
}
.badge {
  display: inline-block;
  background-color: #4f46e5;
  color: #fff;
  padding: 0.25rem 0.65rem;
  margin: 0.2rem 0.2rem 0.2rem 0;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
}


.details-link {
  margin-top: 10px;
  padding: 6px 12px;
  background-color: #6366f1;
  color: #fff;
  text-decoration: none !important;
  border-radius: 8px;
  font-weight: 600;
  transition: all 0.2s ease;
  display: inline-block;
}
.details-link:hover {
  background-color: #4f46e5;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
</style>
