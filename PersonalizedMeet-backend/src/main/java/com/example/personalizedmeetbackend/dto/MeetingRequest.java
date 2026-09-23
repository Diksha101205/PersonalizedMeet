package com.example.personalizedmeetbackend.dto;

import com.example.personalizedmeetbackend.model.MeetingStatus;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

public class MeetingRequest {

    @NotBlank(message = "Title is required")
    @Size(max = 150, message = "Title must not be longer than 150 characters")
    private String title;

    @Size(max = 1000, message = "Description must not be longer than 1000 characters")
    private String description;

    @NotNull(message = "Creator user id is required")
    private Long createdById;

    private MeetingStatus status;

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public Long getCreatedById() {
        return createdById;
    }

    public void setCreatedById(Long createdById) {
        this.createdById = createdById;
    }

    public MeetingStatus getStatus() {
        return status;
    }

    public void setStatus(MeetingStatus status) {
        this.status = status;
    }
}
