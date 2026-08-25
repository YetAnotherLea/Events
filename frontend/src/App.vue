<template>
  <div id="app">
    <nav>
      <router-link to="/" title="Accueil"><img src="./assets/logos/eventalis.png" alt="Eventalis" /></router-link>
      <router-link to="/register" title="Inscription" v-if="!isLoggedIn">Inscription</router-link>
      <router-link to="/signin" title="Connexion" v-if="!isLoggedIn">Connexion</router-link>
      <router-link :to="`/profile/${userPseudo}`" title="Profil" v-if="isLoggedIn">
        Mon Profil
      </router-link>
      <button @click="handleSignOut" title="Déconnexion" v-if="isLoggedIn">Déconnexion</button>
    </nav>
    <router-view />
  </div>
</template>

<style>
nav {
  display: flex;
  align-items: center;
  margin-bottom: 3rem;
  margin: 0 auto;
  height: 3rem;

  padding-left: 1rem;
  padding-bottom: 0.8rem;
}

nav a {
  padding-right: 1rem;
  color: white;
  text-decoration: none;
}

nav img {
  height: 2rem;
  width: 2rem;
}

nav button {
  color: white;
  padding: 0.5rem 0.8rem;
  background-color: #5A4CBF;
  border: 1px solid #5A4CBF;
  font-size: 1rem;
  transition: all 0.2s;
}

nav button:hover {
  border: 1px white solid;
  border-radius: 2px;
}



</style>

<script setup>
  import { onMounted, ref } from 'vue';
  import { getAuth, onAuthStateChanged, signOut } from "firebase/auth"
  import { useRouter } from 'vue-router';
  const API_URL = import.meta.env.VITE_API_URL;


  const router = useRouter()
  const isLoggedIn = ref(false)
  const userPseudo = ref('')

  let auth
  onMounted(() => {
    auth = getAuth()
    onAuthStateChanged(auth, async (user) => {
      if (user) {
        isLoggedIn.value = true
        await getUserPseudo()
      } else {
        isLoggedIn.value = false
        userPseudo.value = ''
      }
    })
  })

  const getUserPseudo = async () => {
    try {
      const token = await auth.currentUser.getIdToken()
      const response = await fetch(`${API_URL}/api/users/me`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const userData = await response.json()
        userPseudo.value = userData.pseudo
      }
    } catch (err) {
      console.error('Erreur récupération pseudo:', err)
    }
  }

  const handleSignOut = () => {
    signOut(auth).then(() => {
      router.push("/")
    })
  }
</script>