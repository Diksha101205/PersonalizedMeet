package com.example.personalizedmeetbackend.dto;

import java.time.LocalDateTime;

import com.example.personalizedmeetbackend.model.RecordingStatus;

public class MeetingRecordingResponse {

    private Long recordingId;
    private Long meetingId;
    private String originalFileName;
    private String contentType;
    private Long fileSize;
    private RecordingStatus uploadStatus;
    private LocalDateTime uploadedAt;

    public MeetingRecordingResponse(
            Long recordingId,
            Long meetingId,
            String originalFileName,
            String contentType,
            Long fileSize,
            RecordingStatus uploadStatus,
            LocalDateTime uploadedAt
    ) {
        this.recordingId = recordingId;
        this.meetingId = meetingId;
        this.originalFileName = originalFileName;
        this.contentType = contentType;
        this.fileSize = fileSize;
        this.uploadStatus = uploadStatus;
        this.uploadedAt = uploadedAt;
    }

    public Long getRecordingId() {
        return recordingId;
    }

    public Long getMeetingId() {
        return meetingId;
    }

    public String getOriginalFileName() {
        return originalFileName;
    }

    public String getContentType() {
        return contentType;
    }

    public Long getFileSize() {
        return fileSize;
    }

    public RecordingStatus getUploadStatus() {
        return uploadStatus;
    }

    public LocalDateTime getUploadedAt() {
        return uploadedAt;
    }
}
