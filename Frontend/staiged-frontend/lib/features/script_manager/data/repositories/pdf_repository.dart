import 'dart:typed_data';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../interfaces/pdf_repository_interface.dart';
import '../providers/api_provider.dart';
import '../../domain/models/pdf_model.dart';
import '../../domain/models/pdf_extensions.dart'; // Import the extensions

class PDFRepository implements PDFRepositoryInterface {
  final ApiProvider apiProvider;

  PDFRepository(this.apiProvider);

  @override
  Future<PDFModel> uploadPDF(String filePath, String marginSide) async {
    final response = await apiProvider.uploadPDF(filePath, marginSide);
    return PDFModel.fromJson(response);
  }

  @override
  Future<PDFModel> fetchPDF(String filename) async {
    final response = await apiProvider.fetchPDF(filename);
    return PDFModel.fromJson(response);
  }

  @override
  Future<PDFModel> uploadPDFBytes(Uint8List fileBytes, String marginSide) async {
    final response = await apiProvider.uploadPDFBytes(fileBytes, marginSide);
    return PDFModel.fromJson(response);
  }

  @override
  Future<void> sendExtractedText(String filename, Map<String, dynamic> pageTexts) async {
    final response = await apiProvider.sendExtractedText(filename, pageTexts);
    if (response.statusCode != 200) {
      throw Exception('Failed to send extracted text');
    }
  }
}
