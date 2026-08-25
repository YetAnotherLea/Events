<template>
  <div class="event-detail">
    <button @click="$router.back()" class="back-button">← Retour</button>

    <p v-if="loading" class="loading">Chargement...</p>
    <p v-if="error" class="error">{{ error }}</p>

    <div v-if="event" class="event-card">
      <h1>{{ event.title_fr }}</h1>

      
      <div class="event-info">
        <p v-if="event.daterange_fr"><span class="label">Date:</span> {{ event.daterange_fr }}</p>
        <p v-if="event.location_name"><span class="label">Lieu:</span> {{ event.location_name }}</p>
        <p v-if="event.location_address"><span class="label">Adresse:</span> {{ event.location_address }}</p>
        <p v-if="event.location_city"><span class="label">Ville:</span> {{ event.location_city }}</p>
        <p v-if="event.category"><span class="label">Catégorie:</span> {{ event.category }}</p>
      </div>

      
      <div v-if="event.keywords_fr" class="keywords">
        <span v-for="k in event.keywords_fr.split(';')" :key="k" class="badge">{{ k.trim() }}</span>
      </div>

     
      <div v-if="event.description_fr" class="description">
        {{ event.description_fr }}
      </div>

      
      <div v-if="event.longdescription_fr" class="long-description" v-html="formatLongDescription(event.longdescription_fr)"></div>

      
      <a v-if="event.canonicalurl" :href="event.canonicalurl" target="_blank" rel="noopener" class="external-link">
        Voir sur OpenAgenda →
      </a>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import axios from "axios";

export default {
  name: "EventDetail",
  setup() {
    const route = useRoute();
    const event = ref(null);
    const loading = ref(true);
    const error = ref("");

    const fetchEvent = async () => {
      loading.value = true;
      error.value = "";
      try {
        const uid = route.params.uid;
        const host = window.location.hostname;
        const port = 5000;
        const res = await axios.get(`http://${host}:${port}/api/events/${uid}`);
        if (res.data) {
          event.value = res.data;
        } else {
          error.value = "Événement introuvable.";
        }
      } catch (err) {
        console.error(err);
        error.value = "Erreur de chargement : " + (err.response?.data?.error || err.message);
      } finally {
        loading.value = false;
      }
    };

    onMounted(fetchEvent);

    
    const formatLongDescription = (text) => {
      if (!text) return "";
      return text
        .replace(/\r\n|\r|\n/g, "<br>")
        .replace(/TRALALA\s+LOVERS/g, "TRALALA LOVERS"); 
    };

    return { event, loading, error, formatLongDescription };
  }
};
</script>

<style scoped>
/*  */
</style>
