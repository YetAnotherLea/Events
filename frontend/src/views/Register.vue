<template>
    <div class="register-container">
        <h3>Inscription</h3>
        <p><input type="text" placeholder="Pseudo" v-model="pseudo" /></p>
        <p><input type="text" placeholder="Email" v-model="email" /></p>
        <p><input type="password" placeholder="Mot de passe" v-model="password" /></p>
        <p v-if="errMsg" style="color: red;">{{ errMsg }}</p>
        <p><button @click="register">Envoyer</button></p>
        <hr/>
        <p><button @click="signInWithGoogle"><img src="../assets/google.png"/> Google</button></p>
        <p><button @click="signInWithFacebook"><img src="../assets/facebook.png"/> Facebook</button></p>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { syncUserWithBackend, getCurrentUserInfo } from '../components/Auth'
import { getAuth, createUserWithEmailAndPassword, GoogleAuthProvider, FacebookAuthProvider, signInWithPopup } from "firebase/auth"

const router = useRouter()
const pseudo = ref("")
const email = ref("")
const password = ref("")
const errMsg = ref("")

const register = () => {
    if (!pseudo.value.trim()) {
        errMsg.value = "Le pseudo est obligatoire"
        return
    }

    createUserWithEmailAndPassword(getAuth(), email.value, password.value)
    .then((data) => {
        return syncUserWithBackend(pseudo.value.trim())
    })
    .then(() => {
        alert("Bienvenue !")
        router.push(`/profile/${pseudo.value.trim()}`)
    })
    .catch((error) => {
        if (error.message.includes("PSEUDO_TAKEN")) {
            errMsg.value = "Ce pseudo est déjà utilisé"
        } else {
            errMsg.value = error.message
        }
    })
}

const signInWithGoogle = () => {
    const provider = new GoogleAuthProvider()
    provider.addScope('profile')
    provider.addScope('email')
    
    signInWithPopup(getAuth(), provider)
    .then((result) => {
        return syncUserWithBackend()
    })
    .then(() => {
        return getCurrentUserInfo()
    })
    .then((userInfo) => {
        alert("Bienvenue !")
        router.push(`/profile/${userInfo.pseudo}`)
    })
    .catch((error) => {
        console.error("Erreur Google:", error)
        errMsg.value = error.message
    })
}

const signInWithFacebook = () => {
    const provider = new FacebookAuthProvider()
    provider.addScope('email')
    provider.addScope('public_profile')
    
    signInWithPopup(getAuth(), provider)
    .then((result) => {
        return syncUserWithBackend()
    })
    .then(() => {
        return getCurrentUserInfo()
    })
    .then((userInfo) => {
        alert("Bienvenue !")
        router.push(`/profile/${userInfo.pseudo}`)
    })
    .catch((error) => {
        console.error("Erreur Facebook:", error)
        errMsg.value = error.message
    })
}
</script>

<style scoped>
.register-container {
  max-width: 400px;
  margin: 0 auto;
  padding: 30px 25px;
  background-color: #ffffff;
  border-radius: 2px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
  font-family: 'Roboto', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

h3 {
  font-size: 1.8rem;
  font-weight: 700;
  color: #1e3a8a;
  text-align: center;
  margin-bottom: 25px;
}

p {
  margin: 0 0 15px 0;
}

input[type="text"], 
input[type="password"] {
  width: 100%;
  padding: 12px 15px;
  border: 1px solid #d1d5db;
  border-radius: 2px;
  font-size: 1rem;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
}

input[type="text"]:focus, 
input[type="password"]:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

button {
  width: 100%;
  padding: 12px 15px;
  border: none;
  border-radius: 2px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

button:first-of-type {
  background-color: #6366f1;
  color: white;
}

button:first-of-type:hover {
  background-color: #4f46e5;
  transform: translateY(-1px);
}

button:nth-of-type(2), 
button:nth-of-type(3) {
  background-color: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

button:nth-of-type(2):hover, 
button:nth-of-type(3):hover {
  background-color: #e5e7eb;
  transform: translateY(-1px);
}

img {
  width: 1rem;
  height: 1rem;
}

.error-message {
  color: #dc2626 !important;
  font-size: 0.9rem;
  text-align: center;
  background-color: #fee2e2;
  padding: 8px 12px;
  border-radius: 2px;
  border: 1px solid #fca5a5;
}

hr {
  margin: 20px 0;
  border: none;
  height: 1px;
  background-color: #e5e7eb;
}
</style>