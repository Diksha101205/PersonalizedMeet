package com.example.personalizedmeetbackend.exception;

public class DuplicateMeetingCodeException extends RuntimeException {

    public DuplicateMeetingCodeException(String meetingCode) {
        super("Meeting code already exists: " + meetingCode);
    }
}
