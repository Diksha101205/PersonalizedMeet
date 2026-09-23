package com.example.personalizedmeetbackend.service;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.List;
import java.util.Set;
import java.util.UUID;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

import com.example.personalizedmeetbackend.dto.MeetingRecordingResponse;
import com.example.personalizedmeetbackend.exception.FileStorageException;
import com.example.personalizedmeetbackend.exception.InvalidRecordingFileException;
import com.example.personalizedmeetbackend.exception.MeetingNotFoundException;
import com.example.personalizedmeetbackend.exception.MeetingRecordingNotFoundException;
import com.example.personalizedmeetbackend.model.Meeting;
import com.example.personalizedmeetbackend.model.MeetingRecording;
import com.example.personalizedmeetbackend.model.RecordingStatus;
import com.example.personalizedmeetbackend.repository.MeetingRecordingRepository;
import com.example.personalizedmeetbackend.repository.MeetingRepository;

@Service
public class MeetingRecordingService {

    private static final Set<String> SUPPORTED_CONTENT_TYPES = Set.of(
            "audio/mpeg",
            "audio/wav",
            "audio/x-wav",
            "audio/mp4",
            "video/mp4",
            "video/webm",
            "video/x-msvideo"
    );

    private final MeetingRecordingRepository meetingRecordingRepository;
    private final MeetingRepository meetingRepository;
    private final Path storageDirectory;
    private final long maxFileSizeBytes;

    public MeetingRecordingService(
            MeetingRecordingRepository meetingRecordingRepository,
            MeetingRepository meetingRepository,
            @Value("${app.upload.meeting-recordings-dir:uploads/meeting-recordings}") String uploadDirectory,
            @Value("${app.upload.max-recording-file-size-bytes:104857600}") long maxFileSizeBytes
    ) {
        this.meetingRecordingRepository = meetingRecordingRepository;
        this.meetingRepository = meetingRepository;
        this.storageDirectory = Paths.get(uploadDirectory).toAbsolutePath().normalize();
        this.maxFileSizeBytes = maxFileSizeBytes;
        createStorageDirectory();
    }

    public MeetingRecordingResponse uploadRecording(Long meetingId, MultipartFile file) {
        Meeting meeting = meetingRepository.findById(meetingId)
                .orElseThrow(() -> new MeetingNotFoundException(meetingId));

        validateFile(file);

        String originalFileName = StringUtils.cleanPath(file.getOriginalFilename());
        String storedFileName = generateStoredFileName(originalFileName);
        Path targetLocation = storageDirectory.resolve(storedFileName).normalize();

        if (!targetLocation.startsWith(storageDirectory)) {
            throw new InvalidRecordingFileException("Invalid file path");
        }

        try {
            Files.copy(file.getInputStream(), targetLocation, StandardCopyOption.REPLACE_EXISTING);
        } catch (IOException ex) {
            throw new FileStorageException("Failed to store recording file", ex);
        }

        MeetingRecording recording = new MeetingRecording();
        recording.setMeeting(meeting);
        recording.setOriginalFileName(originalFileName);
        recording.setStoredFileName(storedFileName);
        recording.setFilePath(targetLocation.toString());
        recording.setContentType(file.getContentType());
        recording.setFileSize(file.getSize());
        recording.setUploadStatus(RecordingStatus.UPLOADED);

        MeetingRecording savedRecording = meetingRecordingRepository.save(recording);
        return mapToResponse(savedRecording);
    }

    public MeetingRecordingResponse getRecordingById(Long id) {
        MeetingRecording recording = findRecordingOrThrow(id);
        return mapToResponse(recording);
    }

    public List<MeetingRecordingResponse> getAllRecordings() {
        return meetingRecordingRepository.findAll()
                .stream()
                .map(this::mapToResponse)
                .toList();
    }

    public List<MeetingRecordingResponse> getRecordingsByMeeting(Long meetingId) {
        meetingRepository.findById(meetingId)
                .orElseThrow(() -> new MeetingNotFoundException(meetingId));

        return meetingRecordingRepository.findByMeetingId(meetingId)
                .stream()
                .map(this::mapToResponse)
                .toList();
    }

    public void deleteRecording(Long id) {
        MeetingRecording recording = findRecordingOrThrow(id);
        Path filePath = Paths.get(recording.getFilePath()).normalize();

        try {
            Files.deleteIfExists(filePath);
        } catch (IOException ex) {
            throw new FileStorageException("Failed to delete recording file", ex);
        }

        meetingRecordingRepository.delete(recording);
    }

    private void validateFile(MultipartFile file) {
        if (file == null) {
            throw new InvalidRecordingFileException("Recording file is required");
        }

        if (file.isEmpty()) {
            throw new InvalidRecordingFileException("Recording file must not be empty");
        }

        if (file.getSize() > maxFileSizeBytes) {
            throw new InvalidRecordingFileException("Recording file is too large");
        }

        String contentType = file.getContentType();
        if (contentType == null || !SUPPORTED_CONTENT_TYPES.contains(contentType)) {
            throw new InvalidRecordingFileException("Unsupported recording file type");
        }

        String originalFileName = file.getOriginalFilename();
        if (originalFileName == null || originalFileName.isBlank()) {
            throw new InvalidRecordingFileException("Original file name is required");
        }
    }

    private MeetingRecording findRecordingOrThrow(Long id) {
        return meetingRecordingRepository.findById(id)
                .orElseThrow(() -> new MeetingRecordingNotFoundException(id));
    }

    private String generateStoredFileName(String originalFileName) {
        String extension = getFileExtension(originalFileName);
        return UUID.randomUUID() + extension;
    }

    private String getFileExtension(String fileName) {
        int extensionIndex = fileName.lastIndexOf('.');
        if (extensionIndex == -1) {
            return "";
        }
        return fileName.substring(extensionIndex).toLowerCase();
    }

    private void createStorageDirectory() {
        try {
            Files.createDirectories(storageDirectory);
        } catch (IOException ex) {
            throw new FileStorageException("Failed to create recording upload directory", ex);
        }
    }

    private MeetingRecordingResponse mapToResponse(MeetingRecording recording) {
        return new MeetingRecordingResponse(
                recording.getId(),
                recording.getMeeting().getId(),
                recording.getOriginalFileName(),
                recording.getContentType(),
                recording.getFileSize(),
                recording.getUploadStatus(),
                recording.getUploadedAt()
        );
    }
}
