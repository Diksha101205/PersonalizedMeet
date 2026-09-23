package com.example.personalizedmeetbackend.dto;

import java.time.LocalDateTime;

import com.example.personalizedmeetbackend.model.ParticipantRole;

public class MeetingParticipantResponse {

    private Long id;
    private Long meetingId;
    private UserResponse user;
    private ParticipantRole participantRole;
    private LocalDateTime joinedAt;

    public MeetingParticipantResponse(
            Long id,
            Long meetingId,
            UserResponse user,
            ParticipantRole participantRole,
            LocalDateTime joinedAt
    ) {
        this.id = id;
        this.meetingId = meetingId;
        this.user = user;
        this.participantRole = participantRole;
        this.joinedAt = joinedAt;
    }

    public Long getId() {
        return id;
    }

    public Long getMeetingId() {
        return meetingId;
    }

    public UserResponse getUser() {
        return user;
    }

    public ParticipantRole getParticipantRole() {
        return participantRole;
    }

    public LocalDateTime getJoinedAt() {
        return joinedAt;
    }
}
