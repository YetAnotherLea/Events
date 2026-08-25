import { getAuth } from "firebase/auth";

const API_URL = import.meta.env.VITE_API_URL;

export function syncUserWithBackend(pseudo = "") {
  const auth = getAuth();
  const user = auth.currentUser;
  if (!user) return Promise.reject(new Error("Utilisateur non connecté"));

  return user
    .getIdToken()
    .then((token) => {
      return fetch(`${API_URL}/api/users/sync`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          idToken: token,
          pseudo: pseudo,
        }),
      });
    })
    .then((response) => {
      if (!response.ok) {
        return response.json().then((err) => {
          throw new Error(err.error || "Sync failed");
        });
      }
      return response.json();
    });
}

export async function getCurrentUserInfo() {
  const auth = getAuth();
  const user = auth.currentUser;
  if (!user) throw new Error("Utilisateur non connecté");

  const token = await user.getIdToken();

  const response = await fetch(`${API_URL}/api/users/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error("Erreur lors de la récup des infos user");
  }

  return await response.json();
}
