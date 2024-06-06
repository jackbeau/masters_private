/*
 * PDFRepository.dart
 * 
 * Author: Jack Beaumont
 * Date: 06/06/2024
 * 
 * Description: This file defines the PDFRepository class which implements the 
 * PDFRepositoryInterface. It handles uploading, fetching, and sending text 
 * extracted from PDF files through an API provider.
 */

import 'dart:typed_data';
import 'package:logging/logging.dart';
import '../interfaces/pdf_repository_interface.dart';
import '../providers/api_provider.dart';
import '../../domain/entities/pdf_model.dart';

class PDFRepository implements PDFRepositoryInterface {
  final ApiProvider apiProvider;
  final _log = Logger('PDFRepository');

  PDFRepository(this.apiProvider);

  /// Uploads a PDF from the specified file path.
  /// 
  /// Parameters:
  /// - [filePath]: The path to the PDF file to upload.
  /// - [marginSide]: The margin side for the PDF.
  /// 
  /// Returns:
  /// - A Future that completes with a PDFModel of the uploaded PDF.
  @override
  Future<PDFModel> uploadPDF(String filePath, String marginSide) async {
    _log.info('Uploading PDF from file path: $filePath with margin side: $marginSide');
    final response = await apiProvider.uploadPDF(filePath, marginSide);
    return PDFModel.fromJson(response);
  }

  /// Fetches a PDF with the specified filename.
  /// 
  /// Parameters:
  /// - [filename]: The name of the PDF file to fetch.
  /// 
  /// Returns:
  /// - A Future that completes with a PDFModel of the fetched PDF.
  @override
  Future<PDFModel> fetchPDF(String filename) async {
    _log.info('Fetching PDF with filename: $filename');
    final response = await apiProvider.fetchPDF(filename);
    return PDFModel.fromJson(response);
  }

  /// Uploads a PDF from the specified byte data.
  /// 
  /// Parameters:
  /// - [fileBytes]: The byte data of the PDF file to upload.
  /// - [marginSide]: The margin side for the PDF.
  /// 
  /// Returns:
  /// - A Future that completes with a PDFModel of the uploaded PDF.
  @override
  Future<PDFModel> uploadPDFBytes(Uint8List fileBytes, String marginSide) async {
    _log.info('Uploading PDF from bytes with margin side: $marginSide');
    final response = await apiProvider.uploadPDFBytes(fileBytes, marginSide);
    return PDFModel.fromJson(response);
  }

  /// Sends extracted text of a PDF to the server.
  /// 
  /// Parameters:
  /// - [filename]: The name of the PDF file.
  /// - [pageTexts]: A map containing the extracted text from the PDF pages.
  /// 
  /// Throws:
  /// - An Exception if the server response indicates a failure.
  @override
  Future<void> sendExtractedText(String filename, Map<String, dynamic> pageTexts) async {
    _log.info('Sending extracted text for filename: $filename');
    final response = await apiProvider.sendExtractedText(filename, pageTexts);
    if (response.statusCode != 200) {
      _log.severe('Failed to send extracted text for filename: $filename');
      throw Exception('Failed to send extracted text');
    }
  }
}
