<template>
  <div class="home">
    
    <h1>Événements à venir</h1>

    <!-- Formulaire de recherche -->
    <form @submit.prevent="fetchEvents" class="search-form">
      <input v-model="city" placeholder="Ville" />
      <input v-model="keyword" placeholder="Mot-clé ou type" />
      <input v-model="year" placeholder="Année (ex: 2025)" /> <!-- nouveau champ -->
      <button type="submit"><img src="../assets/loop.svg"/></button>      <button type="button" @click="showAdvanced = !showAdvanced" class="toggle-advanced">
        {{ showAdvanced ? '−' : '+' }}
      </button>

      <!-- Filtres avancés -->
      <div v-if="showAdvanced" class="advanced-filters">
        <input v-model="category" placeholder="Catégorie" />
        <input v-model="locationName" placeholder="Nom lieu" />
        <input v-model="address" placeholder="Adresse" />
        <input v-model="district" placeholder="Quartier" />
        <input v-model="postalcode" placeholder="CP" />
        <input v-model="department" placeholder="Département" />
        <input v-model="region" placeholder="Région" />
        <input v-model="country" placeholder="Pays" />
      </div>
    </form>

    <!-- Pagination controls -->
    <div class="pagination-controls" v-if="filteredEvents.length > 0">
      <label>
        Événements par page :
        <select v-model.number="itemsPerPage">
          <option v-for="n in [5,10,15,20]" :key="n" :value="n">{{ n }}</option>
        </select>
      </label>
    </div>

    <!-- Messages de chargement / absence -->
    <p v-if="loading" class="loading">Chargement...</p>
    <p v-if="!loading && filteredEvents.length === 0" class="no-events">Aucun événement trouvé.</p>

    <!-- Liste des événements -->
    <div class="events-list">
      <div v-for="event in paginatedEvents" :key="event.uid" class="event-card">
        <h2 class="event-title">{{ event.title_fr }}</h2>
        <p v-if="event.location_name"><strong>Lieu:</strong> {{ event.location_name }}</p>
        <p v-if="event.location_address"><strong>Adresse:</strong> {{ event.location_address }}</p>
        <p v-if="event.location_city"><strong>Ville:</strong> {{ event.location_city }}</p>
        <p v-if="event.daterange_fr"><strong>Date:</strong> {{ event.daterange_fr }}</p>
        <p v-if="event.category"><strong>Catégorie:</strong> {{ event.category }}</p>
        <div v-if="event.keywords_fr" class="keywords">
          <span v-for="k in (Array.isArray(event.keywords_fr) ? event.keywords_fr : event.keywords_fr.split(';'))" :key="k" class="badge">{{ k }}</span>
        </div>
        <p v-if="event.description_fr" class="description">{{ event.description_fr }}</p>

        <router-link :to="`/event/${event.uid}`" class="details-link">Voir détails</router-link>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination" v-if="totalPages > 1">
      <button @click="goToPage(currentPage - 1)" :disabled="currentPage === 1">Précédent</button>
      <span>Page {{ currentPage }} / {{ totalPages }}</span>
      <button @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages">Suivant</button>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getAuth, onAuthStateChanged, signOut } from 'firebase/auth'
import axios from "axios";

export default {
  name: "Home",
  setup() {
    const router = useRouter()
    const API_URL = import.meta.env.VITE_API_URL
    
    const events = ref([])
    const city = ref('')
    const keyword = ref('')
    const year = ref('') // nouveau
    const category = ref('')
    const locationName = ref('')
    const address = ref('')
    const district = ref('')
    const postalcode = ref('')
    const department = ref('')
    const region = ref('')
    const country = ref('')
    const loading = ref(false)
    const showAdvanced = ref(false)
    const currentUser = ref(null)

    const currentPage = ref(1)
    const itemsPerPage = ref(10)

    // Récupération des événements depuis le backend
    const fetchEvents = async () => {
      loading.value = true
      try {
        const params = {}
        if (city.value) params.city = city.value
        if (year.value) params.year = year.value
        const res = await axios.get(`${API_URL}/api/events`, { params })
        events.value = res.data
        currentPage.value = 1
      } catch (err) {
        console.error("Erreur:", err)
      }
      loading.value = false
    }

    // Récupération de l'utilisateur connecté
    const fetchCurrentUser = async () => {
      const auth = getAuth()
      const user = auth.currentUser
      if (user) {
        try {
          const token = await user.getIdToken()
          const response = await fetch(`${API_URL}/api/users/me`, {
            headers: { 'Authorization': `Bearer ${token}` }
          })
          if (response.ok) currentUser.value = await response.json()
        } catch (error) {
          console.error('Erreur lors de la récupération du profil:', error)
        }
      }
    }

    const logout = async () => {
      try {
        await signOut(getAuth())
        currentUser.value = null
        router.push('/')
      } catch (error) {
        console.error('Erreur lors de la déconnexion:', error)
      }
    }

    // Filtrage côté front, incluant l'année
    const filteredEvents = computed(() => {
      const check = (val, field) => !val || (field && field.toLowerCase().includes(val.toLowerCase()))
      return events.value.filter(event => (
        check(city.value, event.location_city) &&
        check(keyword.value, (event.category || "") + " " + (event.keywords_fr || "") + " " + (event.title_fr || "")) &&
        check(category.value, event.category) &&
        check(locationName.value, event.location_name) &&
        check(address.value, event.location_address) &&
        check(district.value, event.location_district) &&
        check(postalcode.value, event.location_postalcode) &&
        check(department.value, event.location_department) &&
        check(region.value, event.location_region) &&
        check(country.value, event.location_countrycode) &&
        (!year.value || (event.firstdate_begin && event.firstdate_begin.startsWith(year.value))) // filtrage année
      ))
    })

    // Pagination
    const totalPages = computed(() => Math.ceil(filteredEvents.value.length / itemsPerPage.value))
    const paginatedEvents = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage.value
      return filteredEvents.value.slice(start, start + itemsPerPage.value)
    })
    const goToPage = page => {
      if (page >= 1 && page <= totalPages.value) currentPage.value = page
    }

    watch(itemsPerPage, () => currentPage.value = 1)

    onMounted(() => {
      fetchEvents()
      const auth = getAuth()
      onAuthStateChanged(auth, (user) => {
        if (user) fetchCurrentUser()
        else currentUser.value = null
      })
    })

    return {
      events, city, keyword, year, category, locationName, address, district,
      postalcode, department, region, country, loading, fetchEvents,
      filteredEvents, paginatedEvents, currentPage, totalPages, goToPage,
      showAdvanced, itemsPerPage, currentUser, logout
    }
  }
}
</script>

