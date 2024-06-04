const grpc = require('@grpc/grpc-js');
const protoLoader = require('@grpc/proto-loader');
const path = require('path');

const PROTO_PATH = path.join(__dirname, '../service.proto');
const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
});

const serviceProto = grpc.loadPackageDefinition(packageDefinition).ScriptService;

const client = new serviceProto('localhost:50051', grpc.credentials.createInsecure());

const addMargin = (filePath, marginSide) => {
  return new Promise((resolve, reject) => {
    client.AddMargin({ file_path: filePath, margin_side: marginSide }, (error, response) => {
      if (error) {
        reject(error);
      } else {
        resolve(response);
      }
    });
  });
};

const performOCR = (filePath) => {
  return new Promise((resolve, reject) => {
    client.PerformOCR({ file_path: filePath }, (error, response) => {
      if (error) {
        reject(error);
      } else {
        resolve(response);
      }
    });
  });
};

const startSpeechToLine = () => {
  return new Promise((resolve, reject) => {
    client.StartSpeechToLine({}, (error, response) => {
      if (error) {
        reject(error);
      } else {
        resolve(response);
      }
    });
  });
};

const stopSpeechToLine = () => {
  return new Promise((resolve, reject) => {
    client.StopSpeechToLine({}, (error, response) => {
      if (error) {
        reject(error);
      } else {
        resolve(response);
      }
    });
  });
};

const startPerformerTracker = () => {
  return new Promise((resolve, reject) => {
    client.StartPerformerTracker({}, (error, response) => {
      if (error) {
        reject(error);
      } else {
        resolve(response);
      }
    });
  });
};

const stopPerformerTracker = () => {
  return new Promise((resolve, reject) => {
    client.StopPerformerTracker({}, (error, response) => {
      if (error) {
        reject(error);
      } else {
        resolve(response);
      }
    });
  });
};

module.exports = { addMargin, performOCR, startSpeechToLine, stopSpeechToLine, startPerformerTracker, stopPerformerTracker};
