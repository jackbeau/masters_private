/**
 * @file grpcClient.js
 * @description gRPC client for interacting with the ScriptService. Includes functions for adding margins, performing OCR, and managing speech-to-script pointers and performer trackers.
 * @author Jack Beaumont
 * @date 06/06/2024
 */

const grpc = require("@grpc/grpc-js");
const protoLoader = require("@grpc/proto-loader");
const path = require("path");

const PROTO_PATH = path.join(__dirname, "../service.proto");
const packageDefinition = protoLoader.loadSync(PROTO_PATH, {
  keepCase: true,
  longs: String,
  enums: String,
  defaults: true,
  oneofs: true,
});

const serviceProto =
  grpc.loadPackageDefinition(packageDefinition).ScriptService;
const client = new serviceProto(
  "localhost:50051",
  grpc.credentials.createInsecure()
);

/**
 * Adds margin to a PDF file.
 * @param {string} filePath - The path to the PDF file.
 * @param {string} marginSide - The side where the margin should be added.
 * @returns {Promise<Object>} Response from the gRPC service.
 */
const addMargin = (filePath, marginSide) => {
  return new Promise((resolve, reject) => {
    client.AddMargin(
      { file_path: filePath, margin_side: marginSide },
      (error, response) => {
        if (error) {
          reject(error);
        } else {
          resolve(response);
        }
      }
    );
  });
};

/**
 * Performs OCR on a PDF file.
 * @param {string} filePath - The path to the PDF file.
 * @returns {Promise<Object>} Response from the gRPC service.
 */
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

/**
 * Starts the speech-to-script pointer service.
 * @returns {Promise<Object>} Response from the gRPC service.
 */
const startSpeechToScriptPointer = () => {
  return new Promise((resolve, reject) => {
    client.StartSpeechToScriptPointer({}, (error, response) => {
      if (error) {
        reject(error);
      } else {
        resolve(response);
      }
    });
  });
};

/**
 * Stops the speech-to-script pointer service.
 * @returns {Promise<Object>} Response from the gRPC service.
 */
const stopSpeechToScriptPointer = () => {
  return new Promise((resolve, reject) => {
    client.StopSpeechToScriptPointer({}, (error, response) => {
      if (error) {
        reject(error);
      } else {
        resolve(response);
      }
    });
  });
};

/**
 * Starts the performer tracker service.
 * @returns {Promise<Object>} Response from the gRPC service.
 */
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

/**
 * Stops the performer tracker service.
 * @returns {Promise<Object>} Response from the gRPC service.
 */
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

module.exports = {
  addMargin,
  performOCR,
  startSpeechToScriptPointer,
  stopSpeechToScriptPointer,
  startPerformerTracker,
  stopPerformerTracker,
};
