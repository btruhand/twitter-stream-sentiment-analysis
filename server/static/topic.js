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
    Graph.addData(event.data);
  },
  handleClose: function(event) {
    if (event.wasClean) {
      console.info(`Closed connection cleanly with code ${event.code} and reason ${event.reason}`);
    } else {
      console.error(`Did not close cleanly with code ${event.code} and reason ${event.reason}`);
    }
  }
};

const Graph = {
  DRAW_INTERVAL: 100, // in milliseconds
  graphData: {},

  drawGraph(graphId) {
    console.log(`Drawing for graph ${graphId}`);
    if (graphId in Graph.graphData && Graph.graphData[graphId].data.length > 0) {
      console.log('Inside drawing logic');
      // request ID is the graph ID
      console.log(Graph.graphData[graphId].at);
      Plotly.extendTraces(graphId, {
        x: [Graph.graphData[graphId].at],
        y:[Graph.graphData[graphId].data],
        text: [Graph.graphData[graphId].text]
      }, [0]);
      Graph.graphData[graphId].at = [];
      Graph.graphData[graphId].text = [];
      Graph.graphData[graphId].data = [];
    }
  },

  graphifyName(name) {
    return name + '-graph';
  },

  addData(data) {
    console.log(`Data is ${data}`);
    console.log(`Data type is ${typeof data}`);
    const jsonData = JSON.parse(data);
    console.log('JSON data is', jsonData);
    const graphId = Graph.graphifyName(jsonData.topic);
    console.log(`In add data adding for ${graphId}`);
    const topicData = {'at': jsonData.at, 'text': jsonData.message, 'data': jsonData.data};
    console.log('Topic data is', topicData);
    if(!(graphId in Graph.graphData)) {
      Graph.graphData[graphId] = {'at': [], 'text': [], 'data': []};
    }
    Graph.graphData[graphId].at.push(jsonData.at);
    Graph.graphData[graphId].text.push(jsonData.text);
    Graph.graphData[graphId].data.push(jsonData.data);
  }
}

const Topic = {
  topicConnection: null, // WsTopic instance
  numTopicsSubscribed: 0,

  EVENTS: {
    SUBSCRIBE: 'sub',
    CANCEL: 'cancel'
  },

  graphTopics: {},

  request: () => {
    //const topicText = document.getElementById('topic_text').value;
    const topicText = document.getElementById('DropDownTopics').options[document.getElementById('DropDownTopics').selectedIndex].value;
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
    const graphId = cancelEvent.target.dataset.graphId;
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
      .then(Topic.removeGraphArea(graphId))
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

    const graphId = Graph.graphifyName(jsonPayload.requested_topic);
    const newGraph = document.createElement('div');
    newGraph.setAttribute('id', graphId);
    topicsArea.appendChild(newGraph);

    const layout = {
      grid: {
        domain: {
          y: [-1,1]
        }
      }
    };
    Plotly.newPlot(graphId, [{
      mode: 'markers',
      type:'scatter',
      x: [],
      y: [],
      text: []
    }]);

    const label = document.createElement('label');
    label.textContent = 'If you want to cancel click here: ';

    const cancel = document.createElement('button');
    cancel.setAttribute('value', jsonPayload.requested_topic);
    cancel.dataset.requestId = jsonPayload.request_id;
    cancel.dataset.graphId = graphId;
    cancel.textContent = `Cancel ${jsonPayload.requested_topic}`;
    cancel.addEventListener('click', Topic.cancel); 
    newGraph.appendChild(label);
    newGraph.appendChild(cancel);

/**                
                if(cnt > 250) {
                    Plotly.relayout(jsonPayload.request_id,{
                        xaxis: {
                            range: [cnt-250,cnt]
                        }
                   });
                }
*/

    Topic.graphTopics[graphId] = setInterval(() => Graph.drawGraph(graphId), Graph.DRAW_INTERVAL);
    return jsonPayload;
  },

  removeGraphArea: (graphId) => (jsonPayload) => {
    console.log("Remove graph area", graphId);
    clearInterval(Topic.graphTopics[graphId]);
    delete Topic.graphTopics[graphId];
    delete Graph.graphData[graphId];
    document.getElementById(graphId).remove();
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
