package com.example.personalizedmeetbackend.dto;

import com.example.personalizedmeetbackend.model.ParticipantRole;

import jakarta.validation.constraints.NotNull;

public class MeetingParticipantRoleUpdateRequest {

    @NotNull(message = "Participant role is required")
    private ParticipantRole participantRole;

    public ParticipantRole getParticipantRole() {
        return participantRole;
    }

    public void setParticipantRole(ParticipantRole participantRole) {
        this.participantRole = participantRole;
    }
}
