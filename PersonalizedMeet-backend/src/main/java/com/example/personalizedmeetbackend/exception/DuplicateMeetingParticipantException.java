package com.example.personalizedmeetbackend.exception;

public class DuplicateMeetingParticipantException extends RuntimeException {

    public DuplicateMeetingParticipantException(Long meetingId, Long userId) {
        super("User with id " + userId + " is already a participant of meeting with id " + meetingId);
    }
}
