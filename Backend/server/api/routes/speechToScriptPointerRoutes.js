/**
 * @file routes/speechToScriptPointerRoutes.js
 * @description Routes for starting and stopping the speech-to-script pointer service using the speechToScriptPointerController.
 * @version 1.0.0
 * @author Jack Beaumont
 * @date 06/06/2024
 */

const express = require("express");
const speechToScriptPointerController = require("../controllers/speechToScriptPointerController");

const router = express.Router();

router.post(
  "/speech-to-script-pointer/start",
  speechToScriptPointerController.startSpeechToScriptPointer
);
router.post(
  "/speech-to-script-pointer/stop",
  speechToScriptPointerController.stopSpeechToScriptPointer
);

module.exports = router;
