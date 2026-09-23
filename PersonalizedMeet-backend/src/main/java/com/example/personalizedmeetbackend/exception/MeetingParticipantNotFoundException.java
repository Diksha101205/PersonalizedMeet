package com.example.personalizedmeetbackend.exception;

public class MeetingParticipantNotFoundException extends RuntimeException {

    public MeetingParticipantNotFoundException(Long id) {
        super("Meeting participant not found with id: " + id);
    }
}
