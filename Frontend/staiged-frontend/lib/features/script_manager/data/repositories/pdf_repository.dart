import 'dart:typed_data';
import '../interfaces/pdf_repository_interface.dart';
import '../providers/api_provider.dart';
import '../../domain/models/pdf_model.dart';

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
}
