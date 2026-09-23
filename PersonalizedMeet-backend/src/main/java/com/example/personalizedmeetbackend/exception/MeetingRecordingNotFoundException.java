package com.example.personalizedmeetbackend.exception;

public class MeetingRecordingNotFoundException extends RuntimeException {

    public MeetingRecordingNotFoundException(Long id) {
        super("Meeting recording not found with id: " + id);
    }
}
