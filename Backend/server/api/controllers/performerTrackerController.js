const { startPerformerTracker, stopPerformerTracker } = require('../../grpc/client/client');

exports.startPerformerTracker = async (req, res) => {
  try {
    const response = await startPerformerTracker();
    if (response.success) {
      res.status(200).json({ message: 'Performer Tracker process started successfully' });
    } else {
      res.status(500).json({ message: 'Failed to start Performer Tracker process' });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

exports.stopPerformerTracker = async (req, res) => {
  try {
    const response = await stopPerformerTracker();
    if (response.success) {
      res.status(200).json({ message: 'Performer Tracker process stopped successfully' });
    } else {
      res.status(500).json({ message: 'Failed to stop Performer Tracker process' });
    }
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
