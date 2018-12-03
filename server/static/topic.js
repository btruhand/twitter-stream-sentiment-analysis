const userId = document.body.id;
console.info(`Your ID is ${userId}`);

const WsTopic = {
  ws: null,
  create: function(ws_uri) {
    const instance = {...WsTopic};
    console.info(instance);
    instance.ws = new WebSocket(ws_uri);
    instance.ws.onopen = () => console.info(`Websocket connection to ${ws_uri} opened`);
    instance.ws.onclose = this.handleClose;
    instance.ws.onmessage = this.handleMessage;
    return instance;
  },
  handleMessage: function(event) {
    console.info(`Received data ${event.data}`);
  },
  handleClose: function(event) {
    if (event.wasClean) {
      console.info(`Closed connection cleanly with code ${event.code} and reason ${event.reason}`);
    } else {
      console.error(`Did not close cleanly with code ${event.code} and reason ${event.reason}`);
    }
  }
};

const Topic = {
  topicConnection: null, // WsTopic instance
  numTopicsSubscribed: 0,

  EVENTS: {
    SUBSCRIBE: 'sub',
    CANCEL: 'cancel'
  },

  request: () => {
    const topicText = document.getElementById('topic_text').value;
    const headers = new Headers({'Content-Type': 'application/json'});
    const request = new Request('/topic', {
      method: 'POST',
      headers: headers,
      body: JSON.stringify({topic: topicText, userId}),
    });
    fetch(request)
      .then(Topic.handleResponse)
      .then(Topic.connectToWebsocket)
      .then(Topic.createGraphArea)
      .catch((reason) => console.error(`Unable to request for topic because of ${reason}`));
  },
  cancel: (cancelEvent) => {
    const requestId = cancelEvent.target.dataset.requestId;
    console.info(`Cancelling topic ${requestId} with request ID`);

    const headers = new Headers({'Content-Type': 'application/json'});
    const request = new Request('/topic', {
      method: 'DELETE',
      headers: headers,
      body: JSON.stringify({request_id: requestId, userId}),
    });
    fetch(request)
      .then(Topic.handleResponse)
      .then(Topic.closeWebsocketConnection)
      .then(Topic.removeGraphArea)
      .catch((reason) => console.error(`Unable to cancel for topic because of ${reason}`));
  },

  handleResponse: (response) => {
    console.info('Received response', response);
    if (response.ok) {
      if (response.headers.get('content-type').startsWith('application/json')) {
        return response.json();
      }
    }
    throw Error('Response was not OK or JSON');
    // if not any of the above do something here
  },

  createGraphArea: (jsonPayload) => {
    const topicsArea = document.getElementById('requested_topics');
    // this is placeholder code for actual graph area
    const newGraph = document.createElement('div');
    newGraph.setAttribute('id', jsonPayload.request_id);
    const label = document.createElement('label');
    label.textContent = 'If you want to cancel click here: ';

    const submit = document.createElement('button');
    submit.setAttribute('value', jsonPayload.requested_topic);
    submit.dataset.requestId = jsonPayload.request_id;
    submit.textContent = `Cancel ${jsonPayload.requested_topic}`;
    submit.addEventListener('click', Topic.cancel); 
    newGraph.appendChild(label);
    newGraph.appendChild(submit);
    topicsArea.appendChild(newGraph);

    return jsonPayload;
  },
  removeGraphArea: (jsonPayload) => {
    document.getElementById(jsonPayload.request_id).remove();
  },

  connectToWebsocket: (jsonPayload) => {
    if (Topic.numTopicsSubscribed === 0) {
      console.info('Establishing websocket connection due to start of topic subscription');
      const websocketUri = jsonPayload.ws_connection;
      Topic.topicConnection = WsTopic.create(websocketUri);
      Topic.numTopicsSubscribed++;
    }
    return jsonPayload;
  },
  closeWebsocketConnection: (jsonPayload) => {
    if (Topic.numTopicsSubscribed === 1) {
      console.info('Closing websocket connection because no more topics subscribed');
      const wsConnection = Topic.topicConnection;
      wsConnection.ws.close(1000, `User ${userId} finished streaming to all subscribed topics`);
      Topic.numTopicsSubscribed--;
      Topic.topicConnection = null;
    }
    return jsonPayload;
  }
};