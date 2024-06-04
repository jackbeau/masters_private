const express = require('express');
const multer = require('multer');
const uploadController = require('../controllers/uploadController');

const router = express.Router();
const upload = multer({ dest: 'server/storage/pdfs/' });

router.post('/script/upload', upload.single('file'), uploadController.uploadPDF);
router.get('/script/download/:filename', uploadController.downloadPDF);

module.exports = router;
