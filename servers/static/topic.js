const WsTopic = {
  ws: null,
  create: function(ws_uri) {
    const instance = {...WsTopic};
    console.log(instance);
    instance.ws = new WebSocket(ws_uri);
    instance.ws.onopen = () => console.log(`Websocket connection to ${ws_uri} opened`);
    instance.ws.onmessage = this.handle_message;
    return instance;
  },
  handle_message: function(event) {
    console.log(`Received data ${event.data}`);
  }
};

const Topic = {
  topics_subscribed: [],
  request: () => {
    const topicText = document.getElementById('topic_text').value;
    const headers = new Headers({'Content-Type': 'application/json'})
    const request = new Request('/request_topic', {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({topic: topicText}),
    });
    fetch(request)
      .then(Topic.handle_response)
      .then(Topic.connect_to_websocket);
  },
  handle_response: (response) => {
    console.log(response);
    if (response.ok) {
      if (response.headers.get('content-type').startsWith('application/json')) {
        return response.json();
      }
    }
    // if not any of the above do something here
  },
  connect_to_websocket: (json_payload) => {
    const websocket_uri = json_payload.ws_connection;
    Topic.topics_subscribed.push(WsTopic.create(websocket_uri));
  }
};