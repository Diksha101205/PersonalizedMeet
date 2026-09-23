package com.example.personalizedmeetbackend.dto;

import com.example.personalizedmeetbackend.model.ParticipantRole;

import jakarta.validation.constraints.NotNull;

public class MeetingParticipantRequest {

    @NotNull(message = "Meeting id is required")
    private Long meetingId;

    @NotNull(message = "User id is required")
    private Long userId;

    @NotNull(message = "Participant role is required")
    private ParticipantRole participantRole;

    public Long getMeetingId() {
        return meetingId;
    }

    public void setMeetingId(Long meetingId) {
        this.meetingId = meetingId;
    }

    public Long getUserId() {
        return userId;
    }

    public void setUserId(Long userId) {
        this.userId = userId;
    }

    public ParticipantRole getParticipantRole() {
        return participantRole;
    }

    public void setParticipantRole(ParticipantRole participantRole) {
        this.participantRole = participantRole;
    }
}
