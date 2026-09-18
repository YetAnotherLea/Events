import { createRouter, createWebHistory } from "vue-router";
import { getAuth, onAuthStateChanged } from "firebase/auth";
import Home from "../views/Home.vue";
import SignIn from "../views/SignIn.vue";
import Register from "../views/Register.vue";
import Profile from "../views/Profile.vue";
import EventDetail from "../views/EventDetail.vue";
import Privacy from "../views/Privacy.vue";
import DataDeletion from "../views/DataDeletion.vue";


const routes = [
  {
    path: "/",
    name: "Home",
    component: Home,
  },
  { path: "/register", component: Register },
  { path: "/signin", component: SignIn },
  {
    path: "/profile/:pseudo",
    name: "Profile",
    component: Profile,
    meta: {
      requiresAuth: true,
    },
  },
  { path: "/event/:uid", name: "EventDetail", component: EventDetail },
  { path: "/privacy", component: Privacy },
  { path: "/data-deletion", component: DataDeletion },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

const getCurrentUser = () => {
  return new Promise((resolve, reject) => {
    const removeListener = onAuthStateChanged(
      getAuth(),
      (user) => {
        removeListener();
        resolve(user);
      },
      reject
    );
  });
};

router.beforeEach(async (to, from, next) => {
  if (to.matched.some((record) => record.meta.requiresAuth)) {
    if (await getCurrentUser()) {
      next();
    } else {
      alert("Vous devez être connecté pour accéder aux profils");
      next("/signin");
    }
  } else {
    next();
  }
});

export default router;
