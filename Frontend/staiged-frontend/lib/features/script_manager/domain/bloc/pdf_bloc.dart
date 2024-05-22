import 'dart:typed_data';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../data/interfaces/pdf_repository_interface.dart';
import '../models/pdf_model.dart';
import 'package:equatable/equatable.dart';
import 'package:pdfrx/pdfrx.dart';

// Events
abstract class PDFEvent extends Equatable {
  const PDFEvent();
}

class UploadPDF extends PDFEvent {
  final String filePath;
  final String marginSide;

  const UploadPDF(this.filePath, this.marginSide);

  @override
  List<Object> get props => [filePath, marginSide];
}

class UploadPDFBytes extends PDFEvent {
  final Uint8List fileBytes;
  final String marginSide;

  const UploadPDFBytes(this.fileBytes, this.marginSide);

  @override
  List<Object> get props => [fileBytes, marginSide];
}

class ExtractAndSendText extends PDFEvent {
  final String filename;
  final Map<String, dynamic> pageTexts;

  const ExtractAndSendText(this.filename, this.pageTexts);

  @override
  List<Object> get props => [filename, pageTexts];
}

// States
abstract class PDFState extends Equatable {
  const PDFState();

  @override
  List<Object> get props => [];
}

class PDFInitial extends PDFState {}

class PDFLoading extends PDFState {}

class PDFSuccess extends PDFState {
  final PDFModel pdf;

  const PDFSuccess(this.pdf);

  @override
  List<Object> get props => [pdf];
}

class PDFError extends PDFState {
  final String message;

  const PDFError(this.message);

  @override
  List<Object> get props => [message];
}

class TextExtractionInProgress extends PDFState {}

class TextExtractionSuccess extends PDFState {}

class TextExtractionError extends PDFState {
  final String message;

  const TextExtractionError(this.message);

  @override
  List<Object> get props => [message];
}

// Bloc
class PDFBloc extends Bloc<PDFEvent, PDFState> {
  final PDFRepositoryInterface pdfRepository;

  PDFBloc(this.pdfRepository) : super(PDFInitial()) {
    on<UploadPDF>((event, emit) async {
      emit(PDFLoading());
      try {
        final pdf = await pdfRepository.uploadPDF(event.filePath, event.marginSide);
        emit(PDFSuccess(pdf));
      } catch (e) {
        emit(PDFError(e.toString()));
      }
    });

    on<UploadPDFBytes>((event, emit) async {
      emit(PDFLoading());
      try {
        final pdf = await pdfRepository.uploadPDFBytes(event.fileBytes, event.marginSide);
        emit(PDFSuccess(pdf));
      } catch (e) {
        emit(PDFError(e.toString()));
      }
    });

    on<ExtractAndSendText>((event, emit) async {
      emit(TextExtractionInProgress());
      try {
        await pdfRepository.sendExtractedText(event.filename, event.pageTexts);
        // emit(TextExtractionSuccess());
      } catch (e) {
        emit(TextExtractionError(e.toString()));
      }
    });
  }
}
