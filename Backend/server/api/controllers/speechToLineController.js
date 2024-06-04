const { startSpeechToLine, stopSpeechToLine } = require('../../grpc/client/client');

exports.startSpeechToLine = async (req, res) => {
  try {
    const response = await startSpeechToLine();
    if (response.success) {
      res.status(200).json({ message: 'SpeechToLine process started successfully' });
    } else {
      res.status(500).json({ message: 'Failed to start SpeechToLine process' });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

exports.stopSpeechToLine = async (req, res) => {
  try {
    const response = await stopSpeechToLine();
    if (response.success) {
      res.status(200).json({ message: 'SpeechToLine process stopped successfully' });
    } else {
      res.status(500).json({ message: 'Failed to stop SpeechToLine process' });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
