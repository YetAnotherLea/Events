<template>
    <div class="legal">
        <h3>Politique de confidentialité</h3>
        <p>
            Events est un projet étudiant de démonstration (Web Academy Epitech Marseille).
            Il n'a aucune finalité commerciale.
        </p>
        <h4>Données collectées</h4>
        <p>
            À la création d'un compte (email, Google ou Facebook), nous conservons votre adresse
            email, un pseudo, l'identifiant technique fourni par Firebase Authentication et, si vous
            les renseignez, une bio et un avatar. Aucune autre donnée n'est lue sur votre compte
            Google ou Facebook.
        </p>
        <h4>Utilisation</h4>
        <p>
            Ces données servent uniquement à vous identifier et à afficher votre profil. Elles ne
            sont ni vendues, ni transmises à des tiers. L'email n'est visible que par vous.
        </p>
        <h4>Hébergement</h4>
        <p>
            Les profils sont stockés sur un serveur situé en France. L'authentification est
            assurée par Firebase (Google).
        </p>
        <h4>Vos droits</h4>
        <p>
            Vous pouvez à tout moment demander la suppression de votre compte et de vos données :
            voir la page <router-link to="/data-deletion">suppression des données</router-link>.
        </p>
    </div>
</template>

<style scoped>
.legal {
  max-width: 600px;
  margin: 0 auto;
  padding: 30px 25px;
  background-color: #ffffff;
  border-radius: 2px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
  font-family: 'Roboto', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.5;
}

h3 {
  font-size: 1.8rem;
  font-weight: 700;
  color: #1e3a8a;
  text-align: center;
  margin-bottom: 25px;
}

h4 {
  color: #5A4CBF;
  margin: 20px 0 5px;
}
</style>
