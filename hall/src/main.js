import { createApp } from "vue";
import { createRouter, createWebHistory } from "vue-router";
import App from "./App.vue";
import GirlsView from "./page/girls.vue";
import AnimeView from "./page/anime.vue";
import ChatView from "./page/chat.vue";

const routes = [
  { path: "/", component: GirlsView },
  { path: "/anime", component: AnimeView },
  { path: "/chat", component: ChatView },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

createApp(App).use(router).mount("#app");
