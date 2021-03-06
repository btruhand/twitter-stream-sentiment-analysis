/* eslint-disable no-use-before-define */ /* global Plotly */

const userId = document.body.id;
console.info(`Your ID is ${userId}`);

const WsTopic = {
  ws: null,
  create: function(ws_uri) {
    const instance = {...WsTopic};
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
  TIME_WINDOW: 60000, // in milliseconds
  graphData: {},
  graphTopics: {},
  xAxisRange: {},

  drawGraph(graphId) {
    if (graphId in Graph.graphData && Graph.graphData[graphId].sentiment.length > 0) {
      const dataAmount = Graph.graphData[graphId].sentiment.length;
      // request ID is the graph ID
      Plotly.extendTraces(graphId, {
        x: [Graph.graphData[graphId].created_at],
        y:[Graph.graphData[graphId].sentiment],
        text: [Graph.graphData[graphId].tweet]
      }, [0]);

      const latestTs = Graph.graphData[graphId].created_at[dataAmount - 1];
      if (latestTs > Graph.xAxisRange[graphId].high) {
        const diff = Graph.xAxisRange[graphId].high - latestTs;
        Graph.xAxisRange[graphId].low = Graph.xAxisRange[graphId].low + diff;
        Graph.xAxisRange[graphId].high = latestTs + Graph.TIME_WINDOW;
        Plotly.relayout(graphId,{
          xaxis: {
            range: [Graph.xAxisRange[graphId].low, Graph.xAxisRange[graphId].high],
            type: 'date'
          }
        });
      }

      Graph.graphData[graphId].created_at = [];
      Graph.graphData[graphId].tweet = [];
      Graph.graphData[graphId].sentiment = [];
    }
  },

  graphifyName(name) {
    return name + '-graph';
  },

  addData(data) {
    const jsonData = JSON.parse(data);
    const graphId = Graph.graphifyName(jsonData.topic.replace('-sentiment',''));
    if(!(graphId in Graph.graphData)) {
      Graph.graphData[graphId] = {'created_at': [], 'tweet': [], 'sentiment': []};
    }
    Graph.graphData[graphId].created_at.push(Graph.xAxisTimeFormat(jsonData.created_at));
    Graph.graphData[graphId].tweet.push(jsonData.tweet);
    Graph.graphData[graphId].sentiment.push(jsonData.sentiment_score);
  },

  xAxisTimeFormat(ts) {
    const time = new Date(ts);
    return Date.parse(time.toLocaleTimeString(undefined, {
      hour12: false,
      year: 'numeric', month: '2-digit', day: '2-digit',
      hour: '2-digit', minute: '2-digit', second: '2-digit'
    }));
  },

  createGraphArea: (jsonPayload) => {
    const topicsArea = document.getElementById('requested_topics');

    const graphId = Graph.graphifyName(jsonPayload.requested_topic);
    const newGraph = document.createElement('div');
    newGraph.setAttribute('id', graphId);
    topicsArea.appendChild(newGraph);

    const ts = Date.now();
    const layout = {
      title: `${jsonPayload.requested_topic} Sentiment`,
      xaxis: {
        range: [ts, ts + Graph.TIME_WINDOW],
        type: 'date',
      },
      yaxis: {
        range: [-1.1,1.1],
      }
    };
    Plotly.newPlot(graphId, [{
      mode: 'markers',
      type:'scatter',
      x: [],
      y: [],
      text: []
    }], layout);
    Graph.xAxisRange[graphId] = {low: ts, high: ts + Graph.TIME_WINDOW};

    const label = document.createElement('label');
    label.textContent = 'If you want to cancel click here: ';

    const cancel = document.createElement('button');
    cancel.setAttribute('value', jsonPayload.requested_topic);
    cancel.dataset.requestId = jsonPayload.request_id;
    cancel.dataset.topic = jsonPayload.requested_topic;
    cancel.dataset.graphId = graphId;
    cancel.textContent = `Cancel ${jsonPayload.requested_topic}`;
    cancel.addEventListener('click', Topic.cancel); // eslint: disable=no-use-before-define 
    newGraph.appendChild(label);
    newGraph.appendChild(cancel);

    Graph.graphTopics[graphId] = setInterval(() => Graph.drawGraph(graphId), Graph.DRAW_INTERVAL);
    return jsonPayload;
  },

  removeGraphArea: (graphId) => (jsonPayload) => { // eslint-dsiable no-unused-vars
    console.log('Remove graph area', graphId);
    clearInterval(Graph.graphTopics[graphId]);
    delete Graph.graphTopics[graphId];
    delete Graph.graphData[graphId];
    delete Graph.xAxisRange[graphId];
    document.getElementById(graphId).remove();
  },
};

const Topic = {
  topicConnection: null, // WsTopic instance
  numTopicsSubscribed: 0,

  EVENTS: {
    SUBSCRIBE: 'sub',
    CANCEL: 'cancel'
  },

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
      .then(Graph.createGraphArea)
      .catch((reason) => console.error(`Unable to request for topic because of ${reason}`));
  },
  cancel: (cancelEvent) => {
    const topic = cancelEvent.target.dataset.topic;
    const graphId = cancelEvent.target.dataset.graphId;
    const requestId = cancelEvent.target.dataset.requestId;
    console.info(`Cancelling topic with requestID ${requestId}`);

    const headers = new Headers({'Content-Type': 'application/json'});
    const request = new Request('/topic', {
      method: 'DELETE',
      headers: headers,
      body: JSON.stringify({request_id: requestId, userId, topic}),
    });
    fetch(request)
      .then(Topic.handleResponse)
      .then(Topic.closeWebsocketConnection)
      .then(Graph.removeGraphArea(graphId))
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
  },

  connectToWebsocket: (jsonPayload) => {
    if (Topic.numTopicsSubscribed === 0) {
      console.info('Establishing websocket connection due to start of topic subscription');
      const websocketUri = jsonPayload.ws_connection;
      Topic.topicConnection = WsTopic.create(websocketUri);
    }
    Topic.numTopicsSubscribed++;
    // send subscription message
    // using setTimeout is a hack but works for local settings
    setTimeout(() => Topic.topicConnection.ws.send(
      JSON.stringify({'subscribe': true, 'topic': jsonPayload.requested_topic})
    ), 100);
    return jsonPayload;
  },
  closeWebsocketConnection: (jsonPayload) => {
    Topic.topicConnection.ws.send(
      JSON.stringify({'unsubscribe': true, 'topic': jsonPayload.cancelled_topic})
    );
    if (Topic.numTopicsSubscribed === 1) {
      console.info('Closing websocket connection because no more topics subscribed');
      const wsConnection = Topic.topicConnection;
      wsConnection.ws.close(1000, `User ${userId} finished streaming to all subscribed topics`);
      Topic.topicConnection = null;
    }
    Topic.numTopicsSubscribed--;
    return jsonPayload;
  }
};
