import 'dart:typed_data'; 

import '../../domain/models/pdf_model.dart';

abstract class PDFRepositoryInterface {
  Future<PDFModel> uploadPDF(String filePath, String marginSide);
  Future<PDFModel> fetchPDF(String filename);
  Future<PDFModel> uploadPDFBytes(Uint8List fileBytes, String marginSide);  // Add this method
}