/// Author: Jack Beaumont
/// Date: 06/06/2024
/// Description: This file contains the PDF Bloc implementation,
/// handling the various events and states for PDF-related operations.
library;

import 'dart:typed_data';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:logger/logger.dart';
import '../../data/interfaces/pdf_repository_interface.dart';
import '../entities/pdf_model.dart';
import 'package:equatable/equatable.dart';

// Logger instance
final logger = Logger();

// Events
/// Abstract class representing all PDF events.
abstract class PDFEvent extends Equatable {
  const PDFEvent();
}

/// Event to upload a PDF file from a file path.
class UploadPDF extends PDFEvent {
  final String filePath;
  final String marginSide;

  const UploadPDF(this.filePath, this.marginSide);

  @override
  List<Object> get props => [filePath, marginSide];
}

/// Event to upload a PDF file from bytes.
class UploadPDFBytes extends PDFEvent {
  final Uint8List fileBytes;
  final String marginSide;

  const UploadPDFBytes(this.fileBytes, this.marginSide);

  @override
  List<Object> get props => [fileBytes, marginSide];
}

/// Event to extract text from a PDF and send it.
class ExtractAndSendText extends PDFEvent {
  final String filename;
  final Map<String, dynamic> pageTexts;

  const ExtractAndSendText(this.filename, this.pageTexts);

  @override
  List<Object> get props => [filename, pageTexts];
}

// States
/// Abstract class representing all PDF states.
abstract class PDFState extends Equatable {
  const PDFState();

  @override
  List<Object> get props => [];
}

/// Initial state of the PDF Bloc.
class PDFInitial extends PDFState {}

/// State when a PDF operation is in progress.
class PDFLoading extends PDFState {}

/// State when a PDF operation is successful.
class PDFSuccess extends PDFState {
  final PDFModel pdf;

  const PDFSuccess(this.pdf);

  @override
  List<Object> get props => [pdf];
}

/// State when a PDF operation fails.
class PDFError extends PDFState {
  final String message;

  const PDFError(this.message);

  @override
  List<Object> get props => [message];
}

/// State when text extraction is in progress.
class TextExtractionInProgress extends PDFState {}

/// State when text extraction is successful.
class TextExtractionSuccess extends PDFState {}

/// State when text extraction fails.
class TextExtractionError extends PDFState {
  final String message;

  const TextExtractionError(this.message);

  @override
  List<Object> get props => [message];
}

// Bloc
/// Bloc handling PDF-related events and states.
class PDFBloc extends Bloc<PDFEvent, PDFState> {
  final PDFRepositoryInterface pdfRepository;

  PDFBloc(this.pdfRepository) : super(PDFInitial()) {
    on<UploadPDF>(_onUploadPDF);
    on<UploadPDFBytes>(_onUploadPDFBytes);
    on<ExtractAndSendText>(_onExtractAndSendText);
  }

  /// Handles the [UploadPDF] event.
  /// 
  /// Parameters:
  /// - [event]: The [UploadPDF] event containing the file path and margin side.
  /// - [emit]: The function to emit new states.
  Future<void> _onUploadPDF(UploadPDF event, Emitter<PDFState> emit) async {
    emit(PDFLoading());
    try {
      final pdf = await pdfRepository.uploadPDF(event.filePath, event.marginSide);
      emit(PDFSuccess(pdf));
    } catch (e) {
      logger.e('Error uploading PDF from file path: ${e.toString()}');
      emit(PDFError(e.toString()));
    }
  }

  /// Handles the [UploadPDFBytes] event.
  /// 
  /// Parameters:
  /// - [event]: The [UploadPDFBytes] event containing the file bytes and margin side.
  /// - [emit]: The function to emit new states.
  Future<void> _onUploadPDFBytes(UploadPDFBytes event, Emitter<PDFState> emit) async {
    emit(PDFLoading());
    try {
      final pdf = await pdfRepository.uploadPDFBytes(event.fileBytes, event.marginSide);
      emit(PDFSuccess(pdf));
    } catch (e) {
      logger.e('Error uploading PDF from bytes: ${e.toString()}');
      emit(PDFError(e.toString()));
    }
  }

  /// Handles the [ExtractAndSendText] event.
  /// 
  /// Parameters:
  /// - [event]: The [ExtractAndSendText] event containing the filename and extracted texts.
  /// - [emit]: The function to emit new states.
  Future<void> _onExtractAndSendText(ExtractAndSendText event, Emitter<PDFState> emit) async {
    emit(TextExtractionInProgress());
    try {
      await pdfRepository.sendExtractedText(event.filename, event.pageTexts);
      emit(TextExtractionSuccess());
    } catch (e) {
      logger.e('Error extracting and sending text: ${e.toString()}');
      emit(TextExtractionError(e.toString()));
    }
  }
}
