<template>
  <div class="profile-container">
    <div v-if="loading" class="loading">Chargement...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else>
        <h3>Profil de {{ profile.pseudo }}</h3>
        
        <div class="avatar-section">
            <img :src="getAvatarUrl()" 
                :alt="profile.pseudo" />
            
            <div v-if="profile.is_own_profile">
                <button @click="triggerFileInput" :disabled="uploadingAvatar">
                    {{ uploadingAvatar ? 'Chargement...' : 'Changer d\'image' }}
                </button>
                <input 
                    ref="fileInput" 
                    type="file" 
                    accept="image/*" 
                    style="display: none;" 
                    @change="handleFileChange"
                />
            </div>
        </div>

        <div class="profile-info">
            <p><strong>Pseudo:</strong> {{ profile.pseudo }}</p>
            <p><strong>Membre depuis:</strong> {{ formatDate(profile.created_at) }}</p>
            
            <p v-if="profile.is_own_profile">
                <strong>Email:</strong> {{ profile.email }}
            </p>
        </div>

        <div class="bio-section">
            <h4>Présentation</h4>
            <div v-if="!isEditing" class="bio-display">
                <p>{{ profile.bio || 'Aucune présentation' }}</p>
                <button v-if="profile.is_own_profile" @click="startEditing">
                    Modifier ma présentation
                </button>
            </div>
            
            <div v-if="isEditing && profile.is_own_profile" class="bio-edit">
                <textarea v-model="editForm.bio" rows="4" cols="50" 
                         placeholder="Écrivez quelque chose sur vous..."></textarea>
                <div>
                    <button @click="saveProfile" :disabled="saving">
                        {{ saving ? 'Sauvegarde...' : 'Sauvegarder' }}
                    </button>
                    <button @click="cancelEditing">Annuler</button>
                </div>
                <p v-if="saveError" class="save-error">{{ saveError }}</p>
            </div>
        </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getAuth } from 'firebase/auth'
const API_URL = import.meta.env.VITE_API_URL;

const route = useRoute()
const loading = ref(true)
const error = ref('')
const profile = ref({})
const isEditing = ref(false)
const saving = ref(false)
const saveError = ref('')
const uploadingAvatar = ref(false)

const editForm = ref({
    bio: '',
    avatar_url: ''
})

const fileInput = ref(null)

const getAvatarUrl = () => {
    if (profile.value.avatar_url && profile.value.avatar_url !== 'default_avatar.png') {
        return profile.value.avatar_url
    }
    return '/default_avatar.png'
}

const triggerFileInput = () => {
    fileInput.value.click()
}

const handleFileChange = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    if (!file.type.startsWith('image/')) {
        alert('Veuillez sélectionner une image')
        return
    }

    if (file.size > 1024 * 1024) {
        alert('L\'image est trop volumineuse (max 1 Mo)')
        return
    }

    uploadingAvatar.value = true

    try {
        const base64 = await fileToBase64(file)
        
        const token = await getUserToken()
        const response = await fetch(`${API_URL}/api/users/${encodeURIComponent(profile.value.pseudo)}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                bio: profile.value.bio || '',
                avatar_url: base64
            })
        })

        if (response.ok) {
            profile.value.avatar_url = base64
            editForm.value.avatar_url = base64
        } else {
            const errorData = await response.json()
            alert(errorData.error || 'Erreur lors de la sauvegarde')
        }
    } catch (err) {
        console.error('Erreur:', err)
        alert('Erreur lors du chargement de l\'image')
    } finally {
        uploadingAvatar.value = false
        event.target.value = ''
    }
}

const fileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader()
        reader.readAsDataURL(file)
        reader.onload = () => resolve(reader.result)
        reader.onerror = (error) => reject(error)
    })
}

const getUserToken = async () => {
    const auth = getAuth()
    const user = auth.currentUser
    if (user) {
        return await user.getIdToken()
    }
    return null
}

const loadProfile = async () => {
    try {
        const pseudo = route.params.pseudo
        const token = await getUserToken()
        
        if (!token) {
            error.value = "Vous devez être connecté pour voir les profils"
            return
        }

        const response = await fetch(`${API_URL}/api/users/${pseudo}`, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })

        if (!response.ok) {
            const errorData = await response.json()
            error.value = errorData.error || "Erreur lors du chargement du profil"
            return
        }

        profile.value = await response.json()
        editForm.value = {
            bio: profile.value.bio || '',
            avatar_url: profile.value.avatar_url || ''
        }

    } catch (err) {
        error.value = "Erreur de connexion"
    } finally {
        loading.value = false
    }
}

const startEditing = () => {
    isEditing.value = true
    saveError.value = ''
}

const cancelEditing = () => {
    isEditing.value = false
    editForm.value = {
        bio: profile.value.bio || '',
        avatar_url: profile.value.avatar_url || ''
    }
}

const saveProfile = async () => {
    saving.value = true
    saveError.value = ''
    
    try {
        const token = await getUserToken()
        const response = await fetch(`${API_URL}/api/users/${encodeURIComponent(profile.value.pseudo)}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(editForm.value)
        })

        if (!response.ok) {
            const errorData = await response.json()
            saveError.value = errorData.error || "Erreur lors de la sauvegarde"
            return
        }

        profile.value.bio = editForm.value.bio
        profile.value.avatar_url = editForm.value.avatar_url
        isEditing.value = false

    } catch (err) {
        saveError.value = "Erreur de connexion"
    } finally {
        saving.value = false
    }
}

const formatDate = (dateString) => {
    if (!dateString) return ''
    return new Date(dateString).toLocaleDateString('fr-FR')
}

onMounted(() => {
    loadProfile()
})
</script>

<style scoped>
.profile-container {
  max-width: 700px;
  margin: 0 auto;
  padding: 30px 25px;
  background-color: #ffffff;
  border-radius: 2px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
  font-family: 'Roboto', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #1f2937;
}

.loading, .error {
  text-align: center;
  font-size: 1.1rem;
  padding: 20px;
  color: #6b7280;
  font-style: italic;
}

.error {
  color: #dc2626;
  border-radius: 2px;
  border: 1px solid #fca5a5;
}

h3 {
  font-size: 2rem;
  font-weight: 700;
  color: #1e3a8a;
  text-align: center;
  margin-bottom: 30px;
}

h4 {
  font-size: 1.3rem;
  font-weight: 600;
  color: #1e3a8a;
  margin: 25px 0 15px 0;
  border-bottom: 2px solid #e0e7ff;
  padding-bottom: 8px;
}

.avatar-section {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px;
  border-radius: 2px;
}

.avatar-section img {
  margin-bottom: 15px;
  height: 10rem;
  width: 10rem;
}

.avatar-section button {
  background-color: #6366f1;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 2px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.avatar-section button:hover:not(:disabled) {
  background-color: #4f46e5;
  transform: translateY(-1px);
}

.avatar-section button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.profile-info {
  padding: 20px;
  border-radius: 2px;
  margin-bottom: 25px;
}

.profile-info p {
  margin: 8px 0;
  font-size: 1rem;
  line-height: 1.5;
}

.profile-info p strong {
  color: #111827;
  font-weight: 600;
}

.bio-section {
  padding: 20px;
  border-radius: 2px;
}

.bio-display p {
  font-size: 1rem;
  line-height: 1.6;
  color: #374151;
  margin-bottom: 15px;
  padding: 12px;
}

.bio-edit textarea {
  width: 100%;
  padding: 12px 15px;
  font-size: 1rem;
  font-family: inherit;
  resize: vertical;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
  margin-bottom: 15px;
}

.bio-edit textarea:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

button {
  padding: 10px 18px;
  border: none;
  border-radius: 2px;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-right: 10px;
  margin-bottom: 10px;
}

button.primary, 
.bio-edit button:first-of-type,
.bio-display button {
  background-color: #6366f1;
  color: white;
}

button.primary:hover:not(:disabled), 
.bio-edit button:first-of-type:hover:not(:disabled),
.bio-display button:hover {
  background-color: #4f46e5;
  transform: translateY(-1px);
}

button.secondary,
.bio-edit button:last-of-type {
  background-color: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

button.secondary:hover,
.bio-edit button:last-of-type:hover {
  background-color: #e5e7eb;
  transform: translateY(-1px);
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.save-error {
  color: #dc2626 !important;
  font-size: 0.9rem;
  background-color: #fee2e2;
  padding: 8px 12px;
  border-radius: 2px;
  border: 1px solid #fca5a5;
  margin-top: 10px;
}
</style>