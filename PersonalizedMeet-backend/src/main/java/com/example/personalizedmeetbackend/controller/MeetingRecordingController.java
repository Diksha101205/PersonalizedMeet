package com.example.personalizedmeetbackend.controller;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

import com.example.personalizedmeetbackend.dto.MeetingRecordingResponse;
import com.example.personalizedmeetbackend.service.MeetingRecordingService;

@RestController
@RequestMapping("/api/meeting-recordings")
public class MeetingRecordingController {

    private final MeetingRecordingService meetingRecordingService;

    public MeetingRecordingController(MeetingRecordingService meetingRecordingService) {
        this.meetingRecordingService = meetingRecordingService;
    }

    @PostMapping("/upload/{meetingId}")
    public ResponseEntity<MeetingRecordingResponse> uploadRecording(
            @PathVariable Long meetingId,
            @RequestParam("file") MultipartFile file
    ) {
        MeetingRecordingResponse response = meetingRecordingService.uploadRecording(meetingId, file);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @GetMapping("/{id}")
    public ResponseEntity<MeetingRecordingResponse> getRecordingById(@PathVariable Long id) {
        return ResponseEntity.ok(meetingRecordingService.getRecordingById(id));
    }

    @GetMapping
    public ResponseEntity<List<MeetingRecordingResponse>> getAllRecordings() {
        return ResponseEntity.ok(meetingRecordingService.getAllRecordings());
    }

    @GetMapping("/meeting/{meetingId}")
    public ResponseEntity<List<MeetingRecordingResponse>> getRecordingsByMeeting(@PathVariable Long meetingId) {
        return ResponseEntity.ok(meetingRecordingService.getRecordingsByMeeting(meetingId));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteRecording(@PathVariable Long id) {
        meetingRecordingService.deleteRecording(id);
        return ResponseEntity.noContent().build();
    }
}
