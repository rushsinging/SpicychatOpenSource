<template>
  <div class="main-container">
    <div class="box">
      <div class="box-2"><span class="text">JOI AI</span></div>
      <div class="wrapper">
        <div class="box-3">
          <div class="section">
            <div class="wrapper-2">
              <div class="box-4">
                <div class="wrapper-3"><div class="wrapper-4"></div></div>
              </div>
              <div class="box-5">
                <span class="text-2">Spicy</span
                ><span class="text-3">chat</span>
              </div>
              <div class="wrapper-5">
                <div class="wrapper-6">
                  <!-- <div class="group">
                    <div class="wrapper-7">
                      <span class="text-4">Explore</span>
                    </div>
                  </div> -->
                  <div class="box-6">
                    <div class="group-2">
                      <div class="group-3"></div>
                      <span class="text-5">Chats</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="section-3">
              <div class="box-8">
                <span class="text-8">Create an account</span>
              </div>
              <div class="wrapper-8"><span class="text-9">Log in</span></div>
            </div>
            <!-- <div class="box-9">
              <div class="group-6"><div class="img"></div></div>
              <span class="text-a">Spicy</span>
            </div> -->
          </div>
        </div>
        <div class="section-4">
          <div class="wrapper-9">
            <div class="section-5">
              <div class="wrapper-a">
                <div class="group-7">
                  <div class="box-a">
                    <div class="box-e">
                      <div class="box-f">
                        <div class="group-b">
                          <div class="section-9">
                            <div class="section-a"></div>
                          </div>
                        </div>
                        <div class="box-10">
                          <div class="section-b">
                            <div class="wrapper-c">
                              <span class="text-d">Sunny</span>
                            </div>
                          </div>
                          <!-- <div class="wrapper-d">
                            <div class="wrapper-e">
                              <span class="text-e"
                                >Heeey, you there? Quick question — should I get
                                a smoothie or save my last $10 for my future
                                mortgage? Be real with me… but also, imagine how
                                good a mango-passionfruit smoothie would be
                                right now 😋</span
                              >
                            </div>
                          </div> -->
                        </div>
                        <div class="img-3"><div class="pic-2"></div></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="box-14">
              <div class="p-toc">
                <span class="terms-of-service">Terms of Service</span
                ><span class="privacy-policy">Privacy Policy</span
                ><span class="support">Support</span>
              </div>
              <span class="all-rights-reserved"
                >© 2025 All rights reserved.</span
              >
            </div>
          </div>
          <div class="chat-container">
            <div class="div">
              <div class="mrviol" ref="message_height">
                <div class="div-1" id="messages">
                  <div
                    v-for="m in messages"
                    :key="m.content"
                    :class="
                      m.sender === user_id ? 'message self' : 'message other'
                    "
                  >
                    {{ m.content }}
                  </div>
                </div>

                <!-- <div class="div-2">
                  <div class="span"><span class="today">today</span></div>
                  <div class="div-3"></div>
                </div> -->
              </div>
              <div class="chat">
                <div class="flex-row">
                  <div class="div-8">
                    <div class="textarea" @keydown.enter="send_message">
                      <textarea
                        v-model="message"
                        placeholder="Please input ..."
                      ></textarea>
                    </div>
                  </div>
                  <div class="svg">
                    <div class="pic-6" @click="send_message"></div>
                  </div>
                  <div class="img-6"></div>
                  <span class="text-19">+50</span>
                </div>
                <div class="wrapper-12">
                  <div class="group-14">
                    <span class="text-1a">Affection Level </span>
                  </div>
                  <div class="group-15"></div>
                  <div class="box-19"></div>
                  <div class="box-1a">
                    <span class="text-1b">loneliss</span>
                  </div>
                  <span class="text-1c">relationships</span
                  ><span class="text-1d">kinks</span>
                </div>
              </div>
            </div>
            <div class="wrapper-13">
              <div class="box-1b">
                <div class="group-16"><div class="img-7"></div></div>
              </div>
            </div>
            <div class="wrapper-14">
              <div class="pic-7"></div>
              <div class="img-8"></div>
              <div class="pic-8"></div>
              <div class="img-9"></div>
              <div class="img-a"></div>
              <div class="pic-9"></div>
            </div>
          </div>
          <div class="wrapper-15">
            <div class="box-1c">
              <div class="box-1d"><div class="img-b"></div></div>
              <span class="text-1e">Sunny</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="pic-a"></div>
  </div>
</template>

<script setup>
import { onMounted } from "vue";
import { ref } from "vue";
import { useCookies } from "vue3-cookies";

const { cookies } = useCookies();
// 邀请想要对话的角色，id 写死
const character_id = ref("1e833650-4f20-4361-ab01-4af3cc38c690");
const messages = ref([]);
const message = ref("");
const user_id = ref("");
const ws = ref(null);
const message_height = ref(null);

function set_session(event) {
  // console.log("set_session", event);
  let session = event.message;
  cookies.set("session", session);
  user_id.value = session;
}

function send_message() {
  let m = message.value;
  if (!m) {
    return;
  }
  console.log("send_message", message.value);
  ws.value.send(
    JSON.stringify({
      event: "message",
      message: m,
    })
  );
  messages.value.push({
    content: m,
    sender: user_id.value,
  });
  message.value = "";
}

onMounted(() => {
  let streaming = false;
  ws.value = new WebSocket(
    "https://nsfw.thousandsofyears.site/ws?user_id=" + cookies.get("session")
  );

  ws.value.onopen = () => {
    // console.log("WebSocket is open");
    const session = cookies.get("session");
    // console.log("session", session);
    ws.value.send(
      JSON.stringify({
        event: "join",
        message: session,
      })
    );
  };
  ws.value.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log(data);
    switch (data.event) {
      case "message":
        messages.value.push(data.message);
        break;
      case "hello":
        set_session(data);

        ws.value.send(
          JSON.stringify({
            event: "invite",
            message: character_id.value,
          })
        );
        break;
      case "history":
        for (let m of data.messages) {
          messages.value.push(m);
        }
        break;
      case "message_stream":
        if (!streaming) {
          streaming = true;
          messages.value.push({
            id: messages.value.length + 1,
            content: "",
            sender: "ai",
          });
        }
        messages.value[messages.value.length - 1].content += data.content;
        break;
      case "message_end":
        streaming = false;
        break;
    }
  };

  ws.value.onclose = () => {
    console.log("WebSocket is closed");
    // alert("WebSocket is closed, Please refresh the page");
  };
});
</script>

<style scoped src="./chat.css"></style>
