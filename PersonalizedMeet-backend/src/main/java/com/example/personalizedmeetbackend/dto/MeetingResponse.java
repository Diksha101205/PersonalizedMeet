package com.example.personalizedmeetbackend.dto;

import java.time.LocalDateTime;

import com.example.personalizedmeetbackend.model.MeetingStatus;

public class MeetingResponse {

    private Long id;
    private String title;
    private String description;
    private String meetingCode;
    private UserResponse createdBy;
    private LocalDateTime createdAt;
    private MeetingStatus status;

    public MeetingResponse(
            Long id,
            String title,
            String description,
            String meetingCode,
            UserResponse createdBy,
            LocalDateTime createdAt,
            MeetingStatus status
    ) {
        this.id = id;
        this.title = title;
        this.description = description;
        this.meetingCode = meetingCode;
        this.createdBy = createdBy;
        this.createdAt = createdAt;
        this.status = status;
    }

    public Long getId() {
        return id;
    }

    public String getTitle() {
        return title;
    }

    public String getDescription() {
        return description;
    }

    public String getMeetingCode() {
        return meetingCode;
    }

    public UserResponse getCreatedBy() {
        return createdBy;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public MeetingStatus getStatus() {
        return status;
    }
}
