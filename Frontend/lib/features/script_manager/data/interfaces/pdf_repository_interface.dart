/// Author: Jack Beaumont
/// Date: 06/06/2024
///
/// This file defines the interface for PDF repository operations such as
/// uploading, fetching PDFs, and sending extracted text.
library;

import 'dart:typed_data';
import '../../domain/entities/pdf_model.dart';

/// PDFRepositoryInterface provides an abstract interface for PDF repository operations.
abstract class PDFRepositoryInterface {
  
  /// Uploads a PDF file from the specified file path with the given margin side.
  ///
  /// [filePath] is the path to the PDF file to upload.
  /// [marginSide] specifies the margin side for the PDF.
  /// Returns a [Future] that completes with a [PDFModel] representing the uploaded PDF.
  Future<PDFModel> uploadPDF(String filePath, String marginSide);
  
  /// Fetches a PDF with the given filename.
  ///
  /// [filename] is the name of the PDF file to fetch.
  /// Returns a [Future] that completes with a [PDFModel] representing the fetched PDF.
  Future<PDFModel> fetchPDF(String filename);
  
  /// Uploads PDF data from a byte array with the given margin side.
  ///
  /// [fileBytes] is a [Uint8List] containing the PDF data to upload.
  /// [marginSide] specifies the margin side for the PDF.
  /// Returns a [Future] that completes with a [PDFModel] representing the uploaded PDF.
  Future<PDFModel> uploadPDFBytes(Uint8List fileBytes, String marginSide);
  
  /// Sends extracted text from a PDF to a specified location.
  ///
  /// [filename] is the name of the PDF file from which text was extracted.
  /// [pageTexts] is a [Map] containing page numbers and their corresponding extracted texts.
  /// Returns a [Future] that completes when the extracted text has been sent.
  Future<void> sendExtractedText(String filename, Map<String, dynamic> pageTexts);
}
